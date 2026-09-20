---
type: Memory Conventions
title: Software Team — OKF Profile
description: The Open Knowledge Format v0.2 profile for all software-team document bundles.
generated: { by: software-team-project-lead/0.1.0, at: 2026-09-20T21:57:20Z }
status: stable
---

# Software Team — OKF Profile

This document defines how Open Knowledge Format (OKF) v0.2 applies to the
`software-team` package. It extends the Project Lead Project Memory profile to
all durable document bundles owned by the six teams. Readers are permissive.
Writers are precise. Provenance is never guessed.

## 1. Why OKF

All project documents are knowledge artifacts: typed, provenanced, citable, and
machine-checkable. OKF gives every team the same catalog, source, citation,
timestamp, trust, and status contract without making optional metadata a delivery
gate.

## 2. Bundles

Each bundle is rooted at its path and has a root `index.md` catalog.

| Bundle | Owner |
|---|---|
| `.project-memory/` | Project-Lead |
| `docs/requirements/` | Project-Lead |
| `docs/research/` | Research-Team |
| `docs/ux/` | UX-Team |
| `docs/specs/` | PM-Team |
| `docs/architecture/` | Architect-Team |

Ownership means write authority. Other teams read, cite, and request changes.
They do not edit a bundle they do not own.

## 3. Core OKF v0.2 rules

These rules carry forward the existing OKF v0.2 Project Lead profile.

### 3.1 Root `index.md`

Every bundle-root `index.md` carries only this frontmatter:

```yaml
---
okf_version: "0.2"
---
```

Its body is a grouped catalog of standard markdown links with one-line
descriptions.

```markdown
# Requirements

* [REQ-001: CSV export](/REQ-001-csv-export.md) - Approved requirement for CSV export.
```

Root catalogs do not carry lifecycle, priority, approval, board columns, review
state, or team progress.

### 3.2 Nested `index.md`

Nested `index.md` files carry no frontmatter.
Their bodies may be generated or sparse. Missing optional catalog detail is a
cleanup item only.

### 3.3 Reserved names

`index.md` and `log.md` are reserved names and must not be used for concept
documents.

`log.md` may carry frontmatter. The Project Lead profile writes:

```yaml
---
type: Log
title: Project Memory Update Log
---
```

Other bundle logs may use `type: Log` with a bundle-specific title. Log bodies
use bare date headings in descending order.

### 3.4 Concept documents

Every non-reserved concept document carries frontmatter with a non-empty `type`.

```yaml
---
type: Requirement
title: CSV export
description: Export filtered account data to CSV.
generated: { by: software-team-project-lead/0.1.0, at: 2026-09-20T21:57:20Z }
status: stable
---
```

`type` is the only always-required OKF key for non-reserved concepts.
Recommended keys are `title`, `description`, `tags`, `generated`, and `status`.
Unknown extra keys are preserved. Consumers tolerate them.

### 3.5 `generated`

`generated` is an object. `generated.by` is mandatory whenever `generated` is
present. `generated.at` records the last meaningful content change.

```yaml
generated: { by: software-team-pm/0.1.0, at: 2026-09-20T21:57:20Z }
```

Do not emit `generated` without `by`.

### 3.6 `sources` and `usage_window`

`sources[]` entries require `resource`. Optional keys are `id`, `title`,
`author`, `usage_count`, and `last_modified`. `sources[].author` uses the same
actor convention as `generated.by` and `verified.by`.

A shared `usage_window: { from:, to: }` belongs beside `sources`, never nested
inside a source entry.

```yaml
sources:
  - id: github-docs
    resource: https://docs.github.com/issues/tracking-your-work-with-issues
    title: GitHub Issues documentation
    author: team:github-docs
    usage_count: 3
    last_modified: 2026-09-01T00:00:00Z
usage_window: { from: 2026-09-01T00:00:00Z, to: 2026-09-20T23:59:59Z }
```

### 3.7 `verified`

`verified` may be a mapping:

```yaml
verified: { by: human:alex-owner, at: 2026-09-20T21:57:20Z }
```

It may also be a list:

```yaml
verified:
  - { by: human:alex-owner, at: 2026-09-20T21:57:20Z }
  - { by: process:github-merge, at: 2026-09-20T21:58:00Z }
```

A `verified.by` value starting with `human:` makes the concept human-reviewed.
Absence means unverified. A bare `verified:` key with no value is wrong and must
never be generated for drafts.

### 3.8 OKF `status`

`status` is OKF status only: `draft` | `stable` | `deprecated`. Absent means
effectively `stable`.

OKF `status` is not the same as a requirement lifecycle, issue state, board
column, workstream state, review outcome, or team handoff state. Those are
package-specific keys and must be named separately.

### 3.9 Timestamps and staleness

`stale_after` is an absolute ISO-8601 timestamp with explicit UTC offset.

