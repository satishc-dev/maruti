---
name: st-handoff
description: 'Use whenever a software-team agent hands work to another team, receives work, consults a peer, escalates an impediment, requests a lifecycle transition, or emits a board request through the durable ledger.'
---
# st-handoff
Use this skill whenever you hand work to another team, receive work, consult a peer, or escalate.
For full detail, read `docs/HANDOFF-PROTOCOL.md`, `docs/LIFECYCLE.md`, `docs/GITHUB-INTEGRATION.md`, and `docs/ROLES.md`.
## Core rule
Handoff is data.
Handoff is recorded.
Handoff is acknowledged.
Do not hand off by telling a human to run a command.
Do not act on an envelope without receipting it.
Do not silently drop an escalation.
## Ledger
Each requirement has one committed ledger:
```text
.software-team/REQ-NNN/ledger.md
```
The ledger is append-only.
Every team appends its own entries.
No team edits, deletes, reorders, or rewrites another team entry.
Corrections are later appended events.
Receipts refer to `event_id`, not line numbers.
## Envelope schema
Every event has these required fields.
Use explicit `null` and empty lists where required.
| Field | Required content |
|---|---|
| `event_id` | Unique `EV-<REQ>-<seq>`. |
| `at` | ISO-8601 timestamp with explicit UTC offset. |
| `from` | Sending team id. |
| `to` | Receiving team id. |
| `req` | `REQ-NNN`. |
| `workstream` | `REQ-NNN/ws<k>` or `null`. |
| `gate` | Lifecycle gate. |
| `intent` | `commission`, `deliver`, `consult`, `escalate`, `accept`, `reject`, or `receipt`. |
| `verdict` | `passed`, `not-passed`, `vetoed`, `accepted`, `rejected`, or `null`. |
| `summary` | One line. |
| `artifacts` | List, empty when none. |
| `board_requests` | List, empty when none. |
| `lifecycle_request` | Object or `null`. |
| `receipt_of` | Event id or `null`. |
| `actor` | OKF actor string. |
Artifact records name a durable path or stable URL and include `path`, `kind`, and `owner`.
Do not make machine-local `.scrum/` state the only durable handoff evidence.
## Receipts
Every envelope with `intent` other than `receipt` gets a receipt.
Receipt before acting.
Receipt `accepted` when you can act.
Receipt `rejected` with a reason when you cannot act.
Malformed or impossible envelopes still get receipts.
Receipt procedure:
1. Read the envelope addressed to your team.
2. Append a receipt naming `receipt_of`.
3. State `verdict: accepted` or `verdict: rejected`.
4. Act only after the receipt exists.
An unreceipted envelope is incomplete work.
If you find one addressed to your team, receipt it before continuing.
## Commissioning
Project-Lead commissions teams with `intent: commission`.
The receiver receipts before acting and returns `deliver`, `escalate`, or `reject`.
| Team | Required inputs |
|---|---|
| Research-Team | Requirement when present, question, scope, constraints, prior references and findings. |
| UX-Team | Requirement, user-visible hypothesis, project context, relevant research. |
| PM-Team | Approved requirement, UX brief when present, research, known architecture constraints. |
| Architect-Team | Requirement, specs, UX brief when present, research, repository constraints, current architecture. |
| Dev-Team | Requirement, specs, architecture, principles, workstream record, branch, worktree, file scope, acceptance criteria. |
A commission transfers work only to the named receiver.
It does not transfer document ownership.
## Peer consultation
Consultation is a question and answer.
It does not transfer ownership.
Use `write_agent` and `read_agent` for peer exchange.
Record the question and answer in the ledger with `intent: consult`.
PM-Team and Dev-Team may consult Architect-Team mid-flight.
A consultation answer is advisory unless it includes `verdict: vetoed` from an agent with veto authority.
Peer consultation steps:
1. Append consult envelope.
2. Send the question with `write_agent`.
3. Collect the reply with `read_agent`.
4. Append the answer.
5. Continue ownership in the original team.
## Escalation envelopes
Use `intent: escalate` when a team cannot proceed safely.
Project-Lead must receipt every escalation with a decision.
Every escalation states:
| Required prose | Meaning |
|---|---|
| What is impeded | Exact work that cannot proceed. |
| Decision needed | Decision, permission, input, dependency, or scope change required. |
| Team recommendation | Preferred resolution when known. |
| Already tried | Evidence that the team investigated. |
Escalation is never silent.
Do not continue by guessing when a real decision is needed.
## Lifecycle transition requests
Only Project-Lead writes requirement lifecycle.
Other teams request transitions through `lifecycle_request`.
Every lifecycle request uses compare-and-swap and includes `expect_version`.
| Field | Meaning |
|---|---|
| `from` | Observed lifecycle. |
| `to` | Requested lifecycle. |
| `expect_version` | Observed requirement version. |
Project-Lead accepts, rejects, parks, or records an impediment state through a receipt.
The requesting team does not edit lifecycle frontmatter.
## Board requests
Project-Lead is the only board writer.
Other teams place board requests in `board_requests[]`.
Use the schema from `docs/GITHUB-INTEGRATION.md`.
| Field | Meaning |
|---|---|
| `action` | `item.create`, `item.link`, `item.status`, `item.label`, `item.comment`, or `item.close`. |
| `target` | Target kind and stable reference. |
| `args` | Action-specific arguments. |
| `reason` | Why the change is needed. |
| `requested_by` | Requesting team. |
A refused board request does not transfer board authority.
## Delivery envelopes
Use `intent: deliver` when returning completed team work.
Include artifacts, validation evidence, duck exchange evidence, lifecycle requests when gates are met, and board requests when projection changes are needed.
Your duck must pass the work before you claim team completion.
At least two rounds always occur.
Record the exchange in the ledger.
## Resumption
When re-entering mid-flight:
1. Read `.software-team/REQ-NNN/ledger.md` from the top.
2. Parse fenced YAML envelopes.
3. Find the last envelope addressed to your team.
4. Check whether a later receipt names it.
5. Receipt it before acting if needed.
6. Find the latest accepted commission, consultation answer, escalation decision, or acceptance decision relevant to you.
7. Read every named artifact.
8. Read the requirement and your owned paths.
9. Continue from the last acknowledged state.
The ledger controls in-flight handoff.
Documents control artifact content.
Local `.scrum/` notes do not override the ledger.
## Prohibitions
| Never | Instead |
|---|---|
| Hand off by telling a human to run a command. | Append an envelope. |
| Act without receipting. | Append a receipt first. |
| Treat chat prose as durable handoff. | Record the envelope. |
| Write another team owned path. | Propose to the owner. |
| Mutate the board outside Project-Lead. | Emit a board request. |
| Edit lifecycle outside Project-Lead. | Emit a lifecycle request. |
| Drop an escalation silently. | Receipt and resolve or correct it. |
| Reuse an `event_id`. | Allocate the next sequence. |
| Rewrite another team ledger entry. | Append a correction. |
| Merge before acceptance. | Wait for Project-Lead acceptance. |
## Quick check
Confirm ledger path, unique event id, timestamp offset, all required fields, receipt, durable artifacts, `expect_version`, board request reason, and escalation decision need.

## Review Record entries are not yours to read

The ledger also carries `Review Record` entries, appended by each team''s duck after
every review round.

**If you are a lead or crew agent, skip them.** When you read the ledger — for
resumption, for context, for anything — read the handoff envelopes and receipts and
pass over any entry whose `type` is `Review Record`. Do not open them, do not
summarise them, and do not reason about their contents.

Those entries exist for audit: so a human, or Project-Lead handling an escalation,
can confirm a review verdict was earned. They contain the reviewer''s internal
accounting, which is deliberately withheld from the agent being reviewed. Reading
them would tell you how your work is being measured, and an agent that knows how it
is measured starts aiming at the measurement instead of the work. That makes the
work worse, which is the entire reason for the arrangement.

This is a rule, not a lock. The file is readable and nothing stops you. Follow it
anyway — and if you find yourself curious about the contents, that is precisely the
impulse the rule exists to stop.

Project-Lead reads `Review Record` entries only when resolving an escalation, and
only to confirm that a deadlock is genuine.