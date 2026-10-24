"""Portable memory skill policies and their lazy reference contracts."""

from pathlib import Path
import re
import shlex
import unittest


PACKAGE = Path(__file__).resolve().parents[2]
NAMES = (
    "memory-bootstrap",
    "memory-recall",
    "memory-capture",
    "memory-checkpoint",
    "memory-maintain",
    "memory-promote",
)


class SkillContractTests(unittest.TestCase):
    """Keep portable entry points small and safety rules discoverable."""

    def skill(self, name):
        return (PACKAGE / "skills" / name / "SKILL.md").read_text(encoding="utf-8")

    def reference(self, name):
        return (PACKAGE / "references" / name).read_text(encoding="utf-8")

    def test_exactly_six_canonical_skill_entry_points(self):
        actual = {path.parent.name for path in (PACKAGE / "skills").glob("*/SKILL.md")}
        self.assertEqual(actual, set(NAMES))

    def test_small_single_quoted_frontmatter_and_lazy_support_resolution(self):
        for name in NAMES:
            with self.subTest(skill=name):
                text = self.skill(name)
                frontmatter, body = text.removeprefix("---\n").split("\n---\n", 1)
                self.assertIn(f"name: {name}", frontmatter.splitlines())
                description = next(
                    line for line in frontmatter.splitlines()
                    if line.startswith("description:")
                )
                self.assertRegex(description, r"^description: '(?:[^']|'')*'$")
                self.assertLess(len(description), 280)
                self.assertLess(len(body), 6500)
                self.assertIn("real loaded", body)
                self.assertIn("memory/runtime/memory.py", body)
                self.assertIn("runtime/memory.py", body)
                self.assertIn("ambiguous", body)
                for reference in re.findall(r"<support-root>/references/([\w-]+\.md)", body):
                    self.assertTrue((PACKAGE / "references" / reference).is_file())
                self.assertIn("operating-policy.md", body)
                self.assertIn("runtime-guide.md", body)

    def test_relative_reference_links_resolve_inside_package(self):
        paths = list((PACKAGE / "skills").glob("*/SKILL.md"))
        paths += list((PACKAGE / "references").glob("*.md"))
        self.assertTrue(paths)
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                with self.subTest(path=path.name, target=target):
                    resolved = (path.parent / target.split("#")[0]).resolve()
                    self.assertTrue(resolved.is_relative_to(PACKAGE.resolve()))
                    self.assertTrue(resolved.is_file())

    def test_all_entry_points_use_helper_and_honor_ownership(self):
        for name in NAMES:
            with self.subTest(skill=name):
                text = self.skill(name)
                self.assertIn("helper", text)
                self.assertIn("owner", text)
                self.assertNotIn("pip install", text)
                self.assertNotIn("uvx ", text)

    def test_runtime_examples_match_v1_direct_python_contract(self):
        text = self.reference("runtime-guide.md")
        commands = re.findall(
            r'^"<python>" "<support-root>/runtime/memory.py" (.+)$', text, re.M
        )
        self.assertGreaterEqual(len(commands), 7)
        expected_flags = {
            "doctor": set(),
            "bootstrap": set(),
            "discover": {"--query"},
            "read": {"--path"},
            "write": {"--path", "--input", "--expected"},
            "catalog": {"--topic"},
            "migration-preview": set(),
        }
        seen = set()
        shared_mutations = set()
        session_verbs = set()
        for command in commands:
            with self.subTest(command=command):
                arguments = shlex.split(command)
                self.assertEqual(arguments[:2], ["--root", "<workspace>"])
                arguments = arguments[2:]
                shared = arguments[:2] == ["--role", "shared"]
                if shared:
                    arguments = arguments[2:]
                verb = arguments[0]
                self.assertIn(verb, expected_flags)
                arguments = arguments[1:]
                flags = {}
                while arguments:
                    flag = arguments.pop(0)
                    self.assertTrue(flag.startswith("--"))
                    self.assertNotIn(flag, flags)
                    flags[flag] = True if flag == "--allow-shared" else arguments.pop(0)
                required = expected_flags[verb].copy()
                if str(flags.get("--path", "")).startswith("sessions/"):
                    session_verbs.add(verb)
                    if verb == "write":
                        required.add("--session")
                        self.assertEqual(flags["--session"], "<session-id>")
                if shared and verb in {"bootstrap", "write", "catalog"}:
                    required.add("--allow-shared")
                    shared_mutations.add(verb)
                self.assertEqual(set(flags), required)
                seen.add(verb)
        self.assertEqual(seen, set(expected_flags))
        self.assertEqual(shared_mutations, {"bootstrap", "write", "catalog"})
        self.assertEqual(session_verbs, {"read", "write"})
        for token in ("3.10", "--expected", "--input", "--allow-shared",
                      "sha256", "missing", "exit", "ok", "16000"):
            self.assertIn(token, text)

    def test_support_resolution_policy_is_identical_across_entry_points(self):
        policies = []
        for name in NAMES:
            body = self.skill(name)
            policies.append(
                body.split("## Locate support lazily\n\n", 1)[1].split("\n\nRead ", 1)[0]
            )
        self.assertEqual(len(set(policies)), 1)
        self.assertIn("following symlinks", policies[0])
        self.assertIn("If both exist, or neither exists, stop", policies[0])

    def test_runtime_failure_policy_has_no_unsafe_mutation_fallback(self):
        text = self.reference("runtime-guide.md")
        for token in ("no consumer pip/uv downloads", "exit 2", "Check both",
                      "A conflict requires rereading", "Unknown/newer", "bypass", "Read back"):
            self.assertIn(token, text)
        self.assertIn("not a\nfallback", self.reference("operating-policy.md"))

    def test_recall_budget_includes_catalog_and_search(self):
        text = self.reference("recall-guide.md").lower()
        for token in ("8", "16000", "catalog", "search", "omitted", "contradict",
                      "applicability", "evidence", "freshness", "repetition"):
            self.assertIn(token, text)
        self.assertIn("stable", text)
        self.assertIn("not proof", text)

    def test_record_policy_preserves_okf_and_honest_provenance(self):
        text = self.reference("record-guide.md")
        for token in ('okf_version: "0.2"', "no frontmatter", "type",
                      "maruti.memory", "schema_version", "unknown keys",
                      "generated.by", "verified", "sources[].id",
                      "UTC offset", "draft", "stable", "deprecated", "lifecycle"):
            self.assertIn(token, text)

    def test_capture_is_enabled_local_and_resume_checks_applicability(self):
        capture = self.skill("memory-capture")
        checkpoint = self.skill("memory-checkpoint")
        self.assertIn("enabled", capture)
        self.assertIn("useful boundaries", capture)
        self.assertIn("not every tool", capture)
        for token in ("branch", "files", "resume", "not knowledge"):
            self.assertIn(token, checkpoint)

    def test_maintenance_and_promotion_preserve_evidence_and_authority(self):
        maintenance = self.reference("maintenance-guide.md").lower()
        sharing = self.reference("sharing-guide.md").lower()
        for token in ("contradictions", "supersession", "no hard-delete", "bounded"):
            self.assertIn(token, maintenance)
        for token in ("explicit authorization", "private", "inaccessible",
                      "stage", "commit", "push", "proposal", "owner"):
            self.assertIn(token, sharing)

    def test_bootstrap_does_not_claim_or_migrate_existing_memory(self):
        text = self.skill("memory-bootstrap")
        for token in ("adopt", "ambiguous", "overwrite", ".project-memory/",
                      "global", "pointer", "approved"):
            self.assertIn(token, text)

    def test_nongit_does_not_claim_active_ignore_protection(self):
        for text in (
            self.skill("memory-bootstrap"),
            self.skill("memory-capture"),
            self.reference("operating-policy.md"),
        ):
            with self.subTest(text=text[:80]):
                self.assertIn("nonGit", text)
                self.assertIn("no active ignore verification", text)
                self.assertIn("git init", text)
                self.assertIn("bootstrap", text)
        for text in (
            self.skill("memory-bootstrap"),
            self.reference("operating-policy.md"),
        ):
            self.assertIn("no `.gitignore`", text)
            self.assertIn("git: false", text)
            self.assertIn("or staging", text)


if __name__ == "__main__":
    unittest.main()
