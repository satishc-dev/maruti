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
