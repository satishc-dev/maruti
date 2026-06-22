# Contributing to Maruti

Welcome! This is the concise **front door** for contributing to Maruti. Read it
once and you should be able to make a correct, mergeable change to either an MCP
tool or an agent package — and pass CI on the first try.

This guide deliberately **points to** the deep-dive docs rather than copying
them, so the canonical sources stay authoritative:

- [`docs/development.md`](docs/development.md) — practical day-to-day workflow (commands, tests, adding tools).
- [`docs/Constitution.md`](docs/Constitution.md) — the governing charter: principles, quality gates, Definition of Done. **When the Constitution and any other doc disagree, the Constitution wins.**
- [`packages/README.md`](packages/README.md) — authoring and structure of agent packages.
- [`scripts/README.md`](scripts/README.md) — the repo scripts (`new_mcp_tool.py`, `link_packages.py`).

## Repository shape

Maruti is a [`uv`](https://docs.astral.sh/uv/) **workspace**, and **Python 3.14**
is the standard (`requires-python = ">=3.14"` in the root `pyproject.toml`). There
are two kinds of unit you can contribute:

### 1. MCP tools — `mcp-tools/<name>/`

Each MCP tool is its own self-contained, independently releasable Python project:

```text
mcp-tools/<name>/
├── pyproject.toml      # its own project + dependency set
├── src/<pkg>/          # source (e.g. src/<snake_name>/{__init__,__main__,server}.py)
├── tests/              # its own tests
├── specs/              # its own specs (see docs/specs-template.md)
└── README.md           # purpose, safety limits, usage, uvx snippet
```

Every tool is declared in the root `pyproject.toml` under
`[tool.uv.workspace].members` (currently `mcp-tools/agent-memory`,
`mcp-tools/pdf-reader`, `mcp-tools/xlsx-reader`).

**Tool isolation (Constitution §1):** a tool MUST NOT import from or depend on a
sibling tool — `mcp-tools/<a>` never imports from `mcp-tools/<b>`. Shared code is
not allowed as an internal library; if true sharing is required it must be
promoted to a separately versioned external package.

> **Exception — `mcp-tools/browser-pilot/`** is a non-Python tool (TypeScript /
> Node, tested with [vitest](https://vitest.dev/)). It has its own tooling and is
> **not** a `uv` workspace member, so the Python workflows below do not apply to
> it.

### 2. Agent packages — `packages/<name>/`

Agent packages are bundles of Claude Code and GitHub Copilot CLI customizations.
Each package is **platform-bifurcated** — it may ship a `claude-code/`
subdirectory and/or a `github-copilot/` subdirectory:

```text
packages/<name>/
├── README.md
├── claude-code/        # subagents, skills, slash commands (+ plugin.json)
└── github-copilot/     # chat-mode agents, skills, prompt files
```

Either platform variant is optional. See [`packages/README.md`](packages/README.md)
for the full layout and naming conventions.

---

## Workflow: add a new MCP tool

Use the scaffolding script — it copies the `templates/mcp-tool/` skeleton into
`mcp-tools/<name>/`, substitutes the placeholders, renames the source module
directory, and registers the tool under `[tool.uv.workspace].members`:

```bash
python scripts/new_mcp_tool.py <name> --description "<one-line summary>"
uv sync --dev --all-packages
```

`<name>` must be lowercase-hyphen (e.g. `image-processor`).

**Manual fallback (no script):** copy `templates/mcp-tool/` into
`mcp-tools/<name>/`, rename `src/__module__/` to `src/<snake_name>/`,
search-and-replace the four `{{...}}` placeholders, and add the path to
`[tool.uv.workspace].members` yourself. Same outcome, more typing.

**Distribution contract (Constitution §5):** declare a `[project.scripts]` entry
so the tool runs via `uv run <tool>`, and give the tool a `README.md` containing a
copy/pasteable `uvx` snippet that fetches and runs it straight from GitHub — for
example:

```bash
uvx --from "git+https://github.com/satishc2437/maruti.git@<ref>#subdirectory=mcp-tools/<tool-folder>" \
  python -m <tool_module>
```

See [`docs/development.md`](docs/development.md) for devcontainer auto-discovery
and the full step-by-step.

## Workflow: add or modify an agent package

The `.claude/` and `.github/` publish targets are **symlink mirrors** managed by
`scripts/link_packages.py` and enforced by CI. **Never edit the mirrors directly**
— always edit the source under `packages/<name>/<platform>/...`.

1. Edit (or create) the source under `packages/<name>/<platform>/...`.
2. Sync the mirror from the repo root:
   ```bash
   python scripts/link_packages.py sync
   ```
3. **Commit the source and the resulting symlinks together** so the mirror never
   drifts from the source.

**Windows prerequisites (one-time per machine):** real filesystem symlinks need
**Developer Mode** enabled (Settings → Privacy & security → For developers →
Developer Mode) *and* git symlink support:

```bash
git config --global core.symlinks true
```

If you cloned the repo on Windows *before* setting `core.symlinks=true`, the
mirror entries will be plain text files instead of symlinks. Fix them with:

```bash
python scripts/link_packages.py repair
```

Details in [`packages/README.md`](packages/README.md) and
[`scripts/README.md`](scripts/README.md).

---

## Quality gates (CI-enforced)

CI (`.github/workflows/ci.yml`) pins Python 3.14, runs `uv sync --dev --all-packages`,
then enforces **four** gates. Run them locally before you push:

```bash
# 1. Docstring lint — Google convention, ruff pydocstyle D* rules (scope limited
#    to mcp-tools/*/src by config).
uv run ruff check --select D mcp-tools/*/src

# 2. Pylint — MUST exit 0 (zero E/W/F messages); uses the root .pylintrc.
uv run pylint mcp-tools/*/src

# 3. Coverage gate — honest ≥95% per tool. Each tool's pyproject pins
#    --cov-fail-under=95, so running its tests fails below the threshold.
cd mcp-tools/<tool> && uv run pytest --cov

# 4. Agent symlink mirror check — fails on drift between packages/ and the mirrors.
python scripts/link_packages.py check
```

> In CI, gate 3 runs as `uv run pytest -q` inside each tool's directory
> (`mcp-tools/agent-memory`, `mcp-tools/pdf-reader`, `mcp-tools/xlsx-reader`); the
> `--cov-fail-under=95` threshold is baked into each tool's `pyproject.toml`.

## Running tests with `uv`

Always sync the workspace with `--all-packages` at the root. **Why:** without it,
`uv` prunes dependencies that belong to individual tools while syncing the root
project, causing `ModuleNotFoundError`s across the workspace.

```bash
# Sync the whole workspace (do this at the root).
uv sync --dev --all-packages

# Whole workspace
uv run pytest

# Single tool
uv run pytest mcp-tools/<tool> -v

# Single test node
uv run pytest mcp-tools/pdf-reader/tests/test_pdf_tools_and_processor.py::test_pdf_processor_and_tool_endpoints -v

# Fast per-tool loop (uses the tool's local dev deps)
cd mcp-tools/<tool> && uv sync --dev && uv run pytest
```

## PR conventions

- **Keep PRs small and scoped to a single tool or package.**
- **Start from a failing test** (red → green → refactor) — TDD is required
  (Constitution §6).
- **Land only with every CI gate green** — all four gates above must pass before
  merge.
- A change is complete when it meets the **Definition of Done** in
  [`docs/Constitution.md`](docs/Constitution.md) (Development Workflow & Quality
  Gates → *Definition of Done*).

Thanks for contributing!
