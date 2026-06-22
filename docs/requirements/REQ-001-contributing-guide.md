---
id: REQ-001
title: Top-level CONTRIBUTING.md for new contributors
status: specced          # draft | in-review | approved | in-spec | specced | in-delivery | delivered | parked
priority: P2             # P0 | P1 | P2 | P3
version: 3
created: 2026-06-21
updated: 2026-06-21
approved_at: 2026-06-21   # set when the requirement PR merges (or express signoff)
approved_by: satishc-dev (e2e-test operator)   # stakeholder identity
requirement_issue: https://github.com/satishc-dev/maruti/issues/7       # GitHub Requirement issue URL
links:
  requirement_pr: https://github.com/satishc-dev/maruti/pull/6        # the PR that introduced/changed this doc
  project_item: https://github.com/users/satishc-dev/projects/5          # GitHub Project item URL
  initiative:            # [[wiki/initiatives/...]] in project memory
  specs:                 # spec PR(s) / docs/specs paths (filled by pm-team)
    - https://github.com/satishc-dev/maruti/pull/8   # spec PR (base pl-e2e-test)
    - docs/specs/contributing-guide/contributing-guide.md
  child_issues:          # Feature/Story sub-issues of #7 (filled after spec)
    - https://github.com/satishc-dev/maruti/issues/9    # Feature
    - https://github.com/satishc-dev/maruti/issues/11   # Story A
    - https://github.com/satishc-dev/maruti/issues/10   # Story B
  prs: []                # dev-team PRs
---

## Problem / Context

New contributors to **maruti** have no single entry point that tells them how to
work in the repo. The relevant knowledge is real and accurate but scattered
across `CLAUDE.md` (oriented at coding agents), `docs/Constitution.md` (binding
principles and gates), `docs/development.md` (the practical companion),
`packages/README.md` (agent-package authoring), and `scripts/README.md` (the
symlink mirror). A first-time human contributor must reverse-engineer the
workflow from these files, and there is currently **no `CONTRIBUTING.md` at the
repo root** — the conventional, GitHub-surfaced place a contributor looks first.

This raises the barrier to a correct first contribution and increases the chance
of avoidable CI failures (wrong `uv sync` invocation, missing docstrings, pylint
warnings, sub-95% coverage, or an un-synced agent-package symlink mirror).

## Desired outcome (goal)

A single top-level `CONTRIBUTING.md` that a new contributor can read once and
then confidently make a correct, mergeable contribution to either kind of work
the repo hosts:

- an **MCP tool** under `mcp-tools/<name>/`, or
- an **agent package** under `packages/<name>/`.

It should orient them on the repo's shape, the Python 3.14 / `uv` workspace
model, the exact quality gates CI enforces, how to run tests, and the PR
conventions — and it should point to (not duplicate) the deeper governance docs
so the two don't drift.

## Scope — in

The `CONTRIBUTING.md` document must cover, accurately to how the repo works today:

1. **Repository layout** — that maruti is a `uv` workspace, and the two kinds of
   contributable units:
   - `mcp-tools/<name>/` — self-contained MCP tool projects (own
     `pyproject.toml`, `src/<pkg>/`, `tests/`, `specs/`, `README.md`), declared
     in the root `pyproject.toml` under `[tool.uv.workspace].members`.
   - `packages/<name>/` — platform-bifurcated agent packages (`claude-code/`
     and/or `github-copilot/`) for Claude Code and GitHub Copilot CLI
     customizations.
2. **Python 3.14 standard** — `requires-python = ">=3.14"` on every project;
   `uv python install 3.14` / pinned via `.python-version`.
3. **Tool isolation** — no `mcp-tools/<a>` may import from `mcp-tools/<b>`; each
   tool is independently releasable (Constitution §1).
