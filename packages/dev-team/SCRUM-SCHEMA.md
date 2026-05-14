# Scrum Schema

This document defines the on-disk Scrum schema that orchestrators in this repository use to plan, journal, retrospect, and accumulate lessons across projects. It is intentionally team-agnostic — the same schema is used by every Scrum-aware orchestrator package shipped from this monorepo.

The schema lives in the **consumer repo's working directory** (the repo where the orchestrator is invoked), never inside the package directory.

## Directory layout

```
.scrum/
├── lessons.md                              # cross-project, 5KB FIFO
└── <project-slug>/
    ├── plan.md                             # frozen plan after user signoff
    ├── retrospective.md                    # written at project end
    └── agents/
        ├── team-lead.md                    # orchestrator's journal
        ├── software-developer-1.md         # one file per persistent agent identity
        ├── software-developer-2.md
        ├── code-reviewer-1.md
        └── ...
```

- `<project-slug>` is derived by the orchestrator from the work-item title (kebab-case, 3–6 words).
- One file per **persistent agent identity** (e.g., `software-developer-1.md`, `software-developer-2.md`). Identities are stable across cycles — the same `software-developer-1` is re-dispatched cycle after cycle and accumulates history in its own file.
- The orchestrator's journal (`team-lead.md`) sits next to subagent journals under `agents/`.
- The orchestrator is the **SOLE writer** to every file under `agents/`. Subagents emit their work-log entry as the final block of their response text; the orchestrator parses that block and prepends it to the appropriate agent file. This eliminates concurrent-write hazards.

## Work-log entry schema

Each entry written into any file under `agents/` MUST conform to this format. Newest entry on top.

```markdown
## [Cycle <N>] <taskId> · <ISO8601 timestamp UTC>

- **agentId:** <agent-id>
- **taskId:** <task-id>
- **taskName:** <task-name>
- **taskDescription:** <task-description>
- **requirement:** <requirement-ref or "n/a">
- **cycle:** <project-cycle-number>
- **status:** <in-progress | blocked | done | observation>

### Details
**Done** — <bulleted list of what was completed this turn>
**Doing** — <what is in-flight / will be next turn>
**Blockers** — <none | description with concrete unblock ask>
**ETA** — <cycles remaining estimate, or "complete">
```

Field notes:

- `agentId` matches the filename stem (e.g., `software-developer-1` for `software-developer-1.md`). The orchestrator's own entries use `team-lead-1`.
- `status` values:
  - `in-progress` — work continues next cycle; turn budget hit or work not yet complete.
  - `blocked` — cannot proceed without external input; Blockers field MUST contain a concrete unblock ask.
  - `done` — task is complete this cycle.
  - `observation` — used by the orchestrator for cycle summaries; `taskId` is `cycle-<N>-observation`.
- `requirement` is an acceptance-criterion reference (e.g., `AC-1`, `AC-3`) or `n/a`.
- The `Details` section is required even on `blocked` or partial completion — at minimum, fill the fields with concrete content; do not write "n/a" or leave them empty unless truly nothing applies.

## Cycle budget contract

- **Default budget:** 12 cycles.
- **Warn threshold:** at cycle `budget - 2` (default 10), the orchestrator emits a warning to the user with the current status and offers: continue without extending, revise plan, or abort.
- **Hard halt:** at cycle `budget` (default 12), the orchestrator HALTS before dispatching a new cycle. It asks the user one question with three choices:
  1. **Continue (+N cycles)** — extend the budget by N (user-supplied) and resume.
  2. **Abort** — stop the project; jump straight to the retrospective with the project marked as aborted.
  3. **Finalize** — stop the loop with current state; jump to the retrospective with current state as final.
- **Override:** the budget is configurable per invocation via `--cycles N`. `N` MUST be an integer `>= 3`. Smaller values are rejected; the orchestrator falls back to the default.
- The cycle counter starts at `1`, increments by `1` per scrum pass, and **never resets** within a project.

## Lessons memory (`.scrum/lessons.md`)

The lessons file is a **cross-project** scratch-pad of project-agnostic guidance distilled from each retrospective. It is read at the start of every new project (Phase 0) so future plans can learn from prior runs.

Rules:

- **Cap:** 5 KB (5120 bytes).
- **Order:** newest on top, oldest on bottom (prepend on write).
- **FIFO eviction:** after each prepend, if the file exceeds 5 KB, trim from the bottom until under the cap. Lessons are evicted **whole** — never split a lesson across the trim boundary. If a single lesson is larger than the cap, drop it entirely rather than truncate it mid-content.
- **Lesson shape:** 1–2 lines of guidance + optional `**Why:** ...` follow-up. Each lesson MUST include a `[[<source-project-slug>]]` backlink so a reader can trace it back to the retrospective that produced it.
- **Project-agnostic content:** lessons should describe guidance that likely applies to FUTURE projects, not specifics of the project that produced them. "Always run linters before claiming done" is a lesson; "Refactor `foo.py`" is not.

Example entry:

```markdown
- Always confirm test runner discovery before claiming green CI. **Why:** missed pyproject vs Makefile divergence cost 2 cycles. [[fix-checkout-typos]]
```

## Retrospective format (`.scrum/<project-slug>/retrospective.md`)

Written once, at project end, after the cycle loop exits (whether by success, abort, or finalize). The orchestrator synthesizes it from every file under `.scrum/<project-slug>/agents/*.md`.

Required sections (in order):

1. **What went well** — concrete moments where the plan, dispatch, or execution worked as intended.
2. **What went poorly** — friction points, miscommunications, wasted cycles.
3. **Blockers encountered + resolution** — what stalled the project, what unblocked it.
4. **Cycle budget consumption** — `<used> of <budget>` plus 1–2 sentences on pacing.
5. **Surprises** — anything outside the plan: new constraints discovered, behaviors that needed redesign mid-stream.
6. **Distilled lessons** — 1–3 bullets, each in the form that will be appended to `.scrum/lessons.md`. Include the `[[<project-slug>]]` backlink in each.

After writing the retrospective, the orchestrator appends the distilled lessons (prepended, newest on top) to `.scrum/lessons.md` and applies the FIFO trim.

## Plan format (`.scrum/<project-slug>/plan.md`)

Written once, at the start of the project, and frozen after user signoff. Re-signoff is required if the orchestrator amends the plan during execution.

Required sections:

- **Project slug** — the derived slug.
- **Objective** — one-sentence summary of the work-item goal.
- **Team composition** — list of agent identities the orchestrator will spawn. Each row: `agentId`, `role`, `responsibility` (1 sentence).
- **Task breakdown** — list of tasks. Each row: `taskId` (`task-<n>`), `taskName`, `taskDescription` (1–2 sentences), `requirementRef` (acceptance-criterion id or n/a), `assignedAgentId`, `successCriteria`.
- **Cycle budget** — the cap `N` and warn threshold `N-2`.
- **Definition of done at the project level** — when does the orchestrator declare success?
- **Risks anticipated** — 1–4 risks / blockers anticipated.
- **Lessons applied** — zero or more bullets from `.scrum/lessons.md` that influenced this plan, each linked with `[[<source-project-slug>]]`.

The plan is presented to the user IN CHAT before any subagent is dispatched. The orchestrator MUST NOT proceed until the user explicitly approves.
