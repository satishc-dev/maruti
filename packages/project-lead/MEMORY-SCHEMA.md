# Project Lead — Memory & Requirements Schema

This document is the binding reference for the on-disk artifacts the Project Lead
maintains. It defines the `.project-memory/` Project Memory bundle, the official
`docs/requirements/` requirement bundle, the requirement lifecycle and approval
contract, and the GitHub Project / issue mapping. The `project-lead` Claude Code
skill and the `Project-Lead` Copilot agent both implement exactly what is
described here.

Project Memory and requirement documents are rebased on the
[Open Knowledge Format (OKF) v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)
as read at spec SHA `ad30107c`. The Lead uses OKF as a permissive markdown
interchange format, not as a rejecting validator.

Two design rules hold everywhere:

1. **The repo is canonical for requirements.** Requirement documents live in
   `docs/requirements/` (versioned, PR-reviewable). `.project-memory/` only
   *references* them — it never becomes a second source of truth.
2. **The Lead owns the bookkeeping.** It writes and maintains every file under
   `.project-memory/`; the human curates sources, makes decisions, and approves.

---

## 1. Project Memory (`.project-memory/`)

Project Memory is an OKF v0.2 bundle rooted at `.project-memory/`: a pure
markdown, Obsidian-readable compounding wiki. Open `.project-memory/` itself as
the Obsidian vault so Obsidian's vault root and OKF's bundle root match. If the
whole repo is opened as a vault, configure links as relative paths to files.

```
.project-memory/
├── index.md                   # bundle root catalog; only okf_version frontmatter
├── log.md                     # OKF-shaped chronology, normalized newest-first
├── overview.md                # evolving project thesis / current-state synthesis
├── schema.md                  # conventions + workflows the Lead follows
├── project-link.md            # linked GitHub Project and Status field IDs
├── requirements-register.md   # mirror that references docs/requirements/*
├── references/                # OKF convention for mirrored external material
│   └── index.md               # no-frontmatter local catalog; keeps folder committed
└── wiki/
    ├── initiatives/           # one page per initiative/epic
    │   └── index.md           # no-frontmatter local catalog; keeps folder committed
    ├── decisions/             # decision records
    │   └── index.md
    ├── architecture/          # accumulated system & architecture knowledge
    │   └── index.md
    ├── stakeholders/          # stakeholder context and preferences
    │   └── index.md
    ├── risks/                 # risks and open questions
    │   └── index.md
    └── glossary/              # domain terms
        └── index.md
```

### 1.1 Type vocabulary

OKF requires a non-empty `type` in every non-reserved concept document. Type
values are producer-defined, descriptive, and self-explanatory. Project Lead uses
this vocabulary consistently:

| File / directory | `type` value |
|---|---|
| `.project-memory/overview.md` | `Project Overview` |
| `.project-memory/log.md` and nested `log.md` | `Log` (recommended) |
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
| Any bundle-root `index.md` | no `type`; only `okf_version` is allowed |
| Any non-root `index.md` | no frontmatter |

Consumers MUST tolerate unknown `type` values. Lint may ask the stakeholder to
confirm an unusual value, but it never rejects the bundle for it.

### 1.2 Frontmatter families

`type` is the only always-required OKF key for non-reserved concepts. The Lead
SHOULD include these families when it knows the values:

- **Readable metadata:** `title`, `description`, and `tags` for navigation.
- **Provenance:** `generated: { by: <actor>, at: <ISO-8601 datetime> }`.
  `generated.by` is required when `generated` is present. `generated.at` records
  the last meaningful content change.
- **Sources:** `sources:` entries with required `resource`, optional `id`,
  `title`, `author`, `usage_count`, and `last_modified`. `sources[].author`
  follows the same OKF actor convention as `generated.by` and `verified[].by`;
  for example, use `team:github-docs` for GitHub documentation authorship, not a
  bare `GitHub` string. When multiple sources share a time range, put
  `usage_window` as a sibling of `sources`, not under an entry. A source entry
  may override the shared window when needed.
- **Per-claim citations:** body footnotes use the same label as `sources[].id`.
  The label is the join key; do not use positional labels that change when the
  source list is reordered.
- **Trust:** `verified` may be a bare mapping or a list. Any verifier whose
  `by` value starts with `human:` makes the concept human-reviewed. Absence of
  `verified` is valid and means unverified.
