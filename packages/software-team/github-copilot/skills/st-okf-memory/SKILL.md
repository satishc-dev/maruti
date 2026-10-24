---
name: st-okf-memory
description: 'Use when any software-team agent reads or writes package documents, OKF bundles, Project Memory, team artifacts, ledgers, or document links; apply ownership, frontmatter, timestamp, citation, actor, and honesty rules before editing or proposing changes.'
---

# st-okf-memory

Use this skill any time you read or write a document in this package.
For full detail, read `.software-team/contracts/OKF-PROFILE.md`, `.software-team/contracts/MEMORY-SCHEMA.md`, `.software-team/contracts/ARTIFACTS.md`, and `.software-team/contracts/ROLES.md`. Bootstrap materializes that directory in the repository; if it is absent, say so and treat this skill as the operative summary rather than inventing the missing detail.

## Canonical Memory capability

Software Team bundles the same canonical Memory skills and helper as the
standalone plugin, not a divergent implementation. Resolve this loaded skill's
real path (following symlinks), then take its plugin root. Read
`<plugin-root>/memory/references/operating-policy.md` and
`<plugin-root>/memory/references/record-guide.md` for the shared OKF format and
evidence rules. Use `runtime-guide.md` in that same directory before invoking the
helper. Do not assume the repository cwd is the plugin root or depend on an
installed sibling `memory` plugin.

The canonical format rules cover index/concept frontmatter, unknown-key
preservation, actors and timestamps, ordinary Markdown links, source/footnote
joins, honesty, and document-trust `status`. This adapter adds the team-specific
ownership and delivery rules below; it does not redefine the generic format.

For local bootstrap/capture/recall/checkpoints/consolidation, use the bundled
Memory skills and invoke Python directly on
`<plugin-root>/memory/runtime/memory.py --root <workspace> ...`.
Bootstrap must verify the narrow `/.maruti/memory/local/` ignore rule before
writing content. It needs no GitHub authentication. Preserve and report existing
roots; do not migrate `.project-memory/` or replace team contracts.

Workers capture observations in ignored `.maruti/memory/local/` or send
`memory_proposals[]` through the team handoff. Generic shared promotion requires
explicit authorization but never transfers ownership of `.project-memory/`,
requirements, lifecycle, board/auth policy, or canonical register projections.
Approval to promote is not approval to stage, commit, or push.

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

## Team document extensions

Follow the canonical Memory OKF profile for document format.
Use `owner:` for accountability.
Use `workstream:` when an artifact belongs to a delivery slice.
Do not overload `generated.by` with ownership.
Use package actors from `.software-team/contracts/OKF-PROFILE.md`.
Use `process:software-team-migration` only when historical authorship is genuinely unknown.

## OKF status

OKF `status` is document trust only.
It is not delivery progress.
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
