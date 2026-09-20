"""Verify the software-team package.

Checks three things that silently break the package if violated:

1. Every agent, skill and prompt has frontmatter that actually parses as YAML.
   Copilot fails to load a primitive whose `description:` contains an unquoted
   ``: `` sequence, and the failure is silent.
2. The rubber-duck rubric appears ONLY in duck-facing files. A single paste of
   the scoring formula into a lead agent defeats the review design, because a
   lead that can see the target optimises for the target.
3. Structural invariants: expected files exist, names match filenames, and no
   filename collides with the legacy packages.

Run from the repository root::

    python packages/software-team/verify.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE.parent.parent
COPILOT = PACKAGE / "github-copilot"
DOCS = PACKAGE / "docs"

# Files permitted to carry the review rubric.
DUCK_ONLY = {
    DOCS / "RUBBER-DUCK-PROTOCOL.md",
    COPILOT / "skills" / "st-rubber-duck" / "SKILL.md",
}

# Terms that reveal the review standard. A lead that sees these can aim at the
# score instead of the work, which is exactly what the asymmetry prevents.
RUBRIC_TERMS = [
    re.compile(r"\bBlocker\b"),
    re.compile(r"\bMajor\b"),
    re.compile(r"\bMinor\b"),
    re.compile(r"\bNit\b"),
    re.compile(r"\brubric\b", re.IGNORECASE),
    re.compile(r"score\s*="),
    re.compile(r"[≥>]=?\s*90\b"),
    re.compile(r"\b90\s*%"),
]

EXPECTED_AGENTS = [
    "st-project-lead", "st-research-lead", "st-research-duck",
    "st-architect", "st-architect-duck",
    "st-pm-lead", "st-pm-duck", "st-feature-analyst",
    "st-dev-lead", "st-dev-duck", "st-implementer",
    "st-test-engineer", "st-code-reviewer",
    "st-ux-designer", "st-ux-duck",
]
EXPECTED_SKILLS = [
    "st-okf-memory", "st-handoff", "st-board-ops", "st-cadence", "st-rubber-duck",
]
EXPECTED_PROMPTS = ["st-bootstrap", "st-status", "st-sync", "st-lint"]

DUCK_AGENTS = {a for a in EXPECTED_AGENTS if a.endswith("-duck")}

failures: list[str] = []
passes: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def ok(msg: str) -> None:
    passes.append(msg)


def split_frontmatter(path: Path) -> dict[str, str] | None:
    """Return the frontmatter mapping, or None when it is absent or malformed."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    block = text[4:end]
    try:
        import yaml  # type: ignore[import-untyped]

        loaded = yaml.safe_load(block)
    except ImportError:
        # Fall back to a shape check that catches the real failure mode: an
        # unquoted value containing ": ", which YAML reads as a nested mapping.
        loaded = {}
        for line in block.splitlines():
            if not line or line.startswith((" ", "\t", "#")):
                continue
            key, _, value = line.partition(":")
            value = value.strip()
            if value and not value[0] in "'\"" and ": " in value:
                return None
            loaded[key.strip()] = value
    except Exception:
        return None
    return loaded if isinstance(loaded, dict) else None


def check_frontmatter() -> None:
    targets = (
        sorted(COPILOT.glob("agents/*.agent.md"))
        + sorted(COPILOT.glob("skills/*/SKILL.md"))
        + sorted(COPILOT.glob("prompts/*.prompt.md"))
    )
    if not targets:
        fail("no primitives found under github-copilot/")
        return
    for path in targets:
        rel = path.relative_to(REPO_ROOT)
        fm = split_frontmatter(path)
        if fm is None:
            fail(f"{rel}: frontmatter missing or does not parse as YAML")
            continue
        if "description" not in fm:
            fail(f"{rel}: frontmatter has no 'description'")
        elif not str(fm["description"]).strip():
            fail(f"{rel}: 'description' is empty")
        if path.name.endswith(".agent.md") or path.name == "SKILL.md":
            if "name" not in fm:
                fail(f"{rel}: frontmatter has no 'name'")
    ok(f"frontmatter parses for {len(targets)} primitives")