- **Lifecycle:** OKF `status` is only `draft`, `stable`, or `deprecated`;
  absent means `stable`. `stale_after` is an absolute ISO-8601 datetime with an
  explicit UTC offset.

Every timestamp-valued key (`generated.at`, `verified.at`, `stale_after`,
`sources[].last_modified`, `usage_window.from`, `usage_window.to`) uses ISO-8601
with an explicit UTC offset, for example `2026-09-19T21:30:00Z`. Bare dates are
only correct for `log.md` date headings.

### 1.3 Actor convention

OKF §7 defines actors as `<producer>/<version>` for agents and tools,
`human:<id>` for people, and `process:<id>` for automation. Project Lead also
uses the spec's `team:<id>` form shown for source authors in §5.1 when a source
is authored by a team rather than a person, agent, or process. The identity
fields `generated.by`, every `verified[].by`, and every `sources[].author` MUST
use this convention.

- Lead-authored content uses `project-lead-claude-code/0.2.0` or
  `project-lead-copilot/0.2.0`, depending on the platform running the Lead. The
  producer names encode the runtime surface, while `0.2.0` is this package's
  Project Lead profile/plugin version; this satisfies OKF §7 because the segment
  after `/` is a real version, not a platform tag.
- Historical migrations use `process:project-lead-migration` because the Lead
  cannot honestly know the original author.
- Human confirmations use `human:<github-login>`.
- Automated events use `process:<name>`, for example `process:github-merge` or
  `process:project-lead-sync`.
- Source authors use the same convention, for example `author: team:github-docs`
  for GitHub documentation or `author: process:github-rest-api` for an API
  response.

The `human:` prefix is mandatory for hand-authored or human-confirmed content;
OKF trust-tier derivation depends on that exact prefix.

### 1.4 Reserved files

`index.md` and `log.md` are reserved filenames and MUST NOT be used for concept
documents.

- The bundle-root `.project-memory/index.md` MAY carry frontmatter, but only:

  ```yaml
  ---
  okf_version: "0.2"
  ---
  ```

  Its body is a grouped catalog of markdown links and one-line descriptions.
- Any nested `index.md` carries no frontmatter. Its body may be generated or
  omitted by consumers.
- `log.md` MAY carry frontmatter. Project Lead writes:

  ```yaml
  ---
  type: Log
  title: Project Memory Update Log
  ---
  ```

  The body starts with `# Project Memory Update Log`, then bare date headings in
  descending order:

  ```markdown
  ## 2026-09-19

  - **Requirement**: Captured REQ-001 for CSV export.
  - **Decision**: Accepted native GitHub sub-issues for traceability.
  ```

### 1.5 Links, sources, and the bundle-root trap

Use standard markdown links only. OKF v0.2 does not include Obsidian wikilinks.

- Same-bundle Project Memory links use the OKF-recommended bundle-relative form,
  resolved from `.project-memory/`: `[Risk](/wiki/risks/rate-limits.md)`.
- Links that leave `.project-memory/` MUST NOT use a leading `/`, because that
  leading slash resolves to `.project-memory/`, not the repo root. Use a
  correctly counted relative path, for example from
  `.project-memory/wiki/initiatives/csv-export.md` to a requirement document:
  `[REQ-001](../../../docs/requirements/REQ-001-csv-export.md)`.
- Absolute URLs are acceptable for out-of-bundle links that need to survive file
  moves.
- Avoid bare non-slash paths for path-valued OKF fields whose target is meant to
  stay inside a bundle; prefer the explicit leading `/` form.

### 1.6 Root concept templates

```yaml
---
type: Project Overview
title: <Project name> — Overview
description: <one-sentence synthesis>
tags: [overview]
generated: { by: project-lead-<platform>/0.2.0, at: <ISO-8601 UTC> }
status: stable
---
```

```yaml
---
type: Memory Conventions
title: Project Memory Conventions (OKF v0.2 profile)
description: Distilled conventions this wiki follows.
generated: { by: project-lead-<platform>/0.2.0, at: <ISO-8601 UTC> }
status: stable
---
```

```yaml
---
type: Integration Link
title: GitHub Project Link
description: The linked GitHub Project (v2) board configuration.
generated: { by: project-lead-<platform>/0.2.0, at: <ISO-8601 UTC> }
status: stable
---
```

