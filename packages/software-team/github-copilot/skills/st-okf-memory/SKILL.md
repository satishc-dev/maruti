---
name: st-okf-memory
description: 'Use when any software-team agent reads or writes package documents, OKF bundles, Project Memory, team artifacts, ledgers, or document links; apply ownership, frontmatter, timestamp, citation, actor, and honesty rules before editing or proposing changes.'
---

# st-okf-memory

Use this skill any time you read or write a document in this package.
For full detail, read `docs/OKF-PROFILE.md`, `docs/MEMORY-SCHEMA.md`, `docs/ARTIFACTS.md`, and `docs/ROLES.md`.

## Core rule

Read freely.
Write only documents your team owns.
If you need a change to a document you do not own, propose it to the owner — do not edit it.
The ledger is append-only; every team appends its own entries and rewrites no other entry.

## Six OKF bundles

| Bundle | Owner | Purpose |
|---|---|---|
| `.project-memory/` | Project-Lead | Durable project context, decisions, risks, references, registers. |
| `docs/requirements/` | Project-Lead | Requirements and lifecycle source of truth. |
| `docs/research/` | Research-Team | Research briefs and cited findings. |
| `docs/ux/` | UX-Team | UX briefs and withdrawal records. |
| `docs/specs/` | PM-Team | Feature specs, stories, acceptance criteria. |
| `docs/architecture/` | Architect-Team | Solution architecture, ADRs, development principles. |

## Per-path ownership map

| Path pattern | Owner | Rule |
|---|---|---|
| `.project-memory/**` | Project-Lead | Other teams propose changes through handoff. |
| `docs/requirements/REQ-NNN-<slug>.md` | Project-Lead | Requirement source of truth. |
| `docs/requirements/README.md` | Project-Lead | Requirement register. |
| `docs/requirements/index.md` | Project-Lead | Bundle catalog. |
| `docs/research/<topic>/index.md` | Research-Team | Nested catalog, no frontmatter. |
| `docs/research/<topic>/brief.md` | Research-Team | Research brief. |
| `docs/research/<topic>/<finding>.md` | Research-Team | Research finding. |
| `docs/ux/REQ-NNN/<feature>.md` | UX-Team | UX brief or withdrawal. |
| `docs/specs/REQ-NNN/<feature>.md` | PM-Team | Feature spec. |
| `docs/architecture/REQ-NNN/solution.md` | Architect-Team | Solution architecture. |
| `docs/architecture/decisions/ADR-NNN-<slug>.md` | Architect-Team | ADR. |
| `docs/architecture/principles/<slug>.md` | Architect-Team | Development principle. |
| `.software-team/REQ-NNN/workstreams.md` | Project-Lead | Workstream record. |
| `.software-team/REQ-NNN/ledger.md` | All teams append | Append only; each team owns its entries. |

## Index rules

| File | Frontmatter | Body |
|---|---|---|
| Bundle-root `index.md` | Only `okf_version: "0.2"`. | Grouped catalog of markdown links. |
| Nested `index.md` | None. | Sparse or generated catalog. |
| Concept document | Non-empty `type` is required. | Schema-defined content. |

Do not put lifecycle, priority, approval, board state, review state, or progress in a bundle-root `index.md`.
Do not put frontmatter in a nested `index.md`.
Do not use reserved names `index.md` or `log.md` for concept documents.

## Concept frontmatter

Every non-reserved concept document has a non-empty `type`.
Recommended keys are `title`, `description`, `tags`, `generated`, and `status`.
Unknown extra keys are preserved unless a documented migration rule rewrites them.
Use `owner:` for accountability.
Use `workstream:` when an artifact belongs to a delivery slice.
Do not overload `generated.by` with ownership.

## `generated` rule

If `generated` is present, `generated.by` is mandatory.
`generated.by` names the writer.
`generated.at` records the last meaningful content change.
Use package actors from `docs/OKF-PROFILE.md`.
Use ISO-8601 timestamps with explicit UTC offsets.

## Timestamps

Every timestamp-valued field uses an explicit UTC offset.
Valid examples are `2026-09-20T21:57:20Z` and `2026-09-20T14:57:20-07:00`.
Bare dates are allowed only as log headings: `## YYYY-MM-DD`.
Apply this to generated, verified, stale, source, usage window, lifecycle, and package extension timestamps.

## Links

Use standard markdown links only.
Never use wikilinks.
Same-bundle links begin with `/` and resolve from the bundle root.
Links leaving the bundle do not begin with `/`.
Absolute URLs are allowed when stability requires them.

## Footnotes and sources

Footnote labels must match `sources[].id` exactly.
The label is the join key.
Do not use positional footnotes.
Every load-bearing claim based on a source carries a matching footnote.
Omit `sources` when no real source was used.

## Actor grammar

| Actor kind | Grammar | Example |
|---|---|---|
| Agent or tool | `<producer>/<version>` | `software-team-architect/0.1.0` |
| Human | `human:<id>` | `human:alex-owner` |
| Team | `team:<id>` | `team:architect-team` |
| Automation | `process:<id>` | `process:github-merge` |

Use `human:` only for a real human verifier or approver.
Use `process:software-team-migration` only when historical authorship is genuinely unknown.

## Honesty rules

Never fabricate a human verifier.
Never fabricate a source.
Never fabricate an actor.
Never cite a document you did not read.
Never present speculation as evidence.
Omit `verified` when no real verifier exists.
Omit `sources` when no real source exists.
Write `unknown` in the body when evidence is unknown.
Preserve unknown frontmatter keys unless a documented rule changes them.

## OKF status

OKF `status` is document trust only.
It is not delivery progress.
Allowed values are `draft`, `stable`, and `deprecated`.
Absent means effectively `stable`.
Do not use OKF `status` for lifecycle, board columns, review state, workstream state, or handoff state.

| System | Field | Owner | Meaning |
|---|---|---|---|
| Delivery lifecycle | `lifecycle` | Project-Lead | Delivery funnel. |
| OKF trust | `status` | Document owner | Document trust. |
| Board projection | GitHub Project `Status` | Project-Lead | Visible board column. |

When board and documents disagree, documents win.
The board is corrected from documents, never the reverse.

## Editing checklist

Before editing, identify the owner.
Confirm the path is yours.
Read the governing schema.
Preserve valid frontmatter and unknown keys.
Use honest `generated.by` and `generated.at`.
Use markdown links only.
Synchronize footnotes with `sources[].id`.
Keep OKF `status` separate from lifecycle.

## Proposal checklist

If the document is not yours, do not edit it.
Send a handoff or memory proposal to the owner.
Name the target path, action, owner, reason, evidence, and proposed text.
Let the owner accept, revise, reject, or defer.
