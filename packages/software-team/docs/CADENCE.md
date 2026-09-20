---
type: Team Contract
title: Software Team — Working Cadence
description: Unified working-cadence schema for plans, cycles, journals, design notes, retrospectives, and lessons.
status: stable
---

# Working Cadence

This contract defines the working cadence for the `software-team` package.
It replaces the divergent legacy `SCRUM-SCHEMA.md` copies shipped by the
`dev-team` and `pm-team` packages.

One package has one cadence schema. Every team lead uses this version.

Where this contract and `ROLES.md` disagree, `ROLES.md` wins.

## 1. Scope

The cadence applies to team-led work by:

| Team | Uses cadence for |
|---|---|
| Research-Team | Research rounds and findings production. |
| Architect-Team | Solution architecture, ADRs, and development principles. |
| PM-Team | Feature specifications and story decomposition. |
| Dev-Team | Implementation, validation, pull request preparation, and internal gates. |
| UX-Team | UX briefs, flows, and wireframes. |
| Project-Lead | Workstream planning, dispatch, collection, escalation, and acceptance tracking. |

Project-Lead remains the only user-facing voice.
Other leads return results to their dispatcher.

## 2. Working directory

Cadence files live in `.scrum/`.
The directory is machine-local and gitignored.

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

`<req>-<ws>` is the workstream key.

Examples:

```text
.scrum/REQ-007-ws1/
.scrum/REQ-007-ws2/
.scrum/REQ-012-ws1/
```

The workstream key mirrors `REQ-NNN/ws<k>` from `PARALLELISM.md`.

Files:

| Path | Required | Purpose |
|---|---|---|
| `.scrum/lessons.md` | Yes | Cross-project FIFO scratchpad. |
| `.scrum/<req>-<ws>/plan.md` | Yes | Frozen plan after signoff. |
| `.scrum/<req>-<ws>/design.md` | Conditional | Optional design contract. |
| `.scrum/<req>-<ws>/retrospective.md` | Yes at close | End-of-workstream retrospective. |
| `.scrum/<req>-<ws>/agents/<agent-id>.md` | As agents run | Lead-written journals for crew, duck, and lead observations. |

These files are working memory only. Durable handoffs are committed in
`.software-team/` and, when they change project context, Project Memory.

## 3. Cycles

A cycle is one dispatch-and-collect round by a team lead.

The counter starts at `1`.
It increments by `1` for each round.
It never resets within the workstream.

Cycle budget:

| Setting | Rule |
|---|---|
| Default budget | `12` cycles. |
| Warning point | `budget - 2`. Default warning point is cycle `10`. |
| Hard halt | At `budget`, before dispatching another cycle. |
| Override | Allowed when requested or configured. Minimum override is `3`. |
| Invalid override | Values below `3` are rejected and the default is used. |

At the warning point, the lead records status and prepares an escalation if the
work is unlikely to finish.

At the hard halt, the lead stops dispatch and escalates to Project-Lead.
Project-Lead chooses one of:

| Choice | Meaning |
|---|---|
| Extend | Add a stated number of cycles and continue. |
| Finalise | Stop with current state and record the result. |
| Abandon | Stop the workstream and record why it is not proceeding. |

The lead does not silently exceed the budget.

## 4. Work-log entries

Every journal entry is prepended to the agent's journal.
Newest entries appear first.

Required format:

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

Required fields:

| Field | Rule |
|---|---|
| `cycle` | Current cycle number. |
| `timestamp` | ISO-8601 with explicit UTC offset. |
| `agentId` | Stable agent identity; matches the journal filename stem. |
| `taskId` | Stable task id from `plan.md`, or `cycle-<N>-observation`. |
| `taskName` | Human-readable task name. |
| `taskDescription` | One or two sentences describing the task. |
| `requirement` | Requirement id or specific requirement reference. |
| `workstream` | Full workstream id, for example `REQ-007/ws2`. |
| `status` | One of the allowed status values. |
| `Details` | Contains Done, Doing, Impediments, and ETA. |

Allowed `status` values:

| Status | Meaning |
|---|---|
| `in-progress` | Work continues next cycle. |
| `impeded` | The agent cannot proceed safely without a decision, permission, input, or dependency. |
| `done` | The assigned task is complete. |
| `observation` | Lead-written cycle summary or coordination note. |

The legacy schema used `blocked`. This schema uses `impeded` for consistency
with the glossary.

## 5. Journal writer rule

The lead writes the journal files.

Crew agents emit a work-log block in their response. They never write
`.scrum/<req>-<ws>/agents/*.md` themselves.

The lead parses the returned work-log block, validates required fields, and
prepends it to the correct journal.

Reason: one writer per file. Concurrent journal writes lose entries, interleave
content, and make cycle state unreliable.