All timestamp-valued keys use ISO-8601 with an explicit UTC offset, for example
`2026-09-19T21:30:00Z` or `2026-09-19T14:30:00-07:00`. This applies to
`generated.at`, `verified.at`, `stale_after`, `sources[].last_modified`,
`usage_window.from`, `usage_window.to`, and package extension timestamp keys.
Bare dates are permitted only as log headings: `## YYYY-MM-DD`.

### 3.10 Links

Use standard markdown links only. Do not generate Obsidian wikilinks.

Same-bundle links use bundle-root-relative paths beginning with `/`:

```markdown
[Risk](/wiki/risks/board-api-rate-limits.md)
```

Links leaving the bundle must not begin with `/`:

```markdown
[Requirement](../requirements/REQ-001-csv-export.md)
```

Absolute URLs are fine for links that must survive file moves.

### 3.11 Footnotes

Footnote labels must match a `sources[].id`. The label is the join key. Never use
positional labels that change when sources are reordered.

## 4. Type vocabulary

Type values are descriptive and producer-defined. Consumers tolerate unknown
values. Lint may ask for confirmation, but it does not reject a bundle for an
unfamiliar type.

| Path pattern | `type` value |
|---|---|
| `.project-memory/overview.md` | `Project Overview` |
| `.project-memory/log.md` and nested `log.md` | `Log` |
| `.project-memory/schema.md` | `Memory Conventions` |
| `.project-memory/project-link.md` | `Integration Link` |
| `.project-memory/requirements-register.md` | `Register` |
| `.project-memory/wiki/initiatives/*.md` | `Initiative` |
| `.project-memory/wiki/decisions/*.md` | `Decision` |
| `.project-memory/wiki/architecture/*.md` | `Architecture Note` |
| `.project-memory/wiki/stakeholders/*.md` | `Stakeholder` |
| `.project-memory/wiki/risks/*.md` | `Risk` |
| `.project-memory/wiki/glossary/*.md` | `Glossary Term` |
| `.project-memory/references/*.md` | `Reference` by default, or a sharper type |
| `docs/requirements/REQ-NNN-<slug>.md` | `Requirement` |
| `docs/requirements/README.md` | `Register` |
| `docs/requirements/_template.md` | `Template` |
| `docs/research/briefs/*.md` | `Research Brief` |
| `docs/research/findings/*.md` | `Research Finding` |
| `docs/specs/REQ-NNN/*.md` | `Feature Spec` |
| `docs/ux/REQ-NNN/*.md` | `UX Brief` |
| `docs/architecture/REQ-NNN/solution-architecture.md` | `Solution Architecture` |
| `docs/architecture/principles/*.md` | `Development Principle` |
| `docs/requirements/workstreams/*.md` | `Workstream` |
| `docs/research/reviews/*.md` | `Review Record` |
| `docs/specs/REQ-NNN/reviews/*.md` | `Review Record` |
| `docs/ux/REQ-NNN/reviews/*.md` | `Review Record` |
| `docs/architecture/reviews/*.md` | `Review Record` |
| `docs/**/team-charter.md` | `Team Charter` |
| `docs/**/handoffs/*.md` | `Handoff Record` |
| Any bundle-root `index.md` | no `type`; only `okf_version` is allowed |
| Any non-root `index.md` | no frontmatter |

## 5. Actor grammar and provenance

OKF actors use these forms.

| Actor kind | Grammar | Example |
|---|---|---|
| Agent or tool | `<producer>/<version>` | `software-team-pm/0.1.0` |
| Human | `human:<id>` | `human:alex-owner` |
| Team | `team:<id>` | `team:research-team` |
| Automation | `process:<id>` | `process:github-merge` |

The `human:` prefix is mandatory for hand-authored or human-confirmed content.

### 5.1 Package actors

Agent actors: `software-team-project-lead/0.1.0`,
`software-team-research/0.1.0`, `software-team-research-duck/0.1.0`,
`software-team-architect/0.1.0`, `software-team-architect-duck/0.1.0`,
`software-team-pm/0.1.0`, `software-team-pm-duck/0.1.0`,
`software-team-dev/0.1.0`, `software-team-dev-duck/0.1.0`,
`software-team-ux/0.1.0`, and `software-team-ux-duck/0.1.0`.

Automation actors: `process:software-team-sync`,
`process:software-team-bootstrap`, `process:software-team-migration`, and
`process:github-merge`.

Team actors: `team:project-lead`, `team:research-team`,
`team:architect-team`, `team:pm-team`, `team:dev-team`, and `team:ux-team`.

### 5.2 Writer, owner, and workstream

`generated.by` names the actor that wrote the file. When the responsible
decision-maker differs, record it separately with `owner:`:

```yaml
owner: team:architect-team
```

When the artifact belongs to a delivery slice, record it separately with
`workstream:`:

```yaml
workstream: WS-REQ-001-export-download
```

Do not overload `generated.by` with ownership or responsibility. That would make
provenance dishonest. A process can migrate a file owned by Architect-Team. A
human can verify a document written by an agent. Each fact belongs in its own key.

### 5.3 Honesty rules

