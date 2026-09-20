---
name: st-cadence
description: 'Use by any software-team lead running cycles and by any crew agent reporting work; apply the shared Scrum directory layout, cycle budget, work-log block, status values, validation scope, retrospectives, lessons, and unattended-operation safety rules.'
---
# st-cadence
Use this skill when a team lead runs cycles or a crew agent reports work.
For full detail, read `docs/CADENCE.md`, `docs/PARALLELISM.md`, `docs/HANDOFF-PROTOCOL.md`, and `docs/ROLES.md`.
## Core rule
A cycle is one dispatch-and-collect round by a team lead.
The counter starts at `1`, increments by `1`, and never resets within the workstream.
The lead owns cadence files.
Crew agents return work-log blocks.
Crew agents never write journal files.
## `.scrum/` layout
Cadence files live in `.scrum/`.
The directory is machine-local and gitignored.
Durable handoffs live in `.software-team/`.
```text
.scrum/
├── lessons.md
└── <req>-<ws>/
    ├── plan.md
    ├── design.md
    ├── retrospective.md
    └── agents/
        ├── <agent-id>.md
        └── ...
```
| Path | Writer | Purpose |
|---|---|---|
| `.scrum/lessons.md` | Lead at closeout | Project-agnostic FIFO lesson scratchpad. |
| `.scrum/<req>-<ws>/plan.md` | Lead | Frozen plan after signoff. |
| `.scrum/<req>-<ws>/design.md` | Lead | Optional or required design contract. |
| `.scrum/<req>-<ws>/retrospective.md` | Lead | End-of-workstream retrospective. |
| `.scrum/<req>-<ws>/agents/<agent-id>.md` | Lead | Journals for crew, duck, and lead observations. |
If the fact matters after the run, write a handoff envelope in `.software-team/REQ-NNN/ledger.md`.
## Cycle budget
Default budget is `12` cycles.
Warning occurs at budget minus `2`; with default budget, warn at cycle `10`.
Hard halt occurs at the budget before dispatching another cycle.
The lead does not silently exceed the budget.
| Point | Lead action |
|---|---|
| Cycle start | Dispatch work within capacity. |
| Warning point | Record status and prepare escalation if completion is unlikely. |
| Hard halt | Stop dispatch and escalate to Project-Lead. |
| Override | Allowed only when requested or configured; minimum override is `3`. |
At hard halt, Project-Lead chooses extend, finalise, or abandon.
The lead waits for that decision.
## Work-log block
Crew agents return this block.
Leads prepend it to the agent journal.
Newest entries appear first.
```markdown
## [Cycle <N>] <taskId> · <ISO-8601 timestamp>

- **agentId:** <agent-id>
- **taskId:** <task-id>
- **taskName:** <task-name>
- **taskDescription:** <task-description>
- **requirement:** <REQ-NNN or requirement reference>
- **workstream:** <REQ-NNN/ws<k>>
- **cycle:** <cycle-number>
- **status:** <in-progress | impeded | done | observation>

### Details
**Done** — <bulleted list or "none">
**Doing** — <current work or next step>
**Impediments** — <none, or concrete escalation ask>
**ETA** — <cycles remaining estimate, or "complete">
```
## Required fields
| Field | Rule |
|---|---|
| `cycle` | Current cycle number. |
| timestamp | ISO-8601 with explicit UTC offset. |
| `agentId` | Stable id matching journal filename stem. |
| `taskId` | Stable task id from `plan.md`, or `cycle-<N>-observation`. |
| `taskName` | Human-readable task name. |
| `taskDescription` | One or two sentences. |
| `requirement` | Requirement id or specific reference. |
| `workstream` | Full workstream id, for example `REQ-007/ws2`. |
| `status` | One allowed value. |
| Details | Done, Doing, Impediments, ETA. |
## Allowed status values
| Status | Meaning |
|---|---|
| `in-progress` | Work continues next cycle. |
| `impeded` | Agent cannot proceed safely without a decision, permission, input, or dependency. |
| `done` | Assigned task is complete. |
| `observation` | Lead-written cycle summary or coordination note. |
Use `impeded` for work that cannot proceed.
Return the concrete decision or input needed.
## Journal writer rule
The lead writes journal files.
Crew agents only return blocks.
The lead validates required fields and prepends the block to `.scrum/<req>-<ws>/agents/<agent-id>.md`.
One writer per file prevents lost entries and interleaved content.
If a crew agent omits the block, the lead writes an `observation` entry and uses the response as evidence.
## Plan
`plan.md` is written before dispatch and frozen after signoff.
Changing it requires new signoff by the dispatcher.
Project-Lead signoff is required for requirement scope, workstream scope, file scope, budget, or acceptance changes.
A plan states workstream, objective, team composition, tasks, cycle budget, completion condition, risks, and lessons applied.
Each task states id, name, description, requirement reference, assigned agent, `changeScope`, `validationScope`, and success criteria.
## Design
`design.md` is required for public contract changes, new components, cross-cutting changes, data model changes, concurrency-sensitive work, security-sensitive surfaces, or ambiguous build paths.
It states workstream, source links, overview, components, interfaces, data model, alternatives, validation strategy, risks, and open questions.
It is frozen after signoff.
Changing it requires renewed signoff.
## Validation scope
| Scope | Meaning | Required validation |
|---|---|---|
| `targeted` | Local change within one component, package, or file set. | Checks covering the touched area. |
| `full` | Cross-cutting, public, schema-level, or multi-subsystem change. | Full project validation appropriate to the repository. |
`local` maps to `targeted`.
`cross-cutting` maps to `full`.
The mechanical gate verifies declared scope and reports if the declaration is wrong.
## Turn budgets
Every dispatched agent carries `turnBudget`, `cycle`, `returnWhenNearBudget: true`, and `expectedWorkLog`.
Unbounded looping is prohibited.
When near budget, return `in-progress` with evidence, Doing, Impediments, and ETA.
A lead narrows, reassigns, or escalates work that repeatedly returns without new evidence.
## Review cadence
Every team except Project-Lead has a duck.
Your duck must pass the work.
At least two rounds always occur.
The exchange is recorded in `.software-team/REQ-NNN/ledger.md`.
Leads produce good work, send it to their duck, and address returned findings.
## Retrospective
Write `retrospective.md` when the workstream closes by delivery, finalise, or abandon.
Include workstream, outcome, cycle budget consumption, what went well, what went poorly, impediments and resolution, surprises, validation result, handoff result, and distilled lessons.
## Lessons
`.scrum/lessons.md` is a project-agnostic FIFO scratchpad.
Cap it at `5 KB` or `5120` bytes.
Newest entries go first.
Evict whole entries from the bottom when over cap.
Drop an oversized single entry rather than splitting it.
Link each lesson to the source retrospective.
Lesson shape:
```markdown
- <guidance>. **Why:** <short reason>. [[REQ-NNN-ws<k>]]
```
Project-specific tasks belong in durable handoffs or requirement updates.
## Operations never performed unattended
Return these as impediments:
| Operation | Required response |
|---|---|
| Force-push | Return an impediment to Project-Lead. |
| History rewrite | Return an impediment to Project-Lead. |
| Deleting outside declared scope | Return an impediment to Project-Lead. |
| Reading secrets | Return an impediment to Project-Lead. |
| Writing secrets | Return an impediment to Project-Lead. |
| Spending money | Return an impediment to Project-Lead. |
Routine safe operations are allowed within declared scope: read files, write declared files, run matched validation, inspect git status and diff, create workstream commits, and open a pull request.
## Closeout
A workstream closes only after the lead collects live agents, writes final journals, writes the retrospective, updates lessons, produces durable handoff, returns Project Memory or board or lifecycle requests, and records validation or the impediment that prevented it.
Closeout does not mean acceptance.
Project-Lead accepts delivered work against the requirement.
