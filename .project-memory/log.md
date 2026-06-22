# Project Memory — Log

Append-only chronology. Each entry begins `## [YYYY-MM-DD] <event> | <subject>`
where `<event>` ∈ `ingest | requirement | approval | handoff | sync | delivery | lint | decision`.

## [2026-06-21] bootstrap | Project-Lead initialized for satishc-dev/maruti

- Platform detected: **GitHub** (remote `github.com/satishc-dev/maruti`); active
  `gh` account `satishc-dev`.
- Created Project Memory skeleton under `.project-memory/`: `schema.md`,
  `index.md`, `log.md`, `overview.md`, `requirements-register.md`,
  `project-link.md`, and `wiki/{initiatives,decisions,architecture,stakeholders,risks,glossary}/`.
- Created requirements area `docs/requirements/` with `_template.md` and the
  register `README.md`.
- GitHub Project v2: the active token unexpectedly **has** the `project` scope,
  so `gh project create` succeeded. It ran twice → two duplicate "maruti Delivery"
  projects; deleted #4, kept **#5** as canonical. Reconfigured its **Status**
  single-select field to the full funnel (Intake → … → Done, Parked). IDs
  recorded in `project-link.md`.
- Requirement concept: custom "Requirement" issue type **not** available for this
  user-owned repo → created the `requirement` label (color `#5319e7`). Using
  `label:requirement` as the fallback.
- Team availability: **pm-team@maruti** and **dev-team@maruti** confirmed
  installed (Copilot plugins + `packages/` + `.github/agents/`).
- Added a "Project Lead" pointer section to `CLAUDE.md`.

## [2026-06-21] requirement | REQ-001 captured — top-level CONTRIBUTING.md

- Intake (Path A — stakeholder-authored brief): the stakeholder asked for a
  top-level `CONTRIBUTING.md` explaining the `uv` workspace layout
  (`mcp-tools/<name>` tools, `packages/<name>` agent packages), Python 3.14
  standard, adding a new MCP tool, adding/modifying an agent package +
  `scripts/link_packages.py`, the quality gates (ruff `--select D`, pylint zero
  E/W/F, ≥95% per-tool coverage), running tests with `uv`, and PR conventions.
- Verified the facts directly against the repo: root `pyproject.toml`
  (`[tool.uv.workspace].members` = agent-memory, pdf-reader, xlsx-reader; ruff D
  / google convention), `.pylintrc` (disables C,R), each tool's
  `--cov-fail-under=95`, `.github/workflows/ci.yml` (the four CI gates),
  `docs/development.md`, `packages/README.md`, `scripts/README.md`,
  `scripts/new_mcp_tool.py`.
- Authored `docs/requirements/REQ-001-contributing-guide.md` with full
  frontmatter and testable acceptance criteria. Definition of Ready satisfied →
  advanced `status: draft → in-review`.
- Recorded two **non-blocking** open questions with default assumptions: (1) how
  deeply to cover the non-Python `mcp-tools/browser-pilot/` (TypeScript/Node,
  vitest, not a uv member); (2) "concise front-door + links" vs. an exhaustive
  doc given overlap with `docs/development.md`.
- Updated both registers (`docs/requirements/README.md` and
  `.project-memory/requirements-register.md`).
- Per the test-run scope: **no** PR, **no** GitHub issue, **no** board item, no
  commit/push — intake stops at the doc + registers. Approval is a separate step.

## [2026-06-21] approval | REQ-001 approved — top-level CONTRIBUTING.md

- Re-checked Definition of Ready: still satisfied (clear problem + outcome,
  testable acceptance criteria, explicit scope in/out, two **non-blocking** open
  questions with default assumptions). Gate passed.
- Guardrail confirmed: PM-Team was **not** engaged at any point before the
  `approved` stamp — no spec work, no Feature/Story seeding.