```yaml
---
type: Register
title: Requirements Register (Project Memory mirror)
description: Tracking index referencing docs/requirements/* plus issues and Project items.
generated: { by: project-lead-<platform>/0.2.0, at: <ISO-8601 UTC> }
status: stable
---
```

Project Memory concepts under `wiki/` follow the same shape, with the directory's
`type`, a meaningful title and description, optional tags, `generated`, OKF
`status`, and optional `sources`, `usage_window`, `verified`, and `stale_after`.

Example initiative source frontmatter:

```yaml
sources:
  - id: req-doc
    resource: ../../../docs/requirements/REQ-001-csv-export.md
    title: "REQ-001: CSV export"
    author: human:satishc
    usage_count: 12
    last_modified: 2026-09-19T20:00:00Z
usage_window: { from: 2026-09-01T00:00:00Z, to: 2026-09-19T23:59:59Z }
```

### 1.7 Workflows

- **Ingest.** When the stakeholder shares a doc, decision, or context, the Lead
  files or updates the relevant wiki page(s), updates `index.md`, normalizes and
  appends `log.md`, and cites sources with OKF `sources` plus footnotes where a
  claim needs attribution.
- **Query.** To answer a stakeholder question, the Lead reads `index.md`, drills
  into relevant pages, and synthesizes an answer with citations to page paths.
  Valuable answers are filed back as new pages so explorations compound.
- **Lint.** On `/project-lead lint`, the Lead reports advisory findings only:
  OKF conformance gaps, contradictions, stale claims, orphan pages, important
  concepts lacking pages, and missing cross-references. It proposes fixes but
  never rejects a bundle or blocks a mode.

### 1.8 `project-link.md` format

```markdown
# GitHub Project Link

- owner: <org-or-user>
- project_number: <N>
- project_url: https://github.com/orgs/<owner>/projects/<N>
- project_id: <PVT_...>            # GraphQL node id
- status_field_id: <PVTSSF_...>    # the single-select Status field
- status_options:
    Intake: <option-id>
    "In Review": <option-id>
    "Ready for Spec": <option-id>
    "In Spec": <option-id>
    "Ready for Dev": <option-id>
    "In Dev": <option-id>
    "In Review (Dev)": <option-id>
    Done: <option-id>
    Parked: <option-id>
- requirement_issue_type: <Requirement | label:requirement>   # detected capability
```

The GitHub Project single-select **Status** field is unrelated to OKF `status`
and to the requirement `lifecycle` extension.

---

## 2. Requirements (`docs/requirements/` — official repo docs)

`docs/requirements/` is its own OKF v0.2 bundle. It has its own bundle-root
`index.md`; `README.md` remains the human-facing register.

```
docs/requirements/
├── index.md                  # bundle root; only okf_version frontmatter
├── README.md                 # official register: lifecycle + priority + links
├── _template.md              # type: Template; live schema is fenced in body
└── REQ-001-<slug>.md         # one official Requirement concept per requirement
```

`index.md` is purely regenerable: a flat list of every `REQ-*.md` using each
doc's title and description, plus exactly one link to `README.md`. It never
carries lifecycle, priority, approval, or board columns; those live in
`README.md` and `.project-memory/requirements-register.md`.

### 2.1 Requirement document schema

Each `REQ-NNN-<slug>.md` is YAML frontmatter + body:

```markdown
---
id: REQ-001
title: <short title>
description: <one-sentence summary>
type: Requirement
lifecycle: draft         # draft | in-review | approved | in-spec | specced | in-delivery | delivered | parked
status: draft            # OKF status: draft | stable | deprecated; derived from lifecycle
priority: P2             # P0 | P1 | P2 | P3
version: 1
generated: { by: project-lead-<platform>/0.2.0, at: <ISO-8601 UTC> }
approved_at:             # ISO-8601 UTC, set on PR merge or express signoff
approved_by:             # human:<stakeholder-login>
requirement_issue:       # GitHub Requirement issue URL
links:
  requirement_pr:        # PR that introduced/changed this doc
  project_item:          # GitHub Project item node id (PVTI_...)
  initiative:            # relative path into .project-memory/wiki/initiatives/
  specs: []              # spec PR(s) / docs/specs paths (filled by pm-team)
  child_issues: []       # Feature/Story sub-issues (filled after spec merge)
  prs: []                # dev-team PRs
---

## Problem / Context
<why this matters; the situation today>

## Desired outcome (goal)
<what "better" looks like>

## Scope — in
<what this requirement covers>

## Scope — out (non-goals)
<explicit exclusions>

## Acceptance / success criteria
<testable, verifiable criteria — the heart of the document>

## Constraints & assumptions
<technical, business, time, dependency constraints; assumptions made>

## Open questions
<unresolved items; must be empty before approval>

## Change log
- [2026-09-19T21:30:00Z] v1 — created as draft.
```