- Never fabricate human verifiers, sources, or actors.
- Omit `verified` when no real verifier exists.
- Omit `sources` when no real source was used.
- Use `process:software-team-migration` when historical authorship is genuinely unknown.
- Preserve unknown frontmatter keys unless a documented migration rule rewrites them.
- Say `unknown` in the body when the evidence is unknown.

## 6. Citation discipline

Every load-bearing claim carries a footnote whose label matches a `sources[].id`.
This is mandatory for Research-Team and expected for every team when claims rely
on external evidence, prior decisions, requirements, research, or other bundle
artifacts.

Claims that need citations include external API behavior, stakeholder intent,
trade-offs from research, architecture constraints, acceptance criteria copied
from requirements, and UX assumptions. Local headings and definitions introduced
by the current document usually do not need citations.

### 6.1 Worked citation example

```markdown
---
type: Research Finding
title: Native sub-issues support requirement roll-up
description: GitHub native sub-issues can represent feature and story hierarchy under a requirement issue.
owner: team:research-team
generated: { by: software-team-research/0.1.0, at: 2026-09-20T21:57:20Z }
status: stable
sources:
  - id: github-sub-issues
    resource: https://docs.github.com/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues
    title: Adding sub-issues
    author: team:github-docs
    usage_count: 4
    last_modified: 2026-09-01T00:00:00Z
usage_window: { from: 2026-09-01T00:00:00Z, to: 2026-09-20T23:59:59Z }
---

# Finding

GitHub native sub-issues model parent-child issue relationships, so a Requirement
issue can own Feature and Story child issues without a custom hierarchy
table.[^github-sub-issues]

[^github-sub-issues]: GitHub documents sub-issues as native parent-child issue relationships.
```

## 7. Conformance checking

Conformance is ADVISORY. Reports propose fixes and identify risk. They never
reject a bundle or block a phase for an optional omission.

| Check | Posture |
|---|---|
| Missing parseable frontmatter or missing/empty `type` on a non-reserved `.md` file | Advisory |
| Illegal frontmatter on an `index.md` | Advisory |
| `log.md` not grouped as bare descending `## YYYY-MM-DD` sections | Advisory; safe auto-fix may be offered |
| Unknown `type` value | Low priority advisory |
| Unknown extra frontmatter keys | Not a finding |
| Absent internal link target | Advisory; may be future knowledge |
| Directory lacking `index.md` | Low priority advisory |
| Timestamp-valued field lacking explicit UTC offset | Advisory |
| `usage_window` nested inside a source entry | High priority advisory |
| Footnote id with no matching `sources[].id` | Advisory |
| `generated` present without `by` | Advisory |

## 8. Worked frontmatter examples

These are complete frontmatter blocks. Bodies still need headings, content,
links, and citations as appropriate.

### 8.1 Research Finding

```yaml
---
type: Research Finding
title: Native sub-issues support delivery hierarchy
description: GitHub native sub-issues can represent requirement, feature, and story hierarchy.
owner: team:research-team
generated: { by: software-team-research/0.1.0, at: 2026-09-20T21:57:20Z }
status: stable
sources:
  - id: github-sub-issues
    resource: https://docs.github.com/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues
    title: Adding sub-issues
    author: team:github-docs
usage_window: { from: 2026-09-01T00:00:00Z, to: 2026-09-20T23:59:59Z }
---
```

### 8.2 Feature Spec

```yaml
---
type: Feature Spec
title: REQ-001 — CSV export download
description: Feature specification for downloading filtered account data as CSV.
owner: team:pm-team
workstream: WS-REQ-001-export-download
generated: { by: software-team-pm/0.1.0, at: 2026-09-20T21:57:20Z }
status: draft
---
```

### 8.3 UX Brief

```yaml
---
type: UX Brief
title: REQ-001 — CSV export experience
description: User flow and interaction design for exporting filtered account data.
owner: team:ux-team
workstream: WS-REQ-001-export-download
generated: { by: software-team-ux/0.1.0, at: 2026-09-20T21:57:20Z }
status: stable
---
```

### 8.4 Solution Architecture

```yaml
---
type: Solution Architecture
title: REQ-001 — CSV export solution architecture
description: Technical architecture for CSV export delivery.
owner: team:architect-team
workstream: WS-REQ-001-export-download
generated: { by: software-team-architect/0.1.0, at: 2026-09-20T21:57:20Z }
status: stable
---
```

### 8.5 Development Principle

```yaml
---
type: Development Principle
title: Stream export responses
description: Export implementations must stream large file responses instead of buffering complete files in memory.
owner: team:architect-team
generated: { by: software-team-architect/0.1.0, at: 2026-09-20T21:57:20Z }
status: stable
---
```

### 8.6 Workstream

```yaml
---
type: Workstream
title: WS-REQ-001-export-download
description: Delivery slice for building the CSV export download path.
owner: team:project-lead
workstream: WS-REQ-001-export-download
generated: { by: software-team-project-lead/0.1.0, at: 2026-09-20T21:57:20Z }
status: stable
---
```