- Requirement PR: branch `users/satishc-dev/requirements/REQ-001-contributing-guide`
  off **`pl-e2e-test`** (integration base for this test, not `main`) →
  [PR #6](https://github.com/satishc-dev/maruti/pull/6), base `pl-e2e-test`.
  Advanced `status: in-review → approved`, stamped `approved_by`
  "satishc-dev (e2e-test operator)" + `approved_at` 2026-06-21, bumped `version`
  1 → 2 with a Change-log entry. Stakeholder signoff was **pre-authorized for
  this e2e test**, so the PR was self-merged to represent signoff.
- Requirement issue: custom "Requirement" issue type unavailable → created
  `requirement`-labeled [issue #7](https://github.com/satishc-dev/maruti/issues/7)
  (problem + acceptance criteria + doc link). URL recorded in the doc frontmatter
  (`requirement_issue`) and both registers.
- Board: added issue #7 to Project **#5 "maruti Delivery"**
  (item `PVTI_lAHOANBnPM4BbTjQzgwamCk`) and set **Status → Ready for Spec**
  (option `74659340`).
- Updated `docs/requirements/REQ-001-contributing-guide.md` (status, stamps,
  links), `docs/requirements/README.md`, and
  `.project-memory/requirements-register.md`. Committed onto `pl-e2e-test` via the
  merged PR #6.
- **Next, separate step:** guided handoff to `pm-team` for the spec — not done in
  this step.

## [2026-06-21] handoff | REQ-001 spec handoff to PM-Team — CONTRIBUTING.md

- Guardrail confirmed: REQ-001 was `approved` before engaging PM-Team. Built the
  handoff brief from `docs/requirements/REQ-001-contributing-guide.md` (approved
  problem + 9 acceptance criteria + scope in/out + doc path + Requirement issue
  #7) and moved board item `PVTI_lAHOANBnPM4BbTjQzgwamCk` **Ready for Spec → In
  Spec** (`8edf51ce`).
- Dispatched **PM-Team** (approved mode, autonomous) with explicit instructions:
  base branch is **`pl-e2e-test`** (not `main`), parent Requirement is **#7**,
  deliverable is a single top-level `CONTRIBUTING.md` (right-size the spec).
- PM-Team returned: spec `docs/specs/contributing-guide/contributing-guide.md`;
  **spec [PR #8](https://github.com/satishc-dev/maruti/pull/8)** with base
  **`pl-e2e-test`** (verified via `gh pr view --json baseRefName`); seeded
  Feature [#9](https://github.com/satishc-dev/maruti/issues/9) and Stories
  [#11](https://github.com/satishc-dev/maruti/issues/11) (orientation &
  cross-refs) / [#10](https://github.com/satishc-dev/maruti/issues/10)
  (workflows, gates, tests & PR conventions). PM-Team created `feature`/`story`
  labels as none existed.
- Reconciliation: linked **#9, #11, #10 as sub-issues of #7**
  (`gh issue edit 7 --add-sub-issue`; verified `subIssuesSummary.total = 3`).
  Updated REQ-001 doc (`status: approved → specced`, `version` 2 → 3, `links.specs`
  + `links.child_issues`, Change-log v3), both registers, and moved the board item
  **In Spec → Ready for Dev** (`98927679`).
- **Dev-Team NOT engaged** (per instruction). REQ-001 is now eligible for build:
  Stories #11 and #10 are the next dev hand-offs once PR #8 is reviewed/merged.

## [2026-06-22] delivery | REQ-001 CONTRIBUTING.md delivered via Dev-Team (PR #12)

- **Guided handoff to Dev-Team.** Moved Stories #11 & #10 board items Ready for
  Dev → **In Dev**, then dispatched the `dev-team` agent to author the top-level
  `CONTRIBUTING.md` per the merged spec (`docs/specs/contributing-guide/contributing-guide.md`)
  and REQ-001 acceptance criteria. Instructed: base branch **`pl-e2e-test`** (not
  `main`), one code PR (single docs file) referencing #11 and #10, operate
  autonomously, no invented commands.
- **Dev-Team delivered** code PR [#12](https://github.com/satishc-dev/maruti/pull/12)
  (head `docs/contributing-md-req-001`, base **`pl-e2e-test`** ✅), adding
  `CONTRIBUTING.md` (190 lines, docs-only). Re-checked out `pl-e2e-test` after the
  sub-agent run before any local commits.
- **Reconcile.** Recorded PR #12 in the REQ-001 doc (`links.prs`), both registers,
  and moved Story board items to **In Review (Dev)** (`bb136f20`).
- **Review (operator pre-authorized).** Verified the deliverable against all **9**
  REQ-001 acceptance criteria — every command/path/threshold checked against
  `.github/workflows/ci.yml` (4 gate steps, `uv python install 3.14`,
  `uv sync --dev --all-packages`), root `pyproject.toml` (members =
  agent-memory/pdf-reader/xlsx-reader, `requires-python ">=3.14"`), `.pylintrc`,
  each tool's `--cov-fail-under=95`, `scripts/new_mcp_tool.py`,
  `scripts/link_packages.py` (sync/check/repair), `templates/mcp-tool/`, and the
  `browser-pilot` Node exception. **All 9 PASS.**
- **Finalize.** Merged PR #12 into `pl-e2e-test` (merge `b56850d`). Closed Stories
  #11 & #10, Feature #9, and Requirement #7 (closed **manually** — the PR targeted
  `pl-e2e-test`, not the default branch, so `Closes #` keywords did not auto-fire).
  Moved all four board items to **Done** (`30f35057`). REQ-001 `status: specced →
  delivered`, `version` 3 → 4, Change-log v4.