Draft requirements intentionally omit the optional OKF `verified` key. OKF
defines "unverified" as no `verified` key at all; a bare `verified:` would parse
as present-but-null rather than absent. On approval, add this key with a real
human confirmation:

```yaml
verified: { by: human:<login>, at: <ISO-8601 datetime with UTC offset> }
```

Blank `approved_at` and `approved_by` placeholders are Project Lead extension
keys, not OKF trust metadata; they remain as visible workflow placeholders until
approval stamps them.

`docs/requirements/README.md` is the official human-facing register:

```markdown
---
type: Register
title: Requirements Register
description: The official, human-facing table of all requirements, their lifecycle stage, and links.
generated: { by: project-lead-<platform>/0.2.0, at: <ISO-8601 UTC> }
status: stable
---

# Requirements Register

| ID | Title | Lifecycle | Priority | Approved | Requirement issue | Doc |
|----|-------|-----------|----------|----------|-------------------|-----|
| REQ-001 | ... | approved | P1 | 2026-09-19T21:30:00Z | #12 | [doc](REQ-001-....md) |
```

`docs/requirements/_template.md` carries `type: Template`; the fillable
Requirement frontmatter lives inside a fenced code block in its body so template
files are never mistaken for live requirements.

### 2.2 Numbering

`REQ-NNN` is zero-padded, monotonically increasing, never reused. The Lead
derives the next number by scanning existing `docs/requirements/REQ-*.md`.

---

## 3. Requirement lifecycle

```
draft ──► in-review ──►(APPROVAL GATE)──► approved
   ──► in-spec ──► specced ──► in-delivery ──► delivered
                          (parked at any point, with a reason logged)
```

| Lifecycle | Meaning | Who advances it |
|---|---|---|
| `draft` | Captured, still being shaped | Lead |
| `in-review` | Meets Definition of Ready; requirement PR open for stakeholder review | Lead opens; stakeholder reviews |
| `approved` | Stakeholder approved (PR merged or express signoff) | Stakeholder action, Lead stamps |
| `in-spec` | Handed to pm-team; spec in progress | Lead, on `/pm-team` launch |
| `specced` | Spec PR merged; Feature/Story issues seeded | Lead, after spec merge |
| `in-delivery` | dev-team building one or more child issues | Lead, on `/dev-team` |
| `delivered` | All children done; verified against acceptance criteria | Lead, at acceptance |
| `parked` | Deferred; reason in Change log | Lead, on stakeholder direction |

### 3.1 The `lifecycle` / OKF `status` mapping

Requirement lifecycle is a Project Lead extension key named `lifecycle`. OKF
`status` remains reserved for OKF's `draft | stable | deprecated` meaning. Every
requirement document carries both keys, using this binding mapping:

| Requirement `lifecycle` | OKF `status` | Justification |
|---|---|---|
| `draft` | `draft` | Not yet reviewed, possibly incomplete — exact match to OKF's own definition of `draft` (§5.4). |
| `in-review` | `draft` | Still not yet a settled, "ready for consumption" document — the requirement PR is open, content can still change under review. Still `draft` in OKF's sense even though our own funnel treats it as a distinct stage. |
| `approved` | `stable` | The document's content is now reviewed and current — exactly OKF's definition of `stable` ("ready for consumption," §5.4). |
| `in-spec` | `stable` | The requirement *document itself* remains the settled, current definition of what's wanted; it is pm-team's spec that is in flux, not this doc. |
| `specced` | `stable` | Same reasoning — the requirement doc doesn't change just because downstream work progresses. |
| `in-delivery` | `stable` | Same reasoning. |
| `delivered` | `stable` | **Deliberately not `deprecated`.** A delivered requirement's *definition* is still current/true — it describes what was built and why, and remains the canonical record. Nothing about "done" makes the content stale or superseded; OKF's `deprecated` means "kept for links and history; no longer current" (§5.4), which does not describe a delivered requirement. |
| `parked` | `deprecated` | This is the one lifecycle stage that genuinely matches OKF's `deprecated`: "kept for links and history; no longer current" (§5.4) — a parked requirement is explicitly deferred/abandoned, its content is not something anyone should act on as current guidance. |

