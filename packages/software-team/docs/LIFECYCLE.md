---
type: Contract
title: Software Team — Delivery Lifecycle
description: Canonical requirement lifecycle, status mapping, transition protocol, gates, and reconciliation rules for the software-team package.
status: stable
---

# Delivery Lifecycle

This contract defines how `software-team` moves a stakeholder requirement from first written intent to delivered work.

It refines `ROLES.md`. If this contract and `ROLES.md` disagree, `ROLES.md` wins.

## 1. Scope

This document governs six teams.

| Team | Lifecycle role |
|---|---|
| Project-Lead | Owns requirements, lifecycle transitions, board projection, and acceptance. |
| Research-Team | Investigates before a requirement exists; advisory and off-board. |
| UX-Team | Defines user-visible experience when the requirement has one. |
| PM-Team | Turns approved requirements into buildable specifications. |
| Architect-Team | Produces solution architecture and development principles. |
| Dev-Team | Builds, verifies, opens the pull request, and merges after acceptance. |

Two rules control every transition.

1. **Project-Lead is the only lifecycle writer.** Other teams request transitions through the handoff envelope.
2. **The requirement document is the source of truth.** The board and registers are projections from requirement frontmatter.

## 2. Research is before the lifecycle

Research is not a requirement lifecycle state.

Research happens before `draft`. It answers questions, compares options, identifies constraints, and records evidence. It may inform a requirement, or it may be discarded. It does not commit the project to build anything.

| Property | Rule |
|---|---|
| Owner | Research-Team owns `docs/research/`. |
| Board | Research is off-board. It has no GitHub Project status. |
| Requirement ID | Research has none unless Project-Lead later creates a requirement. |
| Binding force | Advisory. It informs requirements, specs, and architecture; it does not bind them. |
| Exit | Project-Lead may create a `draft` requirement, commission more research, or discard the finding. |

Research deliberately sits outside the requirement lifecycle so exploratory work does not pollute delivery tracking. A finding becomes delivery work only when Project-Lead writes a requirement document.

## 3. Canonical state machine

The requirement lifecycle is a Project-Lead extension field named `lifecycle`.

```text
research (off-board, not lifecycle)
        |
        v
draft -> in-review -> approved -> in-discovery -> in-spec -> in-architecture
        -> ready-for-dev -> in-dev -> in-acceptance -> delivered
```

`parked` and `blocked` are side states reachable from most states.

```text
most active states -> blocked -> previous active state or revised lifecycle state
most active states -> parked -> draft, in-review, approved, or another justified state
```

`delivered` is terminal unless a new requirement or change-control requirement is created. It is not reopened for additional scope.

## 4. State definitions

| State | Meaning | Active team | Enter when | Leave when | Transition performed by |
|---|---|---|---|---|---|
| `draft` | Project-Lead is shaping the requirement. The document may be incomplete. | Project-Lead | Project-Lead creates `docs/requirements/REQ-NNN-<slug>.md` with `version: 1`. | Definition of Ready is met. | Project-Lead moves to `in-review`. |
| `in-review` | The requirement is ready for stakeholder review but is not yet approved. | Project-Lead and stakeholder | `draft` passes Definition of Ready and a requirement review path is opened. | Stakeholder approves, or Project-Lead revises back to `draft`, parks, or blocks. | Project-Lead records approval and moves to `approved`. |
| `approved` | The requirement is stable stakeholder guidance and can be handed to downstream teams. | Project-Lead | Stakeholder approval is recorded with approval metadata and human verification. | Project-Lead decides whether UX discovery is needed. | Project-Lead moves to `in-discovery` or directly to `in-spec`. |
| `in-discovery` | UX discovery is running for user-visible work. It may conclude no UX artifact is needed. | UX-Team, with Project-Lead informed | The approved requirement has, or may have, a user-visible surface. | UX-Team completes its work and the team's duck must pass the work, or UX-Team records that there is no user-visible surface. | Project-Lead moves to `in-spec`. |
| `in-spec` | PM-Team is producing specifications from the approved requirement and any UX input. | PM-Team, with Architect-Team consulted as needed | The requirement is `approved`, or UX discovery has completed or withdrawn. | Specs exist and PM-Team's duck has passed them. | Project-Lead moves to `in-architecture`. |
| `in-architecture` | Architect-Team is producing solution architecture and development principles. | Architect-Team | Specs exist and have passed PM-Team review. | Architecture exists, development principles are set, Architect-Team's duck has passed them, and Architect-Team has not vetoed any spec. | Project-Lead moves to `ready-for-dev`. |
| `ready-for-dev` | The work is build-ready but no Dev-Team workstream is active yet. | Project-Lead | Architecture and development principles are complete and accepted into the requirement context. | Project-Lead decomposes workstreams and launches Dev-Team. | Project-Lead moves to `in-dev`. |
| `in-dev` | Dev-Team is implementing one or more workstreams. | Dev-Team | Workstreams are assigned with file scope, specs, architecture, principles, and acceptance criteria. | All workstream gates are green and a pull request is open. | Project-Lead moves to `in-acceptance`. |
| `in-acceptance` | Project-Lead is verifying the pull request against the requirement before merge. | Project-Lead, with Dev-Team available for fixes | Dev-Team requests acceptance after opening a pull request. | Project-Lead accepts the diff, the PR is merged, issues are closed, and board projection is updated. | Project-Lead moves to `delivered`. |
| `delivered` | The accepted work is merged and closed. The requirement remains the canonical record of what was built and why. | Project-Lead | Acceptance passed, merge completed, issues closed, and registers/board are current. | Only by new change-control requirement; not by editing the delivered requirement in place. | Project-Lead records delivery. |
| `parked` | Delivery is deliberately deferred. The requirement is no longer current guidance. | Project-Lead | Stakeholder direction, Project-Lead decision, or unresolved escalation justifies deferral. | A recorded decision reactivates or supersedes it. | Project-Lead parks or reactivates. |
| `blocked` | Progress is temporarily stuck on a missing decision, dependency, permission, or conflict. | The blocked team plus Project-Lead | A team cannot proceed safely and records the blocking condition. | The condition is resolved, the requirement is revised, or the work is parked. | Project-Lead blocks or unblocks. |

