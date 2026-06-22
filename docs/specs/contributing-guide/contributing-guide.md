---
spec: contributing-guide
initiative: Top-level CONTRIBUTING.md for new contributors
requirement: REQ-001
requirement_issue: https://github.com/satishc-dev/maruti/issues/7
status: in-review
platform: gh
base_branch: pl-e2e-test
author: pm-team
created: 2026-06-21
---

# Feature Spec — Top-level `CONTRIBUTING.md` front-door guide

## 1. Summary

Author a single top-level **`CONTRIBUTING.md`** that serves as the concise front door for new
contributors to **maruti**. Today the working knowledge of the repo is accurate but scattered
across `CLAUDE.md`, `docs/Constitution.md`, `docs/development.md`, `packages/README.md`, and
`scripts/README.md`, and there is no `CONTRIBUTING.md` at the repo root — the conventional,
GitHub-surfaced place a contributor looks first. This feature delivers that entry point: a
contributor reads it once and can then make a correct, mergeable contribution to either an MCP
tool (`mcp-tools/<name>/`) or an agent package (`packages/<name>/`).

The document **references** the deep-dive docs rather than duplicating them, so the canonical
sources stay authoritative and the two do not drift.

## 2. Problem & goal

- **Problem:** No single entry point. First-time contributors must reverse-engineer the workflow
  from five files, raising the barrier to a correct first contribution and risking avoidable CI
  failures (wrong `uv sync` invocation, missing docstrings, pylint warnings, sub-95% coverage, or
  an un-synced agent-package symlink mirror).
- **Goal:** A concise `CONTRIBUTING.md` that orients the reader on repo shape, the Python 3.14 /
  `uv` workspace model, the exact CI-enforced quality gates, how to run tests, and PR conventions —
  pointing to (not copying) the deeper governance docs.

## 3. Scope

### In scope
The `CONTRIBUTING.md` document covering, accurately to the repo today: repository layout & the two
contributable unit types; Python 3.14 standard; tool isolation; how to add a new MCP tool; how to
add/modify an agent package; the four CI-enforced quality gates with exact commands; running tests
with `uv`; PR conventions; and cross-references to the deep-dive docs.

### Out of scope (non-goals)
- Rewriting or relocating `docs/development.md`, `docs/Constitution.md`, `packages/README.md`, or
  `scripts/README.md`.
- A commit-message convention, a `.github/PULL_REQUEST_TEMPLATE.md`, `CODE_OF_CONDUCT`, or CLA.
- Changing any workflow, gate threshold, tooling, or CI configuration — this only documents
  existing reality.
- Deep documentation of the non-Python `mcp-tools/browser-pilot/` (TypeScript/Node + vitest) tool —
  a brief "exists as an exception with its own tooling" note only.
- Per-tool `README.md` content or spec-template depth beyond a pointer.

## 4. Constraints & assumptions

- The document must match the repo as it is today; it changes no workflow, threshold, or config.
- Where the Constitution and another doc disagree, **the Constitution wins**.
- `CONTRIBUTING.md` is documentation — no automated tests of its own; **acceptance is by
  human/reviewer verification** against the criteria below and the source-of-truth files.
- Primary reader is a new **human** contributor (coding agents already have `CLAUDE.md`).
- `CONTRIBUTING.md` **references** the deep-dive docs rather than copying them.

## 5. Source-of-truth files (for accuracy verification)

Every command, path, and threshold in the delivered doc must be verifiable against:
`pyproject.toml` (workspace members, `requires-python = ">=3.14"`, ruff D + google pydocstyle),
`.pylintrc`, `.github/workflows/ci.yml` (the gate steps), `docs/development.md`, `docs/Constitution.md`,
`scripts/README.md`, `scripts/new_mcp_tool.py`, and `scripts/link_packages.py`.

> Verified during spec authoring against `.github/workflows/ci.yml`, the four gate steps are:
> `uv run ruff check --select D mcp-tools/*/src` · `uv run pylint mcp-tools/*/src` · per-tool
> `uv run pytest` honoring `--cov-fail-under=95` · `python scripts/link_packages.py check`.
> Root sync step is `uv sync --dev --all-packages`; Python pin is `uv python install 3.14`.

## 6. Stories

### Story A — Repo orientation & cross-references section of `CONTRIBUTING.md`

**As** a new contributor, **I want** the top of `CONTRIBUTING.md` to orient me on the repo's shape
and where the deep-dive docs live, **so that** I understand the workspace model before I make a
change.

