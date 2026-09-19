# Project Lead — Claude Code variant

Installable Claude Code plugin bundling one skill (`project-lead`) and one slash
command (`/project-lead`). The Project Lead is the stakeholder-facing
orchestrator: it owns requirements as official OKF v0.2 repo docs, keeps Project
Memory and a linked GitHub Project Kanban current, and delivers by **guided
handoff** to the `pm-team` and `dev-team` plugins. It never writes specs or code
itself.

## Install

### Option A — via the maruti marketplace (recommended)

Two-step flow from a Claude Code session in the target repo, no local checkout
required:

```
/plugin marketplace add satishc-dev/maruti
/plugin install project-lead@maruti
```

The marketplace manifest lives at `.claude-plugin/marketplace.json` in the maruti
repo root. The first command is one-time per machine; the marketplace stays
registered across sessions.

To pin the marketplace to a specific tag or branch:

```
/plugin marketplace add satishc-dev/maruti@<tag-or-branch>
```

### Option B — from a local checkout

```
/plugin install <absolute-path>/packages/project-lead/claude-code
```

### Option C — project-local copy

```bash
mkdir -p .claude/commands .claude/skills/project-lead
cp packages/project-lead/claude-code/commands/*.md          .claude/commands/
cp packages/project-lead/claude-code/skills/project-lead/*  .claude/skills/project-lead/
```

## Prerequisites

| Integration | Setup |
|---|---|
| GitHub | `gh auth login` for the org/repo where issues, PRs, and the Project live. Needed for the Kanban, the Requirement issue/label, and sub-issues. |
| pm-team | Installed transitively by the plugin marketplace; local-copy installs should add `pm-team@maruti`. |
| dev-team | Installed transitively by the plugin marketplace; local-copy installs should add `dev-team@maruti`. |
| Obsidian (optional) | Open `.project-memory/` itself to browse the OKF bundle, graph view, and logs. |

## What the Lead does

1. **Bootstrap** (`/project-lead bootstrap`) — idempotently scaffolds
   `.project-memory/` and `docs/requirements/` as OKF v0.2 bundles, detects or
   creates the GitHub Project Kanban, checks teams, and writes a pointer into
   `AGENTS.md`/`CLAUDE.md`.
2. **Intake** (`/project-lead` + a need) — captures a requirement as an official
   `docs/requirements/REQ-NNN.md` doc and drives it to the Definition of Ready.
3. **Approve** (`/project-lead approve REQ-NNN`) — opens a **requirement PR**;
   your approve/merge is the official signoff. The Lead stamps lifecycle, OKF
   status, and verification, then creates the Requirement issue.
4. **Migrate** (`/project-lead migrate [--apply]`) — dry-runs or applies the OKF
   migration for pre-OKF Project Memory and requirement docs.
5. **Guided handoff** — for approved requirements, the Lead launches/recommends
   `/pm-team <requirement>` and later `/dev-team <issue>`, reconciling outcomes
   back into memory + the Kanban.
6. **Status / sync / lint** — `/project-lead status` reports the funnel; `sync`
   reconciles the board with reality; `lint` is an advisory OKF + wiki
   health-check.

## Usage

```
/project-lead bootstrap
/project-lead I want users to be able to export their data as CSV
/project-lead requirement new
/project-lead approve REQ-001
/project-lead migrate
/project-lead migrate --apply
/project-lead status
/project-lead sync
/project-lead lint
```

## Artifacts the Lead maintains

| Path | Purpose |
|---|---|
| `docs/requirements/` | Official OKF requirement bundle + register |
| `.project-memory/` | The Lead's OKF Project Memory bundle |
| GitHub Project (v2) | The stakeholder Kanban (Intake → … → Done) |
| Requirement issue + sub-issues | GitHub-native Requirement → Feature → Story traceability |

The full OKF memory layout, requirement doc schema, lifecycle, Definition of
Ready, approval contract, migration algorithm, and advisory lint checklist are
documented in [`../MEMORY-SCHEMA.md`](../MEMORY-SCHEMA.md).

## Boundaries

The Project Lead **never** writes product code or specs and **never** bypasses
the signoff gates of `pm-team` or `dev-team`. It is the coordinator and the
keeper of durable project context — the work is done by the teams.