### 3.2 Definition of Ready (DoR)

A requirement may only move to `in-review` when ALL of the following hold:

- [ ] Clear problem statement and desired outcome.
- [ ] **Testable** acceptance / success criteria.
- [ ] Explicit scope **in** and **out** (non-goals).
- [ ] Known constraints & assumptions recorded.
- [ ] No blocking open questions remain.

The Lead checks the DoR explicitly before opening a requirement PR.

---

## 4. Approval gate (the contract)

This is the boundary that protects pm-team from half-baked input.

- **Primary, official approval = a requirement PR.** The Lead writes/updates
  `docs/requirements/REQ-NNN.md` on a branch
  (`users/<you>/requirements/REQ-NNN-<slug>`), commits, and opens a PR titled
  `[REQ-NNN] <title>`. The stakeholder reviews and **approves/merges**. The merge
  is the auditable signoff.
- **Express signoff** (for tiny edits or when a PR is overkill): an explicit
  in-chat "approved" that the Lead records. Even then the Lead updates the doc
  frontmatter (`lifecycle`, `approved_at`, `approved_by`), the OKF `status`, the
  register, and `log.md`.
- On approval the Lead completes the matching persistence path before handing off:
  - For a requirement PR, run the **post-merge reconciliation transaction** below
    on the default branch.
  - For express signoff, there is no PR to query; use the confirmed stakeholder
    GitHub login and current UTC instant as the approval identity/time, then
    perform the same doc/register/log/issue/Project updates on the default branch
    and persist them by the same direct-commit-or-follow-up-PR rule.
- **Verification stamp:** for a PR merge, derive `verified.by` from the
  transaction's `mergedBy.login` and `verified.at` from `mergedAt`. For express
  signoff, use the confirmed stakeholder GitHub login and current UTC instant.
  If no reliable human identity exists, omit `verified` rather than guessing.
- **Post-merge reconciliation transaction (PR approvals):**
  1. Query approval metadata in one call:
     `gh pr view <PR> --json mergedBy,mergedAt`.
  2. Return to the default branch before editing: `git fetch`, checkout the
     default branch, and pull, because team handoffs may leave the worktree on a
     team branch and the metadata must land on the merged state.
  3. Create the **Requirement issue** (see §5) and add/convert the Project item;
     capture both the issue URL and the Project item node id (`PVTI_...`).
  4. Stamp the requirement doc with `lifecycle: approved`, OKF
     `status: stable`, `approved_at`, `approved_by`, `verified`,
     `requirement_issue`, and `links.project_item`; refresh `generated.at`;
     update `docs/requirements/README.md`, `docs/requirements/index.md`, and
     `.project-memory/requirements-register.md`; append the normalized `log.md`
     approval entry; bump the Change log and `version`.
  5. Persist those bookkeeping edits in a clearly designated mechanical follow-up
     commit, for example `chore(REQ-NNN): record approval metadata`. If the
     default branch is protected and refuses a direct commit, open a small
     follow-up PR with that title for the stakeholder to merge without
     re-reviewing the already-approved requirement.
  6. This recording does **not** reopen the requirement. It is bookkeeping for an
     approval that already happened, distinct from the §4 change-control rule
     that intentionally re-opens an approved requirement to `in-review` through a
     new requirement PR.
- **Hard rule:** the Lead **MUST NOT** launch or recommend `/pm-team` for a
  requirement whose `lifecycle` is not `approved`.
- **Change control:** any change to an `approved` (or later) requirement re-opens
  it to `in-review` via a **new requirement PR**, and requires re-approval before
  pm-team re-engages. The Change log records the version bump and the reason.
- **Acceptance signoff (optional closure):** when dev-team has delivered all
  child issues, the Lead verifies the result against the doc's acceptance
  criteria and offers the stakeholder a closing acceptance signoff before
  setting `lifecycle: delivered` (OKF `status` remains `stable`).

---

