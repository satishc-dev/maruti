---
name: st-board-ops
description: 'Use by St-Project-Lead when applying GitHub board requests, and by every other software-team agent to understand board authority, safe reads, request emission, issue conventions, pull request rules, and projection reconciliation.'
---
# st-board-ops
Use this skill for GitHub Project, issue, label, and pull request operations.
For full detail, read `.software-team/contracts/GITHUB-INTEGRATION.md`, `.software-team/contracts/ROLES.md`, `.software-team/contracts/HANDOFF-PROTOCOL.md`, and `.software-team/contracts/LIFECYCLE.md`. Bootstrap materializes that directory in the repository; if it is absent, say so and treat this skill as the operative summary rather than inventing the missing detail.
## First rule
Project-Lead is the ONLY agent that writes to the board.
Every other agent emits board requests and never runs a `gh project`, `gh issue create/edit/close`, or `gh label` mutation.
Reading is unrestricted.
## Authority table
| Operation | Project-Lead | Other teams |
|---|---|---|
| `gh project` mutation | Allowed after pre-flight. | Never. Emit a board request. |
| `gh issue create` | Allowed after pre-flight. | Never. Emit a board request. |
| `gh issue edit` | Allowed after pre-flight. | Never. Emit a board request. |
| `gh issue close` | Allowed after pre-flight. | Never. Emit a board request. |
| `gh label create/edit/delete` | Allowed after pre-flight. | Never. Emit a board request. |
| `gh pr create` | Dev-Team normally owns it. | Dev-Team may create its own PR. |
| `gh pr merge` | Not Project-Lead work. | Dev-Team may merge only after Project-Lead records acceptance. |
Board authority never moves with delegation.
A handoff may request a board change; it does not grant board write authority.
## Safe reads
All teams may read GitHub state.
Use reads to verify links, understand context, and report drift.
```bash
gh project list --owner <owner>
gh project view <N> --owner <owner>
gh project field-list <N> --owner <owner> --format json
gh issue view <number>
gh issue list --repo <owner>/<repo>
gh pr view <number>
gh pr list --repo <owner>/<repo>
```
If a read reveals drift, report it through handoff.
Do not repair it unless you are Project-Lead.
## Auth pre-flight
Before Project-Lead performs board or pull request work, run:
```bash
gh auth status
git ls-remote origin HEAD
gh auth status
```
The first command checks CLI auth.
The second checks repository access through `origin`.
The third shows token scopes.
Projects v2 needs the `project` scope.
If absent, the required human action is `gh auth refresh -s project`.
| Failure | Required action |
|---|---|
| `gh auth status` fails | Stop; Project-Lead reports missing GitHub auth. |
| `git ls-remote origin HEAD` fails | Stop; Project-Lead reports missing repository access. |
| `project` scope absent | Stop; Project-Lead reports the needed refresh. |
If pre-flight fails, create nothing.
## Running these commands safely
Every snippet in this package is a portable command line, not a script for one shell. Copilot CLI runs the host's shell, which on Windows is PowerShell.
- **Never chain commands with the `and-and` operator.** PowerShell rejects it before a variable assignment with `Unexpected token '='`, so a chained pre-flight fails without ever running the command that mattered. Run each command separately, or separate them with `;` and check `$LASTEXITCODE` after each.
- Do not assume `2>/dev/null`, heredocs, or `$(...)` behave as they do in bash.
- Prefer several short commands over one long chain. A chain that dies half way is indistinguishable, in a transcript, from one that succeeded.
## Verify every write
A board mutation is not done because the command was issued. It is done when a read confirms it.
1. After any `gh project item-create`, `item-edit`, `issue create`, `issue edit` or `label create`, run a read that proves the effect:
   ```bash
   gh project item-list <N> --owner <owner> --format json
   gh issue view <number>
   gh label list --search <name> --json name
   ```
