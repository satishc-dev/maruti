---
type: Contract
title: Software Team — Handoff Protocol
description: Machine-readable handoff, receipt, lifecycle request, board request, consultation, escalation, and resumption contract for the software-team package.
status: stable
---
# Handoff Protocol
This contract defines how the six teams pass work without a human relay.
It joins `ROLES.md`, `LIFECYCLE.md`, `PARALLELISM.md`, `GITHUB-INTEGRATION.md`, and `GLOSSARY.md`.
Where this contract disagrees with `ROLES.md`, `ROLES.md` wins.
Where this contract references board requests, `GITHUB-INTEGRATION.md` is the authority.
## 1. Principles
| Principle | Rule |
|---|---|
| Handoff is data. | A handoff is a typed envelope, not an instruction. |
| Handoff is recorded. | Every handoff is appended to the requirement ledger. |
| Handoff is addressed. | Every envelope names sender, receiver, requirement, and gate. |
| Handoff is acknowledged. | Every non-receipt envelope receives a receipt. |
| Silence is incomplete. | An unacknowledged handoff is incomplete work. |
| Humans do not relay teams. | No team hands off by asking a human to run another team. |
| Authority stays fixed. | Project-Lead remains lifecycle writer and board writer. |
The ledger is the authority for in-flight state.
The documents are the authority for content.
The board is a projection.
## 2. The ledger
Each requirement has one committed ledger.
```text
.software-team/REQ-NNN/ledger.md
```
The ledger is committed because parallel teams may run on different machines, branches, and sessions.
They must see the same handoff state after fetch and merge.
`.scrum/` is machine-local and ignored; it may hold execution notes, but it is not shared state.
Ledger rules:
| Rule | Meaning |
|---|---|
| Append-only | Entries are added newest-last. |
| Shared writer | Every team appends its own entries. |
| No rewrite | No team edits, deletes, reorders, or rewrites another team's entries. |
| Correction by append | A team fixes its own earlier event by appending a later event. |
| Stable reference | Receipts refer to `event_id`, never to a line number. |
File structure:
```yaml
---
type: Handoff Record
title: REQ-NNN handoff ledger
status: stable
req: REQ-NNN
---
```
After frontmatter, entries are newest-last.
Each entry has an event heading, a fenced `yaml` envelope, and optional prose.
The YAML is the machine-readable record.
The prose may explain context.
The repository must set union merge for ledgers.
```gitattributes
.software-team/*/ledger.md merge=union
```
The rule makes concurrent branches concatenate appended entries instead of conflicting on ordinary handoff writes.
Project-Lead must normalise the ledger after any merge: keep complete events, preserve `event_id`, keep newest-last order, remove only identical duplicate events, and preserve differing duplicates with a later resolution event.
## 3. The envelope
Every event uses this core schema.
```yaml
event_id: "EV-REQ-014-006"        # string, required, unique. Format: EV-<REQ>-<seq>.
at: "2026-09-20T22:20:00+00:00"  # string, required, ISO-8601 with UTC offset.
from: "PM-Team"                  # string, required, sending team id.
to: "Project-Lead"               # string, required, receiving team id.
req: "REQ-014"                   # string, required, requirement id.
workstream: null                  # string or null, required, full form REQ-NNN/ws<k> when used.
gate: "in-spec"                  # string, required, lifecycle gate this relates to.
intent: "deliver"                # enum, required: commission | deliver | consult | escalate | accept | reject | receipt.
verdict: "passed"                # enum or null, required: passed | not-passed | vetoed | accepted | rejected | null.
summary: "Specs are ready."      # string, required, one line.
artifacts:                       # list, required, empty when none.
  - path: "docs/specs/REQ-014/export-format-selection.md" # string, required, repo-relative path or stable URL.
    kind: "feature_spec"                               # string, required, artifact kind.
    owner: "PM-Team"                                   # string, required, owning team id.
board_requests: []              # list, required, conforming to GITHUB-INTEGRATION.md.
lifecycle_request: null          # object or null, required: { from:, to:, expect_version: }.
memory_proposals: []          # list, required, empty when none; proposal schema is in MEMORY-SCHEMA.md.
receipt_of: null                 # string or null, required, event_id acknowledged by a receipt.
actor: "software-team-pm/0.1.0"    # string, required. OKF actor per OKF-PROFILE.md.
```
Lifecycle request object:
```yaml
lifecycle_request:
  from: "in-spec"        # string, required, observed lifecycle.
  to: "in-architecture"  # string, required, requested lifecycle.
  expect_version: 4      # integer, required, observed version for compare-and-swap.
```
`board_requests[]` uses the board request queue in `GITHUB-INTEGRATION.md`.
This document does not redefine that schema.
## 4. Worked examples
### 4.1 Project-Lead commissions Research-Team
```yaml
event_id: EV-REQ-021-001
at: 2026-09-20T22:30:00+00:00
from: Project-Lead
to: Research-Team
req: REQ-021
workstream: null
gate: approved
intent: commission
verdict: null
summary: "Research import validation patterns before specification."
artifacts:
  - { path: "docs/requirements/REQ-021-bulk-import-validation.md", kind: "requirement", owner: Project-Lead }
  - { path: ".project-memory/references/import-systems.md", kind: "project_memory_reference", owner: Project-Lead }
board_requests: []
lifecycle_request: null
memory_proposals: []
receipt_of: null
actor: "software-team-project-lead/0.1.0"
```
### 4.2 PM-Team delivers specs
```yaml
event_id: EV-REQ-014-006
at: 2026-09-20T22:45:00+00:00
from: PM-Team
to: Project-Lead
req: REQ-014
workstream: null
gate: in-spec
intent: deliver
verdict: passed
summary: "Feature specs are ready for architecture."
artifacts:
  - { path: "docs/specs/REQ-014/export-format-selection.md", kind: "feature_spec", owner: PM-Team }
  - { path: "docs/specs/REQ-014/export-preview.md", kind: "feature_spec", owner: PM-Team }
board_requests:
  - action: item.create
    target: { kind: feature, ref: "REQ-014.feature.export-format-selection" }
    args: { title: "[REQ-014] Export format selection", labels: ["feature"], spec_path: "docs/specs/REQ-014/export-format-selection.md", parent_requirement: "REQ-014", workstream_id: "ws1" }
    reason: "Spec is ready and the feature needs traceability before development."
    requested_by: PM-Team
lifecycle_request: { from: "in-spec", to: "in-architecture", expect_version: 4 }
memory_proposals: []
receipt_of: null
actor: "software-team-pm/0.1.0"
```
### 4.3 Dev-Team requests acceptance
```yaml
event_id: EV-REQ-014-018
at: 2026-09-21T01:15:00+00:00
from: Dev-Team
to: Project-Lead
req: REQ-014
workstream: "REQ-014/ws1"
gate: in-dev
intent: deliver
verdict: passed
summary: "Workstream ws1 is ready for Project-Lead acceptance."
artifacts:
  - { path: "https://github.com/example/repo/pull/42", kind: "pull_request", owner: Dev-Team }
  - { path: ".worktrees/REQ-014/ws1/", kind: "worktree", owner: Dev-Team }
board_requests:
  - action: item.status
    target: { kind: project_item, ref: "REQ-014" }
    args: { status: "In Acceptance", project_item_id: "PVTI_..." }
    reason: "Pull request is ready for Project-Lead acceptance."
    requested_by: Dev-Team
  - action: item.comment
    target: { kind: pull_request, ref: "#42" }
    args: { body: "Workstream REQ-014/ws1 is ready for acceptance. Validation is recorded in the PR body." }
    reason: "Project-Lead needs a direct acceptance handoff on the PR."
    requested_by: Dev-Team
lifecycle_request: { from: "in-dev", to: "in-acceptance", expect_version: 8 }
memory_proposals: []
receipt_of: null
actor: "software-team-dev/0.1.0"
```
## 5. Receipts
Every envelope with `intent` other than `receipt` must be acknowledged by a receipt envelope naming `receipt_of`.
A receipt states `accepted` or `rejected` with a reason.
If a team cannot act, it still receipts with `verdict: rejected` and a reason.
That makes stalls visible instead of silent.
```yaml
event_id: EV-REQ-014-019
at: 2026-09-21T01:18:00+00:00
from: Project-Lead
to: Dev-Team
req: REQ-014
workstream: "REQ-014/ws1"
gate: in-dev
intent: receipt
verdict: accepted
summary: "Acceptance review started for PR #42."
artifacts: []
board_requests: []
lifecycle_request: null
memory_proposals: []
receipt_of: EV-REQ-014-018
actor: "software-team-project-lead/0.1.0"
```
Timeout behaviour:
1. Read the envelope addressed to the team.
2. Receipt `accepted` before acting when the team can act.
3. Receipt `rejected` with a reason when the team cannot act.
4. Project-Lead treats any unreceipted envelope found later as an escalation to resolve.
## 6. Commissioning a team
Project-Lead commissions with `intent: commission`.
The receiver receipts before acting.
The receiver returns `deliver`, `escalate`, or `reject`.
| Team | Receives | Must return |
|---|---|---|
| Research-Team | Requirement when present at `docs/requirements/REQ-NNN-<slug>.md`; research question; scope; constraints; prior references under `.project-memory/`; prior findings under `docs/research/`. | Findings under `docs/research/<topic>/`; cited evidence; verdict; artifacts; open questions; impediments. |
| Architect-Team | Requirement; specs under `docs/specs/REQ-NNN/`; UX brief under `docs/ux/REQ-NNN/` when present; research findings; repository constraints; current `docs/architecture/`. | Solution architecture, ADRs when needed, and development principles under `docs/architecture/`; verdict; vetoes with `verdict: vetoed`; impediments. |
| UX-Team | Requirement; user-visible hypothesis; product context from `.project-memory/`; research findings; output path `docs/ux/REQ-NNN/`. | UX brief under `docs/ux/REQ-NNN/`, or withdrawal stating no user-visible surface; verdict; artifacts; impediments. |
| PM-Team | Approved requirement; UX brief when present; research findings; known architecture constraints; output path `docs/specs/REQ-NNN/`; out-of-scope statements. | Feature specs under `docs/specs/REQ-NNN/`; stories; acceptance criteria; verdict; board requests for feature and story issues; impediments. |
| Dev-Team | Requirement; feature specs; solution architecture; development principles; workstream record; branch; worktree `.worktrees/REQ-NNN/ws<k>/`; file scope; dependencies; acceptance criteria. | Pull request; validation summary; verdict; board requests for acceptance status or PR comment; impediments; no merge before Project-Lead acceptance. |
Exact commission payload pattern:
```yaml
event_id: EV-REQ-NNN-SEQ
at: "<ISO-8601 with UTC offset>"
from: Project-Lead
to: "<Research-Team | Architect-Team | UX-Team | PM-Team | Dev-Team>"
req: REQ-NNN
workstream: "<REQ-NNN/ws<k> or null>"
gate: "<current lifecycle gate>"
intent: commission
verdict: null
summary: "<one-line dispatch>"
artifacts:
  - { path: "docs/requirements/REQ-NNN-<slug>.md", kind: "requirement", owner: Project-Lead }
  - { path: "<team-specific input path>", kind: "<team-specific kind>", owner: "<owning team>" }
board_requests: []
lifecycle_request: null
memory_proposals: []
receipt_of: null
actor: "software-team-project-lead/0.1.0"
```
| Team | Required input paths in `artifacts[]` |
|---|---|
| Research-Team | `docs/requirements/REQ-NNN-<slug>.md` when present; `.project-memory/references/<topic>.md` when present; `docs/research/<prior-topic>/` when relevant. |
| Architect-Team | `docs/requirements/REQ-NNN-<slug>.md`; `docs/specs/REQ-NNN/`; `docs/ux/REQ-NNN/` when present; `docs/research/<topic>/` when relevant. |
| UX-Team | `docs/requirements/REQ-NNN-<slug>.md`; `.project-memory/overview.md`; `docs/research/<topic>/` when relevant. |
| PM-Team | `docs/requirements/REQ-NNN-<slug>.md`; `docs/ux/REQ-NNN/` when present; `docs/research/<topic>/` when relevant. |
| Dev-Team | `docs/requirements/REQ-NNN-<slug>.md`; `docs/specs/REQ-NNN/`; `docs/architecture/`; `.worktrees/REQ-NNN/ws<k>/`. |
## 7. Peer consultation
Consultation is distinct from handoff.
It is a question and an answer.
It does not transfer ownership.
It is recorded in the ledger as `intent: consult`.
PM-Team and Dev-Team may consult Architect-Team mid-flight.
Mechanism: send the question with `write_agent`, end the turn, then read the reply with `read_agent` when it arrives.
```yaml
tool: write_agent
arguments: { agent_id: "<architect-agent-id>", message: "<question with req, paths, constraints, and desired decision>" }
```
```yaml
tool: read_agent
arguments: { agent_id: "<architect-agent-id>" }
```
The answer is advisory unless it is a veto.
Architect vetoes are not advisory.
They are binding and must be recorded with `verdict: vetoed`.
```yaml
event_id: EV-REQ-030-012
at: 2026-09-21T00:10:00+00:00
from: PM-Team
to: Architect-Team
req: REQ-030
workstream: null
gate: in-spec
intent: consult
verdict: null
summary: "Can account setup depend on the existing profile service contract?"
artifacts:
  - { path: "docs/specs/REQ-030/account-setup.md", kind: "draft_feature_spec", owner: PM-Team }
board_requests: []
lifecycle_request: null
memory_proposals: []
receipt_of: null
actor: "software-team-pm/0.1.0"
```
```yaml
event_id: EV-REQ-030-013
at: 2026-09-21T00:18:00+00:00
from: Architect-Team
to: PM-Team
req: REQ-030
workstream: null
gate: in-spec
intent: consult
verdict: vetoed
summary: "Do not depend on the profile service contract; it cannot support the required consistency."
artifacts:
  - { path: "docs/architecture/decisions/ADR-012-profile-consistency.md", kind: "adr", owner: Architect-Team }
board_requests: []
lifecycle_request: null
memory_proposals: []
receipt_of: EV-REQ-030-012
actor: "software-team-architect/0.1.0"
```
## 8. Lifecycle transition requests
Teams do not edit requirement lifecycle.
Only Project-Lead does that, using the compare-and-swap rules in `LIFECYCLE.md`.
A team requests transition through `lifecycle_request` with `expect_version`.
Project-Lead validates the gate, applies or refuses, and receipts the outcome.
```yaml
event_id: EV-REQ-030-021
at: 2026-09-21T02:00:00+00:00
from: Architect-Team
to: Project-Lead
req: REQ-030
workstream: null
gate: in-architecture
intent: deliver
verdict: passed
summary: "Architecture and development principles are ready for development."
artifacts:
  - { path: "docs/architecture/REQ-030/solution.md", kind: "solution_architecture", owner: Architect-Team }
board_requests: []
lifecycle_request: { from: "in-architecture", to: "ready-for-dev", expect_version: 6 }
memory_proposals: []
receipt_of: null
actor: "software-team-architect/0.1.0"
```
```yaml
event_id: EV-REQ-030-022
at: 2026-09-21T02:05:00+00:00
from: Project-Lead
to: Architect-Team
req: REQ-030
workstream: null
gate: in-architecture
intent: receipt
verdict: accepted
summary: "Transition applied: ready-for-dev at version 7."
artifacts:
  - { path: "docs/requirements/REQ-030-onboarding.md", kind: "requirement", owner: Project-Lead }
board_requests: []
lifecycle_request: null
memory_proposals: []
receipt_of: EV-REQ-030-021
actor: "software-team-project-lead/0.1.0"
```
## 9. Board requests
Teams emit board requests in `board_requests[]`.
Project-Lead applies them.
The schema is the board request queue in `GITHUB-INTEGRATION.md`.
Project-Lead validates each request against lifecycle and repository state.
Project-Lead may refuse with a reason recorded in the receipt.
A refused board request does not transfer board authority.
## 10. Escalation envelopes
Escalation uses `intent: escalate`.
Required content: what is impeded, what decision is needed, what the team recommends, and what it has already tried.
Project-Lead must receipt every escalation with a decision.
```yaml
event_id: EV-REQ-030-030
at: 2026-09-21T03:00:00+00:00
from: Dev-Team
to: Project-Lead
req: REQ-030
workstream: "REQ-030/ws1"
gate: in-dev
intent: escalate
verdict: not-passed
summary: "Impediment: file scope excludes a required validation module."
artifacts:
  - { path: "docs/specs/REQ-030/account-setup.md", kind: "feature_spec", owner: PM-Team }
  - { path: ".worktrees/REQ-030/ws1/", kind: "worktree", owner: Dev-Team }
board_requests:
  - action: item.label
    target: { kind: issue, ref: "REQ-030" }
    args: { add: ["needs-decision"] }
    reason: "Project-Lead decision is needed before implementation can continue."
    requested_by: Dev-Team
lifecycle_request: null
memory_proposals: []
receipt_of: null
actor: "software-team-dev/0.1.0"
```
Required prose:
```text
What is impeded: REQ-030/ws1 cannot implement server-side validation within the declared file scope.
Decision needed: expand the file scope, create a second workstream, or revise the spec.
Team recommendation: re-decompose into ws1 UI and ws2 validation service.
Already tried: inspected the validation module, attempted an adapter inside file scope, and confirmed it would duplicate existing rules.
```
Project-Lead receipts the escalation with `verdict: accepted` when it records a decision, or `verdict: rejected` when the escalation is malformed and must be corrected.
## 11. Resumption
A team re-entering mid-flight reconstructs state this way:
1. Read `.software-team/REQ-NNN/ledger.md` from the top.
2. Parse each fenced YAML block.
3. Find the last envelope addressed to the team.
4. Check whether a later receipt names that `event_id`.
5. If the envelope is addressed to this team and has no receipt, receipt it before acting.
6. Find the latest accepted commission, consultation answer, escalation decision, or acceptance decision relevant to the team.
7. Read the artifacts named there.
8. Read the requirement document and the team's owned artifact paths.
9. Continue from the last acknowledged state.
The ledger is the authority for in-flight state.
The documents are the authority for content.
Local `.scrum/` notes do not override the ledger.
## 12. What breaks the protocol
| Prohibited behaviour | Reason |
|---|---|
| Handing off by telling a human to run a command. | Handoff must be recorded data. |
| Acting on an envelope without receipting it. | The sender cannot know the handoff was accepted. |
| Treating chat prose as the durable handoff. | Chat is not shared repository state. |
| Writing to another team's owned paths. | It violates one writer per surface. |
| Mutating the board directly outside Project-Lead. | It violates board authority. |
| Editing requirement lifecycle outside Project-Lead. | It violates compare-and-swap ownership. |
| Silently dropping an escalation. | The impediment becomes invisible. |
| Reusing an `event_id`. | Receipts become ambiguous. |
| Rewriting another team's ledger entry. | Audit history is lost. |
| Merging before acceptance. | Unaccepted work reaches the default branch. |