A requirement with no user-visible surface skips `in-discovery`. UX-Team may make that determination when asked; Project-Lead records the decision and moves the requirement directly to `in-spec`.

## 5. Three status systems

There are three status systems. They are separate on purpose.

| System | Field | Owner | Meaning |
|---|---|---|---|
| Delivery lifecycle | `lifecycle` | Project-Lead | Where the requirement is in the delivery funnel. |
| OKF document trust | `status` | Project-Lead, derived from lifecycle | Whether the document is draft, stable, or deprecated. It is not progress. |
| GitHub Project board | `Status` single-select field | Project-Lead | The visible column used for stakeholder tracking. |

Do not use OKF `status` as a delivery funnel. Do not infer document trust from a board column. Do not treat the board as the source of truth.

### 5.1 Binding mapping

| lifecycle | OKF status | Board column |
|---|---|---|
| `draft` | `draft` | Intake |
| `in-review` | `draft` | In Review |
| `approved` | `stable` | Ready for Discovery |
| `in-discovery` | `stable` | In Discovery |
| `in-spec` | `stable` | In Spec |
| `in-architecture` | `stable` | In Architecture |
| `ready-for-dev` | `stable` | Ready for Dev |
| `in-dev` | `stable` | In Dev |
| `in-acceptance` | `stable` | In Acceptance |
| `delivered` | `stable` | Done |
| `parked` | `deprecated` | Parked |
| `blocked` | `(unchanged)` | Blocked |

`delivered` stays `stable`. Completion does not make the requirement obsolete. A delivered requirement remains the canonical record of what was built and why.

`parked` becomes `deprecated`. A parked requirement is kept for history but is no longer current guidance.

`blocked` leaves OKF `status` untouched. Being stuck says nothing about whether the document is trusted.

### 5.2 Frontmatter contract

Every requirement document carries these fields.

```yaml
id: REQ-001
title: Example requirement
type: Requirement
lifecycle: draft
status: draft
version: 1
approved_at:
approved_by:
verified:
links:
  project_item:
  specs: []
  prs: []
```

`version` is an integer. It starts at `1`. Every successful lifecycle transition increments it by exactly one.

## 6. Compare-and-swap transitions

Multiple teams may run at the same time. A naive frontmatter edit can lose a write. Lifecycle changes therefore use compare-and-swap.

A transition is valid only when both predicates hold.

1. The current `lifecycle` equals the expected from-state.
2. The current `version` equals the expected version.

If either predicate fails, the transition is aborted. The agent re-reads the document and re-evaluates from the current state. It does not overwrite.

Only Project-Lead performs lifecycle transitions. Other teams request a transition through the handoff envelope.

### 6.1 Transition procedure