def check_rubric_asymmetry() -> None:
    """The rubric must appear only in duck-facing files."""
    scanned = 0
    leaked = 0
    for path in sorted(PACKAGE.rglob("*.md")):
        if path in DUCK_ONLY:
            continue
        if path.name == "verify.py":
            continue
        scanned += 1
        rel = path.relative_to(REPO_ROOT)
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern in RUBRIC_TERMS:
                if pattern.search(line):
                    leaked += 1
                    fail(
                        f"RUBRIC LEAK {rel}:{line_no}: "
                        f"matched {pattern.pattern!r} -> {line.strip()[:90]}"
                    )
    if leaked == 0:
        ok(f"rubric asymmetry holds across {scanned} non-duck files")


def check_duck_files_defer() -> None:
    """Duck agents must defer to the skill, not restate the rubric."""
    for name in sorted(DUCK_AGENTS):
        path = COPILOT / "agents" / f"{name}.agent.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "st-rubber-duck" not in text:
            fail(f"{path.relative_to(REPO_ROOT)}: does not reference the st-rubber-duck skill")
    ok(f"{len(DUCK_AGENTS)} duck agents defer to the st-rubber-duck skill")


def check_expected_files() -> None:
    for name in EXPECTED_AGENTS:
        path = COPILOT / "agents" / f"{name}.agent.md"
        if not path.exists():
            fail(f"missing agent: {path.relative_to(REPO_ROOT)}")
    for name in EXPECTED_SKILLS:
        path = COPILOT / "skills" / name / "SKILL.md"
        if not path.exists():
            fail(f"missing skill: {path.relative_to(REPO_ROOT)}")
    for name in EXPECTED_PROMPTS:
        path = COPILOT / "prompts" / f"{name}.prompt.md"
        if not path.exists():
            fail(f"missing prompt: {path.relative_to(REPO_ROOT)}")
    ok(
        f"all expected files present "
        f"({len(EXPECTED_AGENTS)} agents, {len(EXPECTED_SKILLS)} skills, "
        f"{len(EXPECTED_PROMPTS)} prompts)"
    )


def check_no_collisions() -> None:
    """Legacy packages stay installed, so no filename may collide."""
    ours = {p.name for p in COPILOT.glob("agents/*.agent.md")}
    ours |= {p.name for p in COPILOT.glob("prompts/*.prompt.md")}
    our_skills = {p.name for p in COPILOT.glob("skills/*") if p.is_dir()}

    others: set[str] = set()
    other_skills: set[str] = set()
    for pkg in (REPO_ROOT / "packages").iterdir():
        if not pkg.is_dir() or pkg.name == "software-team":
            continue
        for sub in ("github-copilot", "claude-code"):
            root = pkg / sub
            if not root.is_dir():
                continue
            others |= {p.name for p in root.glob("agents/*.md")}
            others |= {p.name for p in root.glob("commands/*.md")}
            others |= {p.name for p in root.glob("prompts/*.prompt.md")}
            other_skills |= {p.name for p in root.glob("skills/*") if p.is_dir()}

    clash = ours & others
    skill_clash = our_skills & other_skills
    if clash:
        fail(f"filename collision with legacy packages: {sorted(clash)}")
    if skill_clash:
        fail(f"skill directory collision with legacy packages: {sorted(skill_clash)}")
    if not clash and not skill_clash:
        ok(f"no collisions: {len(ours)} files and {len(our_skills)} skills are uniquely named")


def check_concurrency_rule() -> None:
    """The concurrency limit must be stated consistently wherever it appears."""
    pattern = re.compile(r"at most 2|more than 2 is not allowed", re.IGNORECASE)
    found = [
        p.relative_to(REPO_ROOT)
        for p in PACKAGE.rglob("*.md")
        if pattern.search(p.read_text(encoding="utf-8"))
    ]
    if len(found) < 3:
        fail(f"concurrency rule stated in only {len(found)} files; expected it in the charter, PARALLELISM and the leads")
    else:
        ok(f"concurrency rule stated in {len(found)} files")


def main() -> int:
    check_expected_files()
    check_frontmatter()
    check_rubric_asymmetry()
    check_duck_files_defer()
    check_no_collisions()
    check_concurrency_rule()

    for line in passes:
        print(f"  PASS  {line}")
    for line in failures:
        print(f"  FAIL  {line}")

    print()
    if failures:
        print(f"FAILED: {len(failures)} problem(s)")
        return 1
    print(f"OK: {len(passes)} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