4. **How to add a new MCP tool** — the supported path
   `python scripts/new_mcp_tool.py <name> --description "..."` (copies
   `templates/mcp-tool/`, substitutes placeholders, renames `src/__module__/`,
   registers the member), the manual fallback, then
   `uv sync --dev --all-packages`, and the `uv run <tool>` + `uvx` distribution
   contract with a README `uvx` snippet.
5. **How to add/modify an agent package** — author under
   `packages/<name>/<platform>/...` (never edit the `.claude/` or `.github/`
   mirrors), then run `python scripts/link_packages.py sync` and commit the
   resulting symlinks together; CI runs `link_packages.py check`. Include the
   Windows symlink prerequisites (Developer Mode + `core.symlinks=true`) and the
   `repair` command.
6. **Quality gates** (CI-enforced), with the exact commands:
   - Docstring lint: `uv run ruff check --select D mcp-tools/*/src` (Google
     pydocstyle convention; tests excluded by config).
   - Pylint zero E/W/F: `uv run pylint mcp-tools/*/src` (root `.pylintrc`
     disables C and R; must exit 0).
   - Per-tool coverage ≥ 95%: enforced via each tool's
     `--cov-fail-under=95`; `cd mcp-tools/<tool> && uv run pytest --cov`.
   - Agent-package mirror check: `python scripts/link_packages.py check`.
7. **Running tests with uv** — `uv sync --dev --all-packages` first (and *why*
   `--all-packages` is required at the root); whole-workspace `uv run pytest`;
   single tool `uv run pytest mcp-tools/<tool> -v`; single node form; and the
   fast per-tool loop `cd mcp-tools/<tool> && uv sync --dev && uv run pytest`.
8. **PR conventions** — keep PRs small and scoped to a single tool or package;
   start from a failing test; all CI gates green (the gates above plus the
   mirror check); reference `docs/Constitution.md` Definition of Done.
9. **Cross-references** — link to `docs/development.md`, `docs/Constitution.md`,
   `packages/README.md`, and `scripts/README.md` as the authoritative deep-dive
   sources, positioning `CONTRIBUTING.md` as the concise front door.

## Scope — out (non-goals)

- Rewriting or relocating `docs/development.md`, `docs/Constitution.md`,
  `packages/README.md`, or `scripts/README.md` — `CONTRIBUTING.md` summarizes and
  links; it is not a merge of them.
- A formal commit-message convention (e.g. Conventional Commits), a PR template
  file (`.github/PULL_REQUEST_TEMPLATE.md`), a CODE_OF_CONDUCT, or CLA — not
  requested; may be a later, separate requirement.
- Changing any actual workflow, gate threshold, tooling, or CI configuration.
  This requirement only documents the existing reality.
- Documentation of the non-Python `mcp-tools/browser-pilot/` (TypeScript/Node +
  vitest) tool's build/test workflow in depth (see Open questions).
- Per-tool `README.md` content or the spec template workflow beyond a pointer.

## Acceptance / success criteria

A reviewer can verify the delivered `CONTRIBUTING.md` against these testable
criteria:

1. A file named `CONTRIBUTING.md` exists at the repository root.
2. It states maruti is a `uv` workspace and Python **3.14** is the standard, and
   explains the two contributable unit types (`mcp-tools/<name>/` tools and
   `packages/<name>/` agent packages) with their distinguishing layout.
3. It documents adding a new MCP tool via
   `python scripts/new_mcp_tool.py <name> --description "..."` followed by
   `uv sync --dev --all-packages`, names the manual fallback, and states the
   `uv run <tool>` + `uvx` distribution contract.
4. It documents the agent-package workflow: edit source under
   `packages/<name>/`, never the `.claude/`/`.github/` mirrors, then
   `python scripts/link_packages.py sync` and commit the symlinks; and notes the
   Windows symlink prerequisites.
5. It lists all four CI-enforced gates with the **exact** commands as they appear
   in `.github/workflows/ci.yml` and `docs/development.md`:
   `uv run ruff check --select D mcp-tools/*/src`,
   `uv run pylint mcp-tools/*/src`, the per-tool `--cov-fail-under=95` coverage
   gate, and `python scripts/link_packages.py check`.
