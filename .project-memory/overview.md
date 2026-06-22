# Project Overview

> Living synthesis of what this project is and where it stands. Rewritten as the
> project evolves — not appended to.

## What this is

**Maruti** is a monorepo of self-contained **Model Context Protocol (MCP)
tools/servers**, plus a set of Copilot/agent definitions that consume them. It is
a `uv` workspace where each tool under `mcp-tools/<name>/` is an independently
releasable Python project (its own `pyproject.toml`, `src/`, `tests/`,
`README.md`). Python 3.14 is the repo standard.

Alongside the tools, `packages/<name>/` holds project-owned Claude Code and
GitHub Copilot customizations (subagents, skills, slash commands, chat modes,
prompt files) — including the **Project-Lead**, **PM-Team**, and **Dev-Team**
agents that drive the delivery workflow.

## Core principles (from `docs/Constitution.md`)

- **Tool isolation:** no `mcp-tools/<a>` may import from `mcp-tools/<b>`.
- **Tool-local everything:** each tool owns its config, source, tests, README.
- **uv/uvx distribution contract:** every tool runs via `uv run <tool>` and via
  `uvx ... #subdirectory=mcp-tools/<tool>`.
- **MCP stdio servers:** `src/<pkg>/__main__.py` → `server.py`, JSON-RPC over stdio.
- **Devcontainer-first:** everything works inside `.devcontainer`.

## Current state

Project-Lead bootstrap has just been run (see [log.md](log.md)). Project Memory
and the `docs/requirements/` area are initialized, the `requirement` label exists,
and the linked GitHub Project board **"maruti Delivery"** is live with the full
Status funnel (see [project-link.md](project-link.md)).

**REQ-001** is the first captured requirement — a top-level `CONTRIBUTING.md`,
now **`delivered`**. The full lifecycle is complete: approved (PR #6, Requirement
[issue #7]), specced by PM-Team (spec PR #8; Feature #9 + Stories #11/#10), built
by Dev-Team (code PR [#12] merged into `pl-e2e-test`), and reviewed against all 9
acceptance criteria (**all PASS**). Requirement #7 and all sub-issues are closed;
the board item is **Done**. See [requirements-register.md](requirements-register.md).

## Active initiatives

- **REQ-001 — Top-level CONTRIBUTING.md** (`delivered`). First stakeholder
  requirement: a root `CONTRIBUTING.md` documenting the `uv` workspace, Python
  3.14 standard, adding MCP tools / agent packages, the four CI quality gates,
  running tests with `uv`, and PR conventions. End-to-end complete — code PR
  [#12](https://github.com/satishc-dev/maruti/pull/12) merged into `pl-e2e-test`,
  all acceptance criteria verified, board item **Done**. See
  [docs/requirements/REQ-001-contributing-guide.md](../docs/requirements/REQ-001-contributing-guide.md).

## Near-term plan

1. **REQ-001 is closed out.** No further action unless the stakeholder requests
   follow-ups (e.g. a PR template, `CODE_OF_CONDUCT`, or deeper Node/`browser-pilot`
   contribution docs — explicit non-goals of REQ-001).
2. Capture the next stakeholder requirement via **intake** when one arrives.