**Acceptance criteria**
1. A file named `CONTRIBUTING.md` exists at the **repository root**. *(REQ AC-1)*
2. It states maruti is a `uv` **workspace** and Python **3.14** is the standard, and explains the
   two contributable unit types with their distinguishing layout: `mcp-tools/<name>/` (own
   `pyproject.toml`, `src/<pkg>/`, `tests/`, `specs/`, `README.md`; declared in root
   `pyproject.toml` under `[tool.uv.workspace].members`) and `packages/<name>/` (platform-bifurcated
   `claude-code/` and/or `github-copilot/`). *(REQ AC-2)*
3. It notes the **tool-isolation** rule: no `mcp-tools/<a>` imports from `mcp-tools/<b>` (Constitution §1).
4. It **cross-links** `docs/development.md`, `docs/Constitution.md`, `packages/README.md`, and
   `scripts/README.md` as authoritative deep-dive sources rather than duplicating them, positioning
   `CONTRIBUTING.md` as the concise front door. *(REQ AC-8)*
5. It briefly notes that a non-Python tool (`mcp-tools/browser-pilot/`, TypeScript/Node + vitest)
   exists as an exception with its own tooling, and is not a `uv` member.

### Story B — Contribution workflows, quality gates, tests & PR conventions section

**As** a new contributor, **I want** step-by-step workflows and the exact CI gates, **so that** I
can produce a mergeable PR that passes CI on the first try.

**Acceptance criteria**
1. **Add a new MCP tool:** documents `python scripts/new_mcp_tool.py <name> --description "..."`
   then `uv sync --dev --all-packages`, names the **manual fallback**, and states the
   `uv run <tool>` + `uvx` distribution contract (incl. the README `uvx` snippet expectation). *(REQ AC-3)*
2. **Add/modify an agent package:** documents editing source under `packages/<name>/<platform>/...`,
   **never** the `.claude/`/`.github/` mirrors, then `python scripts/link_packages.py sync` and
   committing the symlinks together; notes Windows symlink prerequisites (Developer Mode +
   `core.symlinks=true`) and the `repair` command. *(REQ AC-4)*
3. **Quality gates** — lists all **four** CI-enforced gates with the **exact** commands as they
   appear in `.github/workflows/ci.yml` / `docs/development.md`:
   `uv run ruff check --select D mcp-tools/*/src`, `uv run pylint mcp-tools/*/src`, the per-tool
   `--cov-fail-under=95` coverage gate (`cd mcp-tools/<tool> && uv run pytest --cov`), and
   `python scripts/link_packages.py check`. *(REQ AC-5)*
4. **Running tests with `uv`** — explains that the root sync MUST use `--all-packages` and **why**
   (omitting it prunes per-tool deps), and shows whole-workspace (`uv run pytest`), single-tool
   (`uv run pytest mcp-tools/<tool> -v`), and single-node invocations, plus the fast per-tool loop
   (`cd mcp-tools/<tool> && uv sync --dev && uv run pytest`). *(REQ AC-6)*
5. **PR conventions** — states: keep PRs small and scoped to a single tool/package; start from a
   failing test; land only with all CI gates green; and links to `docs/Constitution.md` Definition
   of Done. *(REQ AC-7)*

### Cross-cutting acceptance (applies to the whole deliverable)
- Every command, path, and gate threshold in the delivered doc is **accurate** to the current repo,
  verifiable against the source-of-truth files in §5 — **no invented commands or thresholds**.
  *(REQ AC-9)*

## 7. Acceptance-criteria traceability

| REQ AC | Covered by |
|---|---|
| 1 (file at root) | Story A · AC1 |
| 2 (uv workspace, 3.14, two unit types) | Story A · AC2 |
| 3 (add MCP tool + uvx contract) | Story B · AC1 |
| 4 (agent-package workflow + Windows symlinks) | Story B · AC2 |
| 5 (four exact CI gates) | Story B · AC3 |
| 6 (running tests, --all-packages + why) | Story B · AC4 |
| 7 (PR conventions + DoD link) | Story B · AC5 |
| 8 (cross-links, no duplication) | Story A · AC4 |
| 9 (everything accurate to repo) | Cross-cutting acceptance |

## 8. Definition of done

- `CONTRIBUTING.md` exists at repo root and satisfies all Story A & B acceptance criteria.
- A reviewer verifies every command/path/threshold against the §5 source-of-truth files.
- No source doc is rewritten/relocated; no workflow/threshold/config changed.