## 5. GitHub mapping (leveraging native concepts)

### Requirement issue

Each requirement is represented by exactly one **Requirement issue**:

- **Preferred:** the org's custom **issue type "Requirement"**. Detect support
  via GraphQL (`organization.issueTypes`) or `gh issue create --type` capability.
- **Fallback:** a normal issue carrying a `requirement` label (bootstrap ensures
  the label exists).

The issue title is `[REQ-NNN] <title>`; its body links to the
`docs/requirements/REQ-NNN.md` doc and the requirement PR, and is the board item
for the requirement.

### Sub-issues for traceability

After the spec PR merges, pm-team seeds Feature/Story issues. The Lead makes them
**native sub-issues** of the Requirement issue, producing an end-to-end chain:

```
Requirement issue (REQ-001)
├── Feature issue (from pm-team)
│   ├── User Story issue ──► dev-team PR
│   └── User Story issue ──► dev-team PR
└── Feature issue ...
```

GitHub's Projects v2 rolls up child progress onto the Requirement item, so the
stakeholder sees completion at the requirement level on the Kanban.

### Project (v2) board

- One Project per repo (or per owner), linked in `project-link.md`.
- Single-select **Status** field with the funnel columns:
  **Intake → In Review → Ready for Spec → In Spec → Ready for Dev → In Dev → In
  Review (Dev) → Done** (plus **Parked**).
- Board items are the Requirement issues (with their sub-issues for roll-up).
  During early drafting a requirement may ride as a **draft item** until its
  Requirement issue exists, then it is converted/linked.

### Useful commands (reference)

```bash
# Projects
gh project list --owner <owner>
gh project create --owner <owner> --title "<repo> Delivery"
gh project item-add <N> --owner <owner> --url <issue-url>
gh project field-list <N> --owner <owner>
gh project item-edit --id <item-id> --field-id <status-field-id> \
  --project-id <project-id> --single-select-option-id <option-id>

# Issues / labels / types
gh label create requirement --description "Stakeholder requirement" --color 5319e7
gh issue create --title "[REQ-001] <title>" --body-file <body.md> --type Requirement
# Otherwise drop --type and add: --label requirement

gh issue edit <requirement-issue> --add-sub-issue <child-issue>[,<child-issue>...]
# or, from the child: gh issue edit <child> --parent <requirement-issue>
```

The skill/agent contains the current invocations; this section is a map, not a
frozen contract.

---

## 6. OKF conformance, migration, and versioning

Project Lead pins its profile to OKF v0.2 as read at `ad30107c`. Bundle roots
SHOULD declare `okf_version: "0.2"`; consumers that do not understand a declared
version still attempt best-effort consumption.

### 6.1 Conformance posture

Lint and migration reports are advisory. OKF consumers MUST NOT reject a bundle
for missing optional fields, unknown types, unknown keys, broken links, or
missing `index.md` files. Therefore Project Lead never blocks bootstrap, intake,
approval, sync, or status because an OKF optional field is missing.

### 6.2 Migration mode

`migrate` upgrades pre-OKF Project Memory and requirement files. It is dry-run by
default and prints a diff-shaped report. It writes only with `--apply`, as normal
working-tree edits.

Detection includes: non-root `index.md` frontmatter, concept frontmatter missing
`type`, legacy provenance keys, Obsidian wikilinks, legacy log headings of the
form `## [YYYY-MM-DD] event | subject`, missing root `okf_version`, and
requirement documents that still use the old lifecycle vocabulary directly in
`status` instead of the `lifecycle` extension plus OKF `status`.

Transformations are idempotent:

- Strip `index.md` frontmatter except the bundle-root `okf_version` block.
- Reformat `index.md` bodies into OKF §8 grouped headings containing markdown
  links and one-line descriptions (`* [Title](target.md) - description`).
- Convert legacy log headings into OKF date sections, then run `normalize_log`.
- Infer `type` from the vocabulary table, migrate known provenance into
  `generated` with `process:project-lead-migration` when historical authorship is
  unknown, preserve unknown keys, and rewrite wikilinks to markdown links.
- For `docs/requirements/REQ-*.md`, rename the requirement funnel field to
  `lifecycle`, add OKF `status` from §3.1, and add `type: Requirement` if absent.
- Report optional fields that could not be honestly backfilled instead of
  fabricating sources, generated actors, or verifiers.