1. Project-Lead reads the requirement document from disk.
2. Project-Lead records the expected `lifecycle` and `version` from that read.
3. Project-Lead evaluates the requested transition and its gate.
4. Immediately before writing, Project-Lead re-reads the document.
5. Project-Lead verifies that current `lifecycle` equals the expected from-state and current `version` equals the expected version.
6. If both checks pass, Project-Lead writes the new `lifecycle`, derived OKF `status`, `version + 1`, required metadata, and Change log entry.
7. Project-Lead regenerates registers and updates the board projection.
8. If either check fails, Project-Lead aborts, re-reads, and re-evaluates. No frontmatter from the stale read is retained.

### 6.2 Handoff transition request

Teams never edit requirement lifecycle. They ask Project-Lead to transition it.

```yaml
handoff:
  requirement: REQ-001
  observed_lifecycle: in-spec
  observed_version: 4
  requested_transition:
    from: in-spec
    to: in-architecture
  evidence:
    - docs/specs/REQ-001/search.md
    - .software-team/REQ-001/ledger.md
  statement: Specs exist and PM-Team's duck has passed them.
```

Project-Lead may accept, reject, block, park, or request correction. The team that sent the handoff does not apply the transition itself.

### 6.3 Successful transition example

Initial read:

```yaml
id: REQ-014
lifecycle: in-spec
status: stable
version: 4
links:
  specs:
    - docs/specs/REQ-014/import-flow.md
```

PM-Team sends a handoff requesting `in-spec -> in-architecture` with evidence that specs exist and PM-Team's duck has passed them.

Project-Lead re-reads immediately before writing and still sees:

```yaml
lifecycle: in-spec
version: 4
```

Both predicates pass. Project-Lead writes:

```yaml
lifecycle: in-architecture
status: stable
version: 5
```

Project-Lead appends a Change log entry, regenerates registers, and moves the board item to `In Architecture`.

### 6.4 Aborted transition example

Initial read:

```yaml
id: REQ-014
lifecycle: in-spec
status: stable
version: 4
```

Before Project-Lead writes, another valid Project-Lead action parks the requirement:

```yaml
lifecycle: parked
status: deprecated
version: 5
```

The pending transition expected `lifecycle: in-spec` and `version: 4`. The current document has neither. Project-Lead aborts the transition, re-reads the requirement, and re-evaluates from `parked`. It does not restore `in-spec`. It does not write `version: 5` from stale state.

## 7. Gate definitions

A gated transition may not occur until the gate is satisfied. Project-Lead records the evidence in the requirement Change log, the ledger, or both.

| Transition | Gate |
|---|---|
| `draft -> in-review` | Definition of Ready is met: problem stated, desired outcome stated, testable acceptance criteria present, scope in and scope out recorded, and no blocking open questions remain. |
| `in-review -> approved` | Stakeholder approval is recorded with `approved_at`, `approved_by`, and a `verified` entry whose `by` starts with `human:`. |
| `approved -> in-discovery` | Project-Lead determines the requirement has, or may have, a user-visible surface and dispatches UX-Team. |
| `approved -> in-spec` | Project-Lead determines no UX work is needed, or UX-Team has withdrawn because there is no user-visible surface. |
| `in-discovery -> in-spec` | UX-Team completes the UX artifact and the team's duck must pass the work, or UX-Team records that no user-visible surface exists. |
| `in-spec -> in-architecture` | Specs exist and PM-Team's duck has passed them. |
| `in-architecture -> ready-for-dev` | Solution architecture exists, development principles are set, Architect-Team's duck has passed them, and Architect-Team has not vetoed any spec. |
| `ready-for-dev -> in-dev` | Workstreams are decomposed, file scope is assigned, and Dev-Team has enough specs, architecture, principles, and acceptance criteria to build without guessing. |
| `in-dev -> in-acceptance` | All workstream gates are green: tests pass, linters pass, mechanical code review is complete, the Dev duck has passed the work, development principles are observed, and a pull request is open. |
| `in-acceptance -> delivered` | Project-Lead has verified the diff against the requirement acceptance criteria, the PR is merged, issues are closed, and the board is updated. |

### 7.1 Acceptance before merge

Acceptance happens before merge to the default branch.

This prevents unaccepted work from landing. Dev-Team opens the pull request and requests acceptance. Project-Lead reviews the diff against the requirement's acceptance criteria while the code is still on the PR branch. If acceptance fails, Dev-Team fixes the PR and requests acceptance again.