6. It explains running tests with `uv`, including that the root sync MUST use
   `--all-packages` and *why* (omitting it prunes per-tool deps), and shows the
   whole-workspace, single-tool, and single-node test invocations.
7. It states the PR conventions: small, single tool/package-scoped PRs with all
   CI gates green, and links to the Constitution's Definition of Done.
8. It cross-links `docs/development.md`, `docs/Constitution.md`,
   `packages/README.md`, and `scripts/README.md` rather than duplicating them.
9. Every command, path, and gate threshold in the document is **accurate** to the
   current repo (verifiable against `pyproject.toml`, `.pylintrc`,
   `.github/workflows/ci.yml`, `docs/development.md`, and `scripts/README.md`) —
   no invented commands or thresholds.

## Constraints & assumptions

- **Constraint:** the document must match the repo as it is today; it changes no
  workflow, threshold, or config. Where the Constitution and any other doc
  disagree, the Constitution wins.
- **Constraint:** `CONTRIBUTING.md` is documentation; it has no automated tests
  of its own, so acceptance is by human/reviewer verification against the
  criteria above and the source-of-truth files.
- **Assumption:** the audience includes both human contributors and coding agents,
  but the primary reader is a new **human** contributor (agents already have
  `CLAUDE.md`).
- **Assumption:** "PR conventions" for this repo means the Constitution's
  guidance — keep PRs small and tool/package-scoped, start from a failing test,
  and land only with all CI gates green — since there is no separate
  commit-message standard or PR template in the repo today.
- **Assumption:** `CONTRIBUTING.md` should **reference** the existing deep-dive
  docs rather than copy them, to avoid documentation drift (the four source docs
  remain canonical).

## Open questions

> These are recorded as non-blocking; a reasonable default assumption has been
> made for each so the requirement still meets the Definition of Ready. They can
> be confirmed at approval or during spec.

- **Polyglot reality vs. Python-only framing.** The repo contains a non-Python
  MCP tool, `mcp-tools/browser-pilot/` (TypeScript/Node, `package.json`, vitest),
  which is **not** a `uv` workspace member and is not covered by the Python gates.
  *Default assumption:* `CONTRIBUTING.md` documents the Python/`uv` standard path
  in full and adds a brief note that a Node-based tool exists as an exception with
  its own tooling, rather than fully documenting the Node workflow. Confirm whether
  deeper Node guidance is wanted.
- **Depth vs. front-door.** Much of this content already lives in
  `docs/development.md`. *Default assumption:* `CONTRIBUTING.md` is a concise
  front door that links out, accepting some intentional overlap on the
  most-used commands. Confirm the stakeholder prefers "concise + links" over a
  single exhaustive document.

## Change log
- [2026-06-21] v1 — created (draft), then advanced to in-review after Definition
  of Ready was satisfied during intake.
- [2026-06-21] v2 — approval gate passed. Requirement PR opened and merged into
  `pl-e2e-test`; status advanced in-review → approved; `approved_by`
  satishc-dev (e2e-test operator), `approved_at` 2026-06-21. Requirement issue
  created and board item moved to Ready for Spec.
- [2026-06-21] v3 — guided handoff to PM-Team. Spec PR
  [#8](https://github.com/satishc-dev/maruti/pull/8) (base `pl-e2e-test`) with
  spec `docs/specs/contributing-guide/contributing-guide.md`. Seeded Feature
  [#9](https://github.com/satishc-dev/maruti/issues/9) and Stories
  [#11](https://github.com/satishc-dev/maruti/issues/11) /
  [#10](https://github.com/satishc-dev/maruti/issues/10), all linked as
  sub-issues of Requirement #7. Status approved → specced; board item In Spec →
  Ready for Dev. Dev-Team not yet engaged.