Before transforming, `migrate` checks these already-migrated predicates so a
second pass is a true no-op. A predicate MUST be the exact negation of its
transformation's precondition: if any transformation step would still change the
file, the file is not yet migrated and MUST NOT be skipped.

- A concept file (not `index.md`/`log.md`) is migrated when: it has a non-empty
  `type` key, AND it has neither `created` nor `updated` keys, AND its body
  contains no `[[` `]]` sequences. If all three hold, skip the file entirely
  (report "already conformant").
- A bundle-root `index.md` is migrated only when: its frontmatter is exactly
  `{ okf_version: "0.2" }` and nothing else, AND its body is already in OKF §8
  grouped-links-with-description shape. Missing `okf_version` is a pre-OKF
  detection signal, never an already-migrated state.
- A non-root `index.md` is migrated only when: its frontmatter is empty, AND its
  body is already in OKF §8 grouped-links-with-description shape.
- A `log.md` is migrated when: every `##`-heading line matches
  `^## \d{4}-\d{2}-\d{2}$` exactly, headings are in strictly descending date
  order, and no date appears twice.
- A `docs/requirements/REQ-*.md` is migrated when: the generic concept predicate
  holds (`type` is non-empty, no `created`/`updated`, and no body wikilinks),
  AND it has a `lifecycle:` key (not a bare requirement-vocabulary `status:`
  key), AND it has a `status:` key whose value is one of
  `draft|stable|deprecated`.

When rewriting wikilinks, choose the markdown link text in this order: (i) the
`|Alias` pipe text when present; (ii) the target file's own frontmatter `title`
when the target can be located and read, preferred over guessing; (iii) a
heuristic fallback using the final path segment with `-`/`_` converted to spaces
and title-cased. The dry-run report MUST note which source (`alias`,
`target-file title`, or `heuristic guess`) resolved each link.

When migrating legacy `created`/`updated` provenance, `updated` takes precedence
over `created` for `generated.at`; if only `created` exists, use `created`. Bare
dates are coerced to ISO-8601 UTC by appending `T00:00:00Z`. Each migrated file
MUST disclose the caveat that `process:project-lead-migration` means historical
authorship is unknown and invites the stakeholder to manually correct provenance
where they know the true author.

The dry-run report is binding: for every candidate file, show the old
frontmatter block → new frontmatter block, old heading text → new heading text,
and every rewritten wikilink as `[[old]] → [new](new-target)` with its
resolution source noted (`alias`, `target-file title`, or `heuristic guess`).
The report is printed before any writes; writes happen only with `--apply`.

### 6.3 `normalize_log(text) -> text`

`normalize_log` is the shared routine used by migration, lint fixes, and every
append-to-log path:

1. Split text into a preamble (everything before the first line matching
   `^## `) and sections, where each section is one heading line matching
   `^## (.+)$` plus all content up to the next such heading or EOF. Preserve the
   preamble byte-for-byte. If it is absent, synthesize
   `# <Directory or Project> Update Log\n\n`, deriving the name from the
   containing directory or using `Project Memory` for the bundle-root `log.md`.
2. Classify each `##` heading. A heading that matches
   `^## \d{4}-\d{2}-\d{2}$` exactly is a date section. Any non-date `##`
   heading is first routed through the §6.2 legacy log transformation (for
   example `## [YYYY-MM-DD] event | subject` becomes the date heading and a
   bullet `- **Event**: subject — text`) before continuing.
3. Preserve multiline bullets and section content until the next bullet or
   section boundary; do not split wrapped bullet paragraphs into separate
   entries.
4. Group all date sections with the same date key, concatenating bullets in the
   order they appeared in the input.
5. De-duplicate bullets within each date group. Two bullets are identical when
   their complete text is byte-identical after trimming outer whitespace; keep
   the first occurrence and drop later duplicates.
6. Keep surviving bullets within each date group in their relative input order.
7. Sort date groups descending by `YYYY-MM-DD`.
8. Emit the preamble, then each date group as `## YYYY-MM-DD`, a blank line, the
   ordered bullets (one per bullet block, starting with `- ` and conventionally
   using a bold lead word), and a trailing blank line before the next group.
   Running the routine on its own output MUST be byte-identical.

