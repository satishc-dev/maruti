---
type: Glossary
title: Software Team — Glossary
description: One canonical meaning per term, shared by all six teams.
status: stable
---

# Glossary

The legacy packages this one replaces failed partly on vocabulary: `pm-team` called
its top-level unit an *initiative*, `project-lead` called it a *requirement*, and
`dev-team` called everything a *work item*. Nothing joined up.

This glossary is the authority. Every agent in this package uses these words with
these meanings and no others. Where a term has a tempting alternative meaning, the
alternative is listed and explicitly rejected.

## Work and its units

**Requirement**
: The stakeholder-facing statement of a need — what and why, never how. The root
unit of committed work. Identified `REQ-NNN`, lives at
`docs/requirements/REQ-NNN-<slug>.md`, owned by Project-Lead. Everything downstream
traces to exactly one requirement.
: *Not:* a specification. A requirement states the need; a spec states the solution.

**Feature**
: A coherent, independently specifiable slice of a requirement, user-visible.
Produced by PM-Team during specification. One spec file per feature at
`docs/specs/REQ-NNN/<feature-slug>.md`.

**Story**
: An implementable unit within a feature, expressed from the user's perspective with
testable acceptance criteria. Identified `US-<n>` within its spec.
: *Not:* a task. A story is what the user gets; a task is a step toward it.

**Task**
: A unit of implementation work inside a workstream, assigned to one implementer.
Internal to Dev-Team. Never appears on the board.

**Workstream**
: An independently deliverable slice of an approved requirement, assigned to exactly
one Dev-Team, with a declared file scope that may not overlap any other
workstream's. Identified `ws<k>`, scoped to its requirement — `REQ-007/ws2`.
Workstreams are the unit of parallelism.
: *Not:* a feature. A workstream is a delivery grouping and may span features or
split one.

**Initiative**
: **Rejected.** The legacy `pm-team` used this for the top-level unit. Use
*requirement*. The word appears in this package only when describing what the
legacy packages did.

**Work item**
: **Rejected as a unit of work.** Too vague — it meant three different things across
the legacy packages. Use the specific term. The phrase *board item* is acceptable
when referring to the GitHub Project row itself.

## Documents

**Research brief**
: The question Research-Team was commissioned to answer, with scope and constraints.
`docs/research/<topic>/`.

**Research finding**
: A single cited conclusion. Every load-bearing claim carries a footnote matching a
declared source. Findings are advisory — they inform requirements and specs, they
do not bind.

**UX brief**
: The interaction design for a user-visible requirement, with flows and wireframes
expressed as text (Mermaid or ASCII) so they live in the repository.
`docs/ux/REQ-NNN/`.

**Spec** · **Feature spec**
: The buildable description of one feature: problem, goal, non-goals, stories,
acceptance criteria, dependencies, risks. Produced by PM-Team.
`docs/specs/REQ-NNN/<feature-slug>.md`.

**Solution architecture**
: The technical shape of the system for a requirement — components, interfaces, data
flow, alternatives considered. Produced by Architect-Team with Project-Lead, after
specs exist. `docs/architecture/`.

**ADR** · **Architecture decision record**
: A single durable technical decision, its context, the alternatives, and its
consequences. Written when a decision constrains future work.

**Development principle**
: A binding repository engineering standard derived from the solution architecture —
coding standards, testing standards, structural conventions, dependency policy.
Owned by Architect-Team. **Binding on Dev-Team, not advisory.**
: *Not:* a style preference. A principle traces to a real constraint.

**Project Memory**
: The durable, committed knowledge bundle at `.project-memory/` — project overview,
decisions, risks, stakeholders, glossary, initiatives, references, and the update
log. Owned and written solely by Project-Lead.

**Ledger** · **Delivery ledger**
: The append-only cross-team record for one requirement, at
`.software-team/REQ-NNN/ledger.md`. Holds handoff envelopes, receipts, review
records and board requests. Committed. Every team appends; no team rewrites another
team's entries.

## Process

**Bootstrap**
: The idempotent mode that makes a repository ready for this package — memory
bundle, document bundles, Project board, labels, ignore rules. Run once per
repository; safe to re-run.