After Project-Lead accepts, Dev-Team may merge. Project-Lead then closes the loop: confirm merge, close issues, update registers, update the board projection, and transition to `delivered`.

This keeps the loop automatable without allowing unaccepted work onto the default branch.

## 8. Parked and blocked

`parked` and `blocked` are not ordinary progress states.

| State | Nature | Entry rule | Exit rule | OKF status |
|---|---|---|---|---|
| `parked` | Deliberate deferral. | Project-Lead records why the requirement is no longer current guidance. | Project-Lead records why the requirement is reactivated, superseded, or left parked. | `deprecated` |
| `blocked` | Temporary stop. | Project-Lead records the unresolved dependency, decision, permission, conflict, or missing input. | Project-Lead records the resolution and returns to the appropriate lifecycle state. | Unchanged |

A parked requirement is not waiting on routine work. It is intentionally deferred. Teams do not keep working it unless Project-Lead reactivates it.

A blocked requirement is expected to move again. The reason must be specific enough that Project-Lead can tell what would unblock it.

Every entry to or exit from `parked` or `blocked` requires a Change log entry in the requirement document.

```yaml
change_log:
  - at: 2026-09-20T22:00:00Z
    version: 7
    from: in-dev
    to: blocked
    by: Project-Lead
    reason: Waiting for repository permission needed by Dev-Team.
  - at: 2026-09-21T15:30:00Z
    version: 8
    from: blocked
    to: in-dev
    by: Project-Lead
    reason: Permission granted; Dev-Team can continue the existing workstream.
```

When exiting `blocked`, Project-Lead chooses the correct current lifecycle state. It is usually the state that was interrupted, but it may be a revised state if the resolution changed the plan.

When exiting `parked`, Project-Lead does not assume the old state is still valid. It re-evaluates the requirement, stakeholder intent, and downstream artifacts.

## 9. Reconciliation

`sync` reconciles documents, registers, and the GitHub Project board.

Documents are the source of truth for `lifecycle`. The board is a projection and is corrected to match. Registers are regenerated from documents.

### 9.1 Sync order of operations

1. Fetch the latest default branch and ensure Project-Lead is operating on the intended repository state.
2. Read `.project-memory/project-link.md` for the GitHub Project id, Status field, and option ids.
3. Scan `docs/requirements/REQ-*.md`.
4. Read each requirement's `id`, `title`, `description`, `lifecycle`, OKF `status`, `priority`, `version`, issue links, PR links, and Project item link.
5. Validate `lifecycle` against the canonical state list.
6. Derive the expected OKF `status` from the mapping.
7. If OKF `status` disagrees and lifecycle is not `blocked`, correct the document status with a version bump and Change log entry.
8. If lifecycle is `blocked`, preserve OKF `status` and record only projection fixes unless a separate valid document edit is needed.
9. Regenerate `docs/requirements/README.md`, `docs/requirements/index.md`, and `.project-memory/requirements-register.md`.
10. For each requirement with a Project item, derive the expected board column from lifecycle.
11. Update GitHub Project Status where the board differs from the derived column.
12. Create missing Project items for approved or later requirements when policy allows and the requirement issue exists.
13. Report unresolved inconsistencies that cannot be corrected safely, such as a missing issue URL needed to create a board item.
14. Persist document and register corrections in the smallest safe commit or PR.

### 9.2 Disagreement rules

| Disagreement | Source of truth | Action |
|---|---|---|
| Requirement `lifecycle` and board Status differ | Requirement document | Move board item to mapped column. |
| Requirement `lifecycle` and OKF `status` differ | Lifecycle mapping | Correct OKF `status`, except `blocked` preserves the current OKF value. |
| Register row and requirement frontmatter differ | Requirement document | Regenerate the register row. |
| Project item missing but requirement issue exists | Requirement document plus project policy | Add or report the item, then set mapped Status. |
| Board column exists without matching requirement document | Requirement documents | Report as orphaned board work; do not invent a requirement. |
| Two documents claim the same `id` | No automatic winner | Stop automatic correction and report the conflict to Project-Lead. |

```bash
# Project-Lead sync
git fetch --all --prune
git pull --ff-only
# scan docs/requirements/REQ-*.md
# regenerate requirement registers
# update GitHub Project Status from mapped lifecycle
# commit or open a reconciliation PR when files changed
```

`sync` never treats the board as authoritative over the requirement document. If a stakeholder moved a card manually, Project-Lead either corrects the card or records an intentional lifecycle transition through the compare-and-swap protocol.