If a crew agent omits the work-log block, the lead writes an `observation`
entry noting the missing log and uses the response content as evidence.

## 6. Plan

`plan.md` is written before dispatch.
It is frozen after signoff.
Changing it requires a new signoff by the dispatcher that owns the workstream,
and by Project-Lead when the change affects requirement scope, workstream scope,
file scope, budget, or acceptance.

Required fields:

| Field | Rule |
|---|---|
| Workstream | Full id, for example `REQ-007/ws2`. |
| Objective | One-sentence workstream goal. |
| Team composition | Agent identities, roles, and responsibilities. |
| Tasks | Table or list with the required task fields. |
| Cycle budget | Budget and warning point. |
| Definition of done | Workstream done condition. |
| Risks | Anticipated risks and impediments. |
| Lessons applied | Lessons from `.scrum/lessons.md` that influenced the plan. |

Task fields:

| Field | Rule |
|---|---|
| `id` | Stable id, for example `task-1`. |
| `name` | Short task name. |
| `description` | One or two sentences. |
| `requirement reference` | Requirement, story, acceptance criterion, or `n/a`. |
| `assigned agent` | `agentId` responsible for the task. |
| `changeScope` | `local` or `cross-cutting`. |
| `validationScope` | `targeted` or `full`. |
| `success criteria` | Concrete completion checks. |

Plan body structure:

```markdown
# Plan — REQ-NNN/ws<k>

## Workstream
## Objective
## Team composition
## Tasks
## Cycle budget
## Definition of done
## Risks
## Lessons applied
```

The plan does not duplicate requirement, spec, UX, or architecture documents.
It points to them.

## 7. Design

`design.md` is optional.

It is required when any of these are true:

| Signal | Meaning |
|---|---|
| Public contract change | API, CLI, schema, event, file format, or integration contract changes. |
| New component | A new module, service, package, or durable subsystem is introduced. |
| Cross-cutting change | More than one subsystem or package boundary is affected. |
| Data model change | Database, persisted state, migration, or serialized shape changes. |
| Concurrency-sensitive work | Shared state, locking, id allocation, merge behavior, or parallel workflows change. |
| Security-sensitive surface | Authentication, authorization, secret handling, or trust boundary changes. |
| Ambiguous build path | The team cannot implement safely from existing specs and architecture. |

Required fields when present:

| Field | Rule |
|---|---|
| Workstream | Full workstream id. |
| Requirement and spec links | Source documents being implemented. |
| Architectural overview | One to three paragraphs plus diagram when useful. |
| Components touched | Files, modules, services, and whether each is new, edited, or removed. |
| Interfaces and contracts | Signatures, endpoints, messages, schemas, CLI flags, or public surfaces. |
| Data model changes | Tables, migrations, on-disk formats, or `n/a`. |
| Alternatives considered | Options rejected and why. |
| Validation strategy | Tests, linters, checks, and acceptance mapping. |
| Risks and mitigations | Design-level risks and mitigations. |
| Open questions | Questions that must be resolved before implementation proceeds. |

`design.md` is frozen after signoff.
Changing it requires renewed signoff.

## 8. Validation scope

Validation scope is declared per task.

| Scope | Meaning | Required validation |
|---|---|---|
| `targeted` | Change is local to one component, package, or file set and does not alter shared contracts. | Tests, linters, type checks, or equivalent checks covering the touched area. |
| `full` | Change is cross-cutting, public, schema-level, or affects multiple subsystems. | Full project validation appropriate to the repository. |

Mapping:

| `changeScope` | Allowed `validationScope` |
|---|---|
| `local` | `targeted` |
| `cross-cutting` | `full` |

A local change validates targeted.
A cross-cutting change validates full.

This resolves the legacy contradiction: a developer was told to run targeted
validation while the definition of done demanded full validation.

Rule: the definition of done is that the validation appropriate to the declared
scope passes, plus the mechanical gate independently re-runs it.

A targeted task is done when targeted validation passes and the mechanical gate
independently re-runs targeted validation.
A full-scope task is done when full validation passes and the mechanical gate
independently re-runs full validation.

The mechanical gate does not expand scope on its own. It verifies the declared
scope and reports if the declaration is wrong.

## 9. Turn budgets and runaway control

Every dispatched agent carries a turn budget.

The dispatch states:

| Field | Rule |
|---|---|
| `turnBudget` | Maximum reasoning turns or tool-use turns for the dispatch. |
| `cycle` | Current cycle number. |
| `returnWhenNearBudget` | True. |
| `expectedWorkLog` | Required work-log block. |

When nearing the turn budget, the agent returns `in-progress`.
It records Done, Doing, Impediments, and ETA.
The lead re-dispatches the same task in the next cycle when appropriate.

Unbounded looping is prohibited.
An agent must return partial work, evidence, and a work-log entry rather than
continue indefinitely.

If a task repeatedly returns `in-progress` without new evidence, the lead narrows
the task, changes assignment, or escalates to Project-Lead.

## 10. Retrospective

`retrospective.md` is written when the workstream closes, whether by success,
finalise, or abandon.

Required fields:

| Field | Rule |
|---|---|
| Workstream | Full workstream id. |
| Outcome | `delivered`, `finalised`, or `abandoned`. |
| Cycle budget consumption | Used cycles of budget with pacing note. |
| What went well | Concrete moments where planning or execution worked. |
| What went poorly | Friction, miscommunication, wasted cycles, or weak evidence. |
| Impediments encountered and resolution | What prevented progress and how it was resolved or escalated. |
| Surprises | New constraints or behavior discovered mid-workstream. |
| Validation result | Validation scope and final result. |
| Handoff result | Durable artifacts created or requested. |
| Distilled lessons | One to three project-agnostic lessons for `.scrum/lessons.md`. |

Body structure:

```markdown
# Retrospective — REQ-NNN/ws<k>

## Outcome
## Cycle budget consumption
## What went well
## What went poorly
## Impediments encountered and resolution
## Surprises
## Validation result
## Handoff result
## Distilled lessons
```

The retrospective is machine-local. Durable conclusions move through the
handoff protocol into committed artifacts.

## 11. Lessons

`.scrum/lessons.md` is a cross-project FIFO scratchpad.

Rules:

| Rule | Contract |
|---|---|
| Cap | `5 KB` or `5120` bytes. |
| Order | Newest entries first. |
| Eviction | Evict whole entries from the bottom when over the cap. |
| Oversized single entry | Drop it rather than split it. |
| Scope | Project-agnostic only. |
| Source | Each lesson links to the source retrospective. |

Lesson shape:

```markdown
- <guidance>. **Why:** <short reason>. [[REQ-NNN-ws<k>]]
```

Good:

```markdown
- Confirm test discovery before claiming validation is complete. **Why:** mismatched runners can hide failing checks. [[REQ-007-ws1]]
```

Bad:

```markdown
- Rename `src/accounts/exporter.py` in the next task. **Why:** this project needs it. [[REQ-007-ws1]]
```

The good lesson applies to future workstreams.
The bad lesson is project-specific tasking and belongs in a durable handoff or
requirement update, not the lessons scratchpad.

## 12. Permission and safety

These operations are never performed unattended.
They are returned as impediments:

| Operation | Required response |
|---|---|
| Force-push | Return an impediment to Project-Lead. |
| History rewrite | Return an impediment to Project-Lead. |
| Deleting anything outside the declared file scope | Return an impediment to Project-Lead. |
| Reading secrets | Return an impediment to Project-Lead. |
| Writing secrets | Return an impediment to Project-Lead. |
| Anything that spends money | Return an impediment to Project-Lead. |

Routine safe operations are allowed when they are within the declared scope:

| Operation | Rule |
|---|---|
| Read files | Allowed within repository context and policy. |
| Write declared files | Allowed for the owning team and workstream. |
| Run targeted tests, linters, or builds | Allowed when matched to validation scope. |
| Inspect git status and diff | Allowed. |
| Create workstream commits | Allowed by Dev-Team within its branch and file scope. |
| Open pull request | Allowed by Dev-Team for its workstream. |

If an operation is not clearly allowed and could damage data, expose secrets,
rewrite history, exceed scope, or incur cost, the agent stops that operation and
returns an impediment.

## 13. Review cadence

Every team except Project-Lead has a duck.
The team's duck must pass the work before the team claims completion.

The cadence records:

| Record | Location |
|---|---|
| Dispatch and response | `.scrum/<req>-<ws>/agents/<agent-id>.md` |
| Review exchange | `.software-team/<REQ>/ledger.md` |
| Durable handoff | `.software-team/<REQ>/ledger.md` |
| Project-level synthesis | `.project-memory/`, written by Project-Lead |

Lead agents do not carry private review criteria.
They produce good work, send it to their duck, and address the returned findings.

## 14. Closeout

A workstream closes only after the lead has:

1. Collected every live agent or recorded why it ended.
2. Written final journal entries.
3. Written `retrospective.md`.
4. Updated `.scrum/lessons.md` with distilled project-agnostic lessons.
5. Produced a durable handoff in `.software-team/<REQ>/ledger.md`.
6. Returned any Project Memory, board, or lifecycle requests to Project-Lead.
7. Confirmed validation appropriate to the declared scope was run or explicitly
   recorded the impediment that prevented it.

Closeout does not by itself mean acceptance.
Project-Lead accepts delivered work against the requirement.