**Handoff**
: The transfer of work between teams, carried by a typed envelope in the ledger and
acknowledged by a receipt. Never a bare instruction to a human.

**Envelope**
: The structured record of a handoff: who, to whom, about which requirement and
workstream, at which gate, with which verdict, artifacts and board requests.

**Receipt**
: A receiving team's acknowledgement of an envelope. An unreceipted envelope is an
incomplete handoff.

**Board request**
: A change to the GitHub Project or its issues, requested by a team and applied by
Project-Lead. Teams never mutate the board directly.

**Gate**
: A condition that must hold before a lifecycle transition. Gates are stated, not
implied, and are never skipped.

**Duck** · **Rubber duck**
: A team's independent critic. Reviews the team's output, reports what is wrong, and
decides whether it may proceed. Every team except Project-Lead has one. A team's
work is not complete until its duck has passed it.
: *Not:* a proofreader, and not a co-author. A duck never writes the artifact it
judges.

**Review round**
: One exchange between a lead and its duck — the duck reviews, the lead revises, the
duck reviews again. At least two rounds always occur.

**Escalation**
: A team returning a decision it cannot make to Project-Lead. Always recorded, never
silent.

**Impediment**
: Something preventing a team from proceeding — a missing decision, an ambiguity, an
unmet dependency. Returned to Project-Lead as an escalation.
: *Note:* this package uses *impediment* for this meaning. The word *blocker* is
reserved and should not be used as a synonym.

**Acceptance**
: Project-Lead's verification that delivered work satisfies the requirement's
acceptance criteria. Happens **before** merge to the default branch.

**Debt**
: Work accepted despite a known shortfall, after a review deadlock. Recorded as a
decision in Project Memory. Never absorbed silently.

## State

**Lifecycle**
: The delivery funnel a requirement moves through. A Project-Lead extension field.
: *Not:* OKF status, and not the board column.

**OKF status**
: Document trust only — `draft`, `stable`, or `deprecated`. Says nothing about
delivery progress.

**Board column** · **Status field**
: The visible state on the GitHub Project. A **projection** of lifecycle, not a
source of truth. When they disagree, the document wins and the board is corrected.

**Parked**
: A requirement deliberately deferred, with a recorded reason. OKF status becomes
`deprecated` because it is no longer current guidance.

**Blocked**
: Work that cannot proceed pending a decision or dependency. Transient. Leaves OKF
status untouched — being stuck says nothing about whether a document is trustworthy.

## Identifiers

| Form | Meaning |
|---|---|
| `REQ-NNN` | Requirement. Zero-padded, monotonic, never reused. Allocated only by Project-Lead. |
| `ws<k>` | Workstream within a requirement — written `REQ-NNN/ws<k>` when ambiguous. |
| `US-<n>` | Story within a feature spec. |
| `ADR-NNN` | Architecture decision record. |
| `F-<round>-<n>` | A review finding, scoped to its round. |
| `#<n>` | A GitHub issue or pull request. |
| `PVT_…` `PVTI_…` `PVTSSF_…` | GitHub Projects v2 node ids — project, item, status field. |

## Agents

| Name | Role |
|---|---|
| `St-Project-Lead` | Root agent. The only voice to the user, the only board writer. |
| `St-Research-Lead` · `St-Research-Duck` | Research-Team |
| `St-Architect` · `St-Architect-Duck` | Architect-Team |
| `St-Pm-Lead` · `St-Pm-Duck` · `St-Feature-Analyst` | PM-Team |
| `St-Dev-Lead` · `St-Dev-Duck` · `St-Implementer` · `St-Test-Engineer` · `St-Code-Reviewer` | Dev-Team |
| `St-Ux-Designer` · `St-Ux-Duck` | UX-Team |

**Lead**
: The agent that owns and produces a team's output.

**Crew**
: A team's worker agents, dispatched by its lead.

**Root agent**
: Project-Lead. Runs as the session itself rather than as a dispatched subagent.

**Mechanical gate**
: `St-Code-Reviewer` — independently re-runs tests and linters and reads the diff.
Distinct from the duck, which judges quality and goal alignment rather than
correctness mechanics.
