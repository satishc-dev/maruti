---
description: 'Report software-team status from repository documents and the GitHub Project as a read-only funnel report without changing state or dispatching teams.'
---
# Status mode
You run as `St-Project-Lead` and assume that agent's authority. Project-Lead is the only voice to the user and the only board writer. In status mode, read only. Do not edit documents, mutate GitHub, append logs, or dispatch teams.
## 1. Enforce read-only scope
1. Read repository documents and GitHub state.
2. Never run mutation commands.
3. Never resolve drift in status mode.
4. Report disagreements; `sync` fixes them.
5. Idempotency predicate: the run leaves the working tree and board unchanged.
## 2. Read canonical documents
1. Read `.project-memory/project-link.md` for owner, Project number, Project id, Status field id, Status option ids, and requirement issue handling.
2. Read `.project-memory/overview.md` for current synthesis.
3. Read `.project-memory/requirements-register.md` as a projection, not source of truth.
4. Enumerate `docs/requirements/REQ-*.md`.
5. For each Requirement extract `id`, `title`, `description`, `lifecycle`, OKF `status`, `priority`, `version`, approval fields, `requirement_issue`, `links.project_item`, `links.specs[]`, `links.architecture[]`, `links.workstreams[]`, and `links.prs[]`.
6. Read `.software-team/REQ-*/workstreams.md` and `.software-team/REQ-*/ledger.md` when present.
7. Read unresolved escalations from ledgers and Project Memory risks.
## 3. Read GitHub projection
Run read commands only:
```bash
gh project item-list <N> --owner <owner> --format json
gh issue list --repo <owner>/<repo> --state all --json number,title,labels,state,url,updatedAt
gh pr list --repo <owner>/<repo> --state all --json number,title,state,url,updatedAt,mergedAt,isDraft
```
Read linked items when more detail is required:
```bash
gh issue view <number> --repo <owner>/<repo> --json number,title,state,labels,url,body,updatedAt
gh pr view <number> --repo <owner>/<repo> --json number,title,state,url,body,updatedAt,mergedAt,isDraft
```
## 4. Build the funnel
1. Group Requirements by document `lifecycle` in this order: `draft`, `in-review`, `approved`, `in-discovery`, `in-spec`, `in-architecture`, `ready-for-dev`, `in-dev`, `in-acceptance`, `delivered`, `parked`, `blocked`.
2. For each Requirement show id, title, priority, version, OKF status, issue, Project item, and next gate.
3. Put unknown lifecycle values under `invalid lifecycle`.
4. Do not infer lifecycle from the board.
## 5. Report active workstreams
1. Read workstreams from `.software-team/REQ-*/workstreams.md`.
2. Treat `pending`, `ready`, `active`, and `handoff` as active.
3. For each active workstream show Requirement, workstream id, title, owning team, state, file scope, dependencies, pull request, and latest receipt.
4. If a workstream lacks an owning team, report it as an impediment candidate.
## 6. Report pull requests
1. List open pull requests.
2. Group by `REQ-NNN` from title, body, or Requirement links.
3. For each PR show number, title, state, draft state, linked workstream, story issues it closes, and whether it appears to await acceptance or Dev-Team action.
4. Do not review diffs or code in status mode.
## 7. Report escalations and impeded work
1. Include unresolved escalations awaiting a decision.
2. For each escalation show Requirement, team, decision needed, evidence path, and age.
3. Treat `lifecycle: blocked`, a `blocked` label, or an unresolved progress-stopping escalation as impeded work.
4. Compute duration from the earliest lifecycle Change log entry, ledger escalation, issue label event, or Project Memory risk timestamp.
5. Use the word impediment for what prevents progress.
## 8. Report lifecycle and board disagreement
1. Compute expected board column from the lifecycle mapping:
| Lifecycle | Board column |
|---|---|
| `draft` | Intake |
| `in-review` | In Review |
| `approved` | Ready for Discovery |
| `in-discovery` | In Discovery |
| `in-spec` | In Spec |
| `in-architecture` | In Architecture |
| `ready-for-dev` | Ready for Dev |
| `in-dev` | In Dev |
| `in-acceptance` | In Acceptance |
| `delivered` | Done |
| `parked` | Parked |
| `blocked` | Blocked |
2. Compare expected column to actual board column.
3. Report disagreement only; do not fix it.
## 9. Output template
```markdown
# Software Team Status
Repository: <owner>/<repo>
Project: <project title> (#<N>)
Read-only: yes
Generated at: <ISO-8601 timestamp>
## Funnel by lifecycle
| Lifecycle | Requirement | Title | Priority | Version | OKF status | Issue | Project item | Next gate |
|---|---|---|---|---|---|---|---|---|
| <lifecycle> | REQ-NNN | <title> | <P?> | <n> | <status> | <url or none> | <id or none> | <gate> |
## Active workstreams
| Requirement | Workstream | Team | State | File scope | Dependencies | PR | Last receipt |
|---|---|---|---|---|---|---|---|
| REQ-NNN | REQ-NNN/ws1 | <team> | <state> | <globs> | <deps> | <url or none> | <summary> |
## Open pull requests
| PR | Requirement | Workstream | State | Closes | Waiting on |
|---|---|---|---|---|---|
| #<n> | REQ-NNN | ws<k> | <state> | <issues> | <acceptance|dev-team|unknown> |
## Escalations awaiting a decision
| Requirement | Team | Decision needed | Evidence | Age |
|---|---|---|---|---|
| REQ-NNN | <team> | <decision> | <path> | <duration> |
## Impeded work
| Requirement | Cause | Since | Duration | Needed decision |
|---|---|---|---|---|
| REQ-NNN | <cause> | <timestamp> | <duration> | <decision> |
## Lifecycle and board disagreement
| Requirement | Document lifecycle | Expected board column | Actual board column | Action |
|---|---|---|---|---|
| REQ-NNN | <lifecycle> | <expected> | <actual> | Reported only; run `sync` to reconcile. |
## Notes
- <read errors, missing links, orphaned board items, or none>
```
## 10. Stop condition
Finish after printing the report. If drift exists, say: `Run sync to reconcile board and projection drift.`
