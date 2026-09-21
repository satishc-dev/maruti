---
type: Memory Conventions
title: Software Team — Project Memory Schema
description: Project Memory bundle, ownership, generated projections, and concurrency rules for the software-team package.
status: stable
---

# Project Memory Schema

This contract defines `.project-memory/` for the `software-team` package.
It carries forward the Project Memory bundle used by Project-Lead and adapts it
for six concurrent teams: Project-Lead, Research-Team, Architect-Team, PM-Team,
Dev-Team, and UX-Team.

Project Memory is durable project context. It is committed to the repository.
It is readable by every team. It is written only by Project-Lead.

Where this contract and `ROLES.md` disagree, `ROLES.md` wins.

## 1. Bundle root

Project Memory is an OKF v0.2 bundle rooted at `.project-memory/`.
Open `.project-memory/` as the Obsidian vault when using Obsidian.
If the whole repository is opened as a vault, use standard markdown links and
explicit relative paths.

The bundle tree is fixed.

```text
.project-memory/
├── index.md
├── log.md
├── overview.md
├── schema.md
├── project-link.md
├── requirements-register.md
├── references/
│   └── index.md
└── wiki/
    ├── initiatives/
    │   └── index.md
    ├── decisions/
    │   └── index.md
    ├── architecture/
    │   └── index.md
    ├── stakeholders/
    │   └── index.md
    ├── risks/
    │   └── index.md
    ├── glossary/
    │   └── index.md
    └── workstreams/
        └── index.md
```

No other root files are reserved. Concept pages may be added under
`references/` and the `wiki/` subdirectories.

## 2. OKF profile

Project Memory conforms to `OKF-PROFILE.md`.

Rules that matter most:

| Rule | Contract |
|---|---|
| Root `index.md` | Carries only `okf_version: "0.2"`. |
| Nested `index.md` | Carries no frontmatter. |
| Non-reserved concept document | Carries non-empty `type`. |
| `status` | OKF document trust only: `draft`, `stable`, `deprecated`. |
| `generated.by` | Actor, not owner. Use `owner:` when ownership matters. |
| Links | Standard markdown links only. No Obsidian wikilinks. |
| Same-bundle link | Begins with `/`, resolved from `.project-memory/`. |
| Link leaving bundle | Does not begin with `/`. |
| Bare dates | Allowed only as `log.md` headings. |

Type values are the type vocabulary in `OKF-PROFILE.md`.

## 3. Reserved files

Reserved files have fixed purpose, fixed frontmatter, and fixed body structure.

### 3.1 `.project-memory/index.md`

Type: bundle-root catalog. It has no `type`.

Exact frontmatter:

```yaml
---
okf_version: "0.2"
---
```

Body structure:

```markdown
# Project Memory

## Core

* [Overview](/overview.md) - Current project synthesis.
* [Update log](/log.md) - Chronological update log.
* [Memory schema](/schema.md) - Bundle conventions.
* [GitHub Project link](/project-link.md) - Linked Project configuration.
* [Requirements register](/requirements-register.md) - Requirement mirror.

## References

* [References](/references/index.md) - External and mirrored source material.

## Wiki

* [Initiatives](/wiki/initiatives/index.md) - Initiative and epic context.
* [Decisions](/wiki/decisions/index.md) - Durable decisions.
* [Architecture](/wiki/architecture/index.md) - Architecture knowledge.
* [Stakeholders](/wiki/stakeholders/index.md) - Stakeholder context.
* [Risks](/wiki/risks/index.md) - Risks and open questions.
* [Glossary](/wiki/glossary/index.md) - Domain terms.
* [Workstreams](/wiki/workstreams/index.md) - Workstream context.
```

`index.md` is a generated projection. It is regenerated, never hand-edited.

### 3.2 `.project-memory/log.md`

Type: `Log`.

Exact frontmatter:

```yaml
---
type: Log
title: Project Memory Update Log
---
```

Body structure:

```markdown
# Project Memory Update Log

## YYYY-MM-DD

- **EntryType**: [YYYY-MM-DDTHH:MM:SSZ] <actor> — text.
```

Allowed `EntryType` values:

| Entry type | Use |
|---|---|
| Requirement | Requirement capture, update, approval-state change, or delivery-state change. |
| Approval | Stakeholder approval or acceptance. |
| Handoff | Handoff between teams. |
| Sync | Repository, board, register, or projection reconciliation. |
| Lint | Conformance report or safe normalization. |
| Delivery | Pull request, merge, acceptance, or release event. |
| Decision | Durable project decision. |
| Bootstrap | Repository or bundle setup event. |
| Research | Research question, finding, or conclusion filed. |
| Architecture | Architecture note, ADR, or development principle filed. |
| Principle | Binding development principle recorded or revised. |
| Escalation | Decision returned to Project-Lead because a team cannot proceed. |
| Debt | Known shortfall accepted and recorded explicitly. |