Run `normalize_log` in one shared pre-mode Project Memory step at the top of
every mode that touches `.project-memory/`, including read-only `status`, before
reading or writing memory. Also run it inside `lint` as an explicitly reported
safe auto-fix (state dates merged and duplicate bullets dropped) and after any
git operation that could have union-merged `.project-memory/log.md`.

### 6.4 Lint checklist

`lint` reports and proposes; it never gates progress. Checks include:

| Check | Posture |
|---|---|
| Non-reserved `.md` missing parseable frontmatter or non-empty `type` | Advisory |
| `index.md` frontmatter beyond root `okf_version` | Advisory |
| `log.md` not grouped as bare descending `## YYYY-MM-DD` sections | Advisory; safe auto-fix may be offered |
| Bare `verified` mapping | Not a finding; it is valid OKF |
| Unknown `type` value | Low-priority advisory |
| Unknown extra frontmatter keys | Not a finding |
| Bundle-internal link whose target is absent | Advisory, framed as possible future knowledge |
| Missing `index.md` in a directory | Low-priority advisory |
| Timestamp-valued field lacking explicit UTC offset | Advisory |
| Shared `usage_window` nested under a source entry | High-priority advisory |
| Footnote label with no matching `sources[].id` | Advisory |
| `generated` present without `by` | Advisory |
| Same-bundle path-valued field not using recommended `/` form | Gentle advisory |
| Requirement `lifecycle` and OKF `status` disagree with §3.1 | Prominent advisory |
| `docs/requirements/index.md` duplicates README lifecycle/priority columns | Advisory |

Pre-existing quality checks continue: contradictions between pages, stale claims
superseded by newer information, orphan pages, concepts lacking pages, and
missing cross-references.

### 6.5 Out of scope

`type: Attested Computation` and OKF §10 fields (`runtime`, `parameters`,
`computation`, `executor`, `attester`) are not part of this profile. A future
extension could model the Lead's requirements-funnel status digest as an
Attested Computation, but this schema does not implement it.

---

## 7. Distributed / multi-machine operation

When features are distributed across multiple agent sessions and machines, some
generated files merge cleanly and some do not. Durable shared knowledge is
committed; ephemeral per-session / per-machine working state is gitignored; and
the one shared-but-append-only file uses a union merge.

Bootstrap writes the `.gitignore` and `.gitattributes` entries below.

### Committed (durable, shared) — all of `.project-memory/`

`overview.md`, `index.md`, `requirements-register.md`, `schema.md`,
`project-link.md`, `log.md`, `references/`, and every page under `wiki/` are the
project's brain and record. Parallel sessions generally edit different pages, so
conflicts are rare and, when they occur, are real semantic merges to resolve by
hand. `project-link.md` holds platform/account-agnostic IDs, not machine-specific
values, so it is safe to share.

### Gitignored (ephemeral, machine-local) — all of `.scrum/` (and `.worktrees/`)

The teams' Scrum working memory — per-agent session journals (which embed
**absolute worktree paths**), `plan.md`, `design.md`, `retrospective.md`,
`watchdog-status.json`, and the cross-project `lessons.md` — is scratch state for
one run on one machine. The deliverables of a run are its **PRs, issues, and
board items**; distributed runs coordinate through GitHub, not through `.scrum/`
files. `.gitignore` gets `.scrum/` and `.worktrees/`.

### Union-merged (shared but append-only) — `.project-memory/log.md`

`.gitattributes` gets `.project-memory/log.md merge=union`, so git concatenates
both sides' entries instead of raising a conflict. The Lead immediately runs
`normalize_log`: it groups entries under bare date headings, sorts dates
newest-first, and collapses exact duplicate bullets.

### Lessons stay useful without merging

Because raw `.scrum/lessons.md` is machine-local, cross-machine learning is
preserved by having the Lead **ingest notable lessons into `.project-memory/wiki/`**
(committed) rather than relying on the raw FIFO file.

### Keep the Lead single-writer where you can

By design the Lead is the **sole writer** of `.project-memory/`. If one Lead
session coordinates while only `dev-team` / `pm-team` execution is distributed,
`.project-memory/` has a single writer and the union merge on `log.md` is only a
safety net. Running multiple concurrent Lead sessions against the same wiki is
supported by the rules above, but will occasionally require a manual merge on the
rewritten summary files (`overview.md`, `index.md`, `requirements-register.md`).