2. Compare the read against what you intended, and record the observed id or value in the ledger and in the requirement's `links`.
3. If the read does not show the change, the write failed. Report it as an impediment. Never report a board change you have not seen.
4. This matters most at the end of a long run, where a command can be issued but never complete. Treat an unverified write as a failed write.
No issue, label, project, project item, branch, or pull request is half-created.
## Project detection
The board title is `<repo> Delivery`.
Detection order:
1. Read `.project-memory/project-link.md`.
2. Use the recorded project if present.
3. Otherwise list projects for the owner.
4. Match exact title `<repo> Delivery`.
5. Only if no exact match exists, create the project.
`gh project create` is not idempotent.
It can create duplicate projects with the same title.
Exact-title match before creation.
## Status column set
The Project has a single-select `Status` field with these options:
| Status option |
|---|
| Intake |
| In Review |
| Ready for Discovery |
| In Discovery |
| In Spec |
| In Architecture |
| Ready for Dev |
| In Dev |
| In Acceptance |
| Done |
| Parked |
| Blocked |
Persist option ids in `.project-memory/project-link.md`.
Do not hard-code option ids elsewhere.
## Board projection rule
The board is a projection corrected from documents.
The board never corrects documents.
If lifecycle and board disagree, lifecycle wins.
If register and requirement disagree, requirement wins.
If an orphaned board row exists, report it; do not invent a requirement.
## Issue title conventions
| Level | Title | Label |
|---|---|---|
| Requirement | `[REQ-NNN] <title>` | `requirement` when custom issue type is unavailable. |
| Feature | `[REQ-NNN] <feature title>` | `feature` |
| Story | `<feature title>: <story title>` | `story` |
One Requirement has one Requirement issue.
One Requirement may have many Feature issues.
One Feature may have many Story issues.
## Requirement issues
Prefer custom issue type `Requirement`.
Detect support before use.
If unavailable, use label fallback `requirement`.
Record the chosen mode in `.project-memory/project-link.md`.
A Requirement issue links to the requirement document, Project item, child Feature issues, and workstreams when known.
## Feature issues
Feature issue title is `[REQ-NNN] <feature title>`.
Body includes the spec link on the default branch, parent Requirement issue, `workstream_id` when assigned, and child Story issues when known.
## Story issues
Story issue title is `<feature title>: <story title>`.
Body includes the spec link, parent Feature issue, parent Requirement issue, `workstream_id` when assigned, and acceptance criteria copied or referenced from the spec.
## Parenting
Prefer native GitHub sub-issues.
Use native parent-child relationships when available.
Fallback when unavailable:
| Fallback | Meaning |
|---|---|
| `parent:REQ-NNN` label | Marks Requirement parent by id. |
| `Parent: #<n>` in body | Human-readable parent link. |
The fallback is not a real relationship and can go stale.
Project-Lead corrects it from documents during sync.
## Pull requests
Dev-Team owns implementation pull requests.
Project-Lead owns acceptance.
PR title is `[REQ-NNN] <workstream title>`.
PR body includes requirement id, workstream id, workstream title, story issues it closes, spec link on default branch, validation summary, and acceptance request.
Use closing syntax only for story issues the PR really delivers.
## Acceptance precedes merge
Project-Lead accepts before merge to default branch.
Dev-Team may merge only after Project-Lead records acceptance and grants permission through the handoff envelope.
After merge, Project-Lead updates board projection and Project Memory as needed.
## Board request queue
Non-Project-Lead teams request changes in `board_requests[]`.
| Field | Meaning |
|---|---|
| `action` | `item.create`, `item.link`, `item.status`, `item.label`, `item.comment`, or `item.close`. |
| `target.kind` | `requirement`, `feature`, `story`, `project_item`, `issue`, or `pull_request`. |
| `target.ref` | Stable reference. |
| `args` | Action-specific arguments. |
| `reason` | Why the change is needed. |
| `requested_by` | Requesting team. |
Project-Lead validates target existence, status option, lifecycle fit, acceptance order, authority, and reason.
Project-Lead may reject a request with a recorded reason.
## Applying as Project-Lead
Before applying:
1. Run auth pre-flight.
2. Read the requirement and ledger request.
3. Validate target existence or safe creation.
4. Validate status option names against `project-link.md`.
5. Validate the request does not bypass acceptance.
6. Apply the smallest mutation set.
7. Record issue numbers, PR numbers, Project item ids, and URLs.
8. Append results to the ledger or Project Memory as required.
## Failure handling
Do not ignore GitHub failures.
For rate limits, stop the batch, inspect reset time when available, and report the paused state.
For partial creation, record what exists, re-read GitHub, and reuse matching items.
For missing permissions, stop and return the failure to Project-Lead.
Do not try alternate mutation paths that evade this contract.
## Non-Project-Lead behavior
Read GitHub if needed.
Do not mutate Project, issue, or label state.
Put requested changes in `board_requests[]` with reason and evidence.
Let Project-Lead apply or reject.