`log.md` is append-oriented and normalized. It is not a free-form journal.

### 3.3 `.project-memory/overview.md`

Type: `Project Overview`.

Exact frontmatter:

```yaml
---
type: Project Overview
title: <Project name> — Overview
description: <one-sentence synthesis>
generated: { by: software-team-project-lead/0.1.0, at: <ISO-8601 timestamp> }
status: stable
---
```

Body structure:

```markdown
# <Project name> — Overview

## Thesis
<Current one-paragraph project thesis.>

## Current status
<Generated status synthesis.>

## Active requirements
<Generated summary from docs/requirements/.>

## Active workstreams
<Generated summary from canonical workstream records.>

## Key decisions
<Generated links to current decision records.>

## Current risks
<Generated links to current risks and escalations.>
```

The status sections are generated projections. The thesis may be edited by
Project-Lead when new durable context changes the project narrative.

### 3.4 `.project-memory/schema.md`

Type: `Memory Conventions`.

Exact frontmatter:

```yaml
---
type: Memory Conventions
title: Project Memory Conventions (OKF v0.2 profile)
description: Distilled conventions this Project Memory bundle follows.
generated: { by: software-team-project-lead/0.1.0, at: <ISO-8601 timestamp> }
status: stable
---
```

Body structure:

```markdown
# Project Memory Conventions

## OKF profile
<Pointer to OKF-PROFILE.md and local conventions.>

## Bundle structure
<Tree and reserved file rules.>

## Ownership
<Project-Lead single-writer rule.>

## Projections
<Generated file rules.>

## Concurrency
<Race controls and merge rules.>
```

This file documents the working conventions applied to the bundle instance.

### 3.5 `.project-memory/project-link.md`

Type: `Integration Link`.

Exact frontmatter:

```yaml
---
type: Integration Link
title: GitHub Project Link
description: Linked GitHub Project board configuration.
generated: { by: software-team-project-lead/0.1.0, at: <ISO-8601 timestamp> }
status: stable
---
```

Body structure:

```markdown
# GitHub Project Link

<Field list defined by GITHUB-INTEGRATION.md.>
```

The field list is not duplicated here. `GITHUB-INTEGRATION.md` is the authority
for owner, project number, Project URL, Project id, Status field id, Status
options, and requirement issue type.

### 3.6 `.project-memory/requirements-register.md`

Type: `Register`.

Exact frontmatter:

```yaml
---
type: Register
title: Requirements Register (Project Memory mirror)
description: Mirror of docs/requirements/ with lifecycle, board, and delivery links.
generated: { by: software-team-project-lead/0.1.0, at: <ISO-8601 timestamp> }
status: stable
---
```

Body structure:

```markdown
# Requirements Register

| ID | Title | Lifecycle | Priority | Version | Approved | Requirement issue | Project item | Workstreams | Doc |
|---|---|---|---|---|---|---|---|---|---|
```

The register mirrors `docs/requirements/`. It never replaces requirement
documents and never carries facts that are absent from canonical sources.

### 3.7 `.project-memory/references/index.md`

Type: nested catalog. It has no `type`.

Exact frontmatter: none.

Body structure:

```markdown
# References

* [Title](file.md) - One-line description.
```

The file is generated from reference concept pages.

### 3.8 `.project-memory/wiki/initiatives/index.md`

Type: nested catalog. It has no `type`.

Exact frontmatter: none.

Body structure:

```markdown
# Initiatives

* [Title](file.md) - One-line description.
```

The file is generated from initiative concept pages.

### 3.9 `.project-memory/wiki/decisions/index.md`

Type: nested catalog. It has no `type`.

Exact frontmatter: none.

Body structure:

```markdown
# Decisions

* [Title](file.md) - One-line description.
```

The file is generated from decision concept pages.

### 3.10 `.project-memory/wiki/architecture/index.md`

Type: nested catalog. It has no `type`.

Exact frontmatter: none.

Body structure:

```markdown
# Architecture

* [Title](file.md) - One-line description.
```

The file is generated from architecture-note concept pages.

### 3.11 `.project-memory/wiki/stakeholders/index.md`

Type: nested catalog. It has no `type`.

Exact frontmatter: none.

Body structure:

```markdown
# Stakeholders

* [Title](file.md) - One-line description.
```

The file is generated from stakeholder concept pages.

### 3.12 `.project-memory/wiki/risks/index.md`

Type: nested catalog. It has no `type`.

Exact frontmatter: none.

Body structure:

```markdown
# Risks

* [Title](file.md) - One-line description.
```

The file is generated from risk concept pages.

### 3.13 `.project-memory/wiki/glossary/index.md`

Type: nested catalog. It has no `type`.

Exact frontmatter: none.

Body structure:

```markdown
# Glossary

* [Title](file.md) - One-line description.
```

The file is generated from glossary-term concept pages.

### 3.14 `.project-memory/wiki/workstreams/index.md`

Type: nested catalog. It has no `type`.

Exact frontmatter: none.

Body structure:

```markdown
# Workstreams

* [Title](file.md) - One-line description.
```

The file is generated from workstream concept pages and canonical workstream
records.

## 4. Ownership and writers

Project-Lead is the sole writer of `.project-memory/`.

Other teams do not edit Project Memory. They contribute by proposing changes
through the handoff protocol. A handoff may request a memory entry, a wiki page,
a register refresh, a decision record, a risk record, a workstream note, or a
log entry.

Reason: Project Memory contains cross-cutting summaries with no safe merge
semantics. Two teams can both be correct locally and still produce a wrong
combined summary. A single writer serializes interpretation.

Read access is unrestricted. Every team may cite Project Memory.

## 5. Generated projections

Hand-edited shared summaries are exactly what race under concurrency.
Generated projections are therefore regenerated from canonical documents.

| Projection | Source of truth | Regeneration rule |
|---|---|---|
| `.project-memory/requirements-register.md` | `docs/requirements/REQ-*.md`, requirement `links`, canonical workstream records, and `GITHUB-INTEGRATION.md` for board fields. | Regenerate after any requirement lifecycle, link, priority, version, approval, workstream, or board projection change. Do not edit rows by hand. |
| `.project-memory/index.md` | Fixed bundle tree plus frontmatter from root concept files and nested catalog paths. | Regenerate after bootstrap, migration, file add, file remove, or title/description change. Keep only the root OKF frontmatter. |
| Nested `index.md` files | Child concept pages in the same directory. | Regenerate alphabetically or by documented local ordering after child page add, remove, title change, or description change. Carry no frontmatter. |
| `.project-memory/overview.md` status sections | Requirement documents, lifecycle mapping in `LIFECYCLE.md`, workstream records, delivery ledger entries, decision pages, risk pages, and current board projection. | Regenerate the status sections during sync and after lifecycle transitions. Preserve the thesis unless Project-Lead deliberately revises it. |

Projection files may be deleted and recreated from source. Their content is not
canonical evidence.

## 6. Requirements register

The Project Memory requirements register is a mirror.

Required columns:

| Column | Source |
|---|---|
| ID | Requirement frontmatter `id`. |
| Title | Requirement frontmatter `title`. |
| Lifecycle | Requirement frontmatter `lifecycle`. |
| Priority | Requirement frontmatter `priority`, when present. |
| Version | Requirement frontmatter `version`. |
| Approved | Requirement frontmatter `approved_at` and `approved_by`. |
| Requirement issue | Requirement frontmatter `requirement_issue`. |
| Project item | Requirement frontmatter `links.project_item`. |
| Workstreams | Canonical workstream records for the requirement. |
| Doc | Link to `docs/requirements/REQ-NNN-<slug>.md`. |

The register mirrors. It never replaces `docs/requirements/`.
If the register and a requirement document disagree, regenerate the register.

## 7. `REQ-NNN` allocation

Project-Lead is the sole serialized allocator of `REQ-NNN` identifiers.

Allocation procedure:

1. Project-Lead fetches and reads the current default-branch state.
2. Project-Lead scans `docs/requirements/REQ-*.md`.
3. Project-Lead extracts every `REQ-NNN` from filenames and frontmatter.
4. Project-Lead chooses the next unused zero-padded number.
5. Project-Lead creates exactly one new requirement document with that id.
6. Project-Lead writes the id into filename, frontmatter, change log, and any
   initial ledger or board request.
7. Project-Lead persists the allocation before allocating another id.
8. If a write collides with a newer requirement, Project-Lead re-reads and
   repeats the allocation. It never reuses the stale number.

Specialist teams never choose requirement ids. They refer to ids already
allocated by Project-Lead.

## 8. Log normalization

`log.md` uses this exact body shape:

```markdown
# Project Memory Update Log

## YYYY-MM-DD

- **EntryType**: [YYYY-MM-DDTHH:MM:SSZ] <actor> — text.
```

Headings are bare dates in descending order.
Bullets use only the entry types listed in §3.2.
The bullet text carries actor and timestamp so union-merged entries retain
identity.

Normalization algorithm:

1. Split preamble at the first line matching `^## `.
2. Preserve the preamble byte-for-byte.
3. Convert legacy headings into bare-date sections and bullets.
4. Group equal dates into one section.
5. Preserve multiline bullet blocks until the next bullet or section boundary.
6. Deduplicate identical bullet blocks after trimming outer whitespace.
7. Keep surviving bullets for the same date in first-seen order.
8. Sort date sections descending by `YYYY-MM-DD`.
9. Emit the preserved preamble, each `## YYYY-MM-DD` heading, one blank line,
   the ordered bullets, and one blank line before the next date.

The algorithm MUST be idempotent. A second run on its own output produces
byte-identical output.

Required `.gitattributes` entries:

```gitattributes
.project-memory/log.md merge=union
.software-team/**/ledger.md merge=union
```

Normalization runs immediately after any merge that may have concatenated log
or ledger entries.

## 9. Concurrency countermeasures

| Hazard | Countermeasure |
|---|---|
| Single-writer assumption from the legacy package | Project-Lead is the sole writer of `.project-memory/`; other teams propose changes through handoff envelopes. |
| `REQ-NNN` allocation races | Project-Lead is the sole serialized allocator. It scans existing ids, chooses the next unused id, persists it before the next allocation, and retries on collision. |
| Lifecycle last-write-wins | Requirement transitions use compare-and-swap with `version`; see `LIFECYCLE.md`. Stale writes are aborted and re-evaluated. |
| Union-merged log lacking identity | Each log bullet carries timestamp and actor inside the text. Normalization groups, sorts, and deduplicates without erasing identity. |
| Shared summaries | Root `index.md`, nested indexes, requirements register, and overview status sections are generated projections. They are regenerated from canonical sources. |
| Missing team namespace | Durable records carry `workstream` and `owner` keys when the artifact belongs to a delivery slice or team-owned fact. |

## 10. Workstream memory

Workstream concept pages live under `.project-memory/wiki/workstreams/` when a
workstream needs durable synthesis.

Recommended frontmatter:

```yaml
---
type: Workstream
title: REQ-NNN/ws<k> — <title>
description: Durable context for one delivery workstream.
owner: team:project-lead
workstream: REQ-NNN/ws<k>
generated: { by: software-team-project-lead/0.1.0, at: <ISO-8601 timestamp> }
status: stable
---
```

Body structure:

```markdown
# REQ-NNN/ws<k> — <title>

## Scope
<Declared workstream scope.>

## File scope
<Declared write scope.>

## Dependencies
<Other workstreams or artifacts required first.>

## Current state
<Generated or Project-Lead-authored synthesis.>

## Handoffs
<Links to ledger entries and artifacts.>

## Decisions and risks
<Links to decision and risk pages.>
```

The canonical workstream record remains the record defined by `PARALLELISM.md`
and the requirement documents. The wiki page is a durable synthesis.

## 11. Handoff proposals

Teams propose Project Memory changes in handoff envelopes.

Minimum proposal fields:

```yaml
memory_proposals:
  - target: ".project-memory/wiki/risks/<slug>.md"
    action: create | update | append-log | regenerate
    owner: team:project-lead
    workstream: "REQ-NNN/ws<k>"
    reason: "<why this belongs in Project Memory>"
    evidence:
      - "<path or URL>"
    proposed_text: |
      <text for Project-Lead to accept, revise, or reject>
```

Project-Lead may accept, revise, reject, or defer a proposal.
The proposing team does not write the target file.

## 12. Ephemeral versus committed state

Committed:

| Path | Purpose |
|---|---|
| `.project-memory/` | Durable project context and cross-cutting synthesis. |
| `.software-team/` | Durable ledgers, handoff envelopes, receipts, and board requests. |

Machine-local and gitignored:

| Path | Purpose |
|---|---|
| `.scrum/` | Working cadence journals, plans, retrospectives, and local lessons. |
| `.worktrees/` | Per-workstream git worktrees and local forensic state. |

Consequence: every durable handoff must be represented in a committed artifact.
Machine-local state vanishes when a session, runner, or workstation is gone.
If the handoff matters after the run, it belongs in `.software-team/` and, when
it changes project knowledge, in `.project-memory/` through Project-Lead.
