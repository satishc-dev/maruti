---
type: Integration Contract
title: Software Team — GitHub Integration
description: Board, issue, label, and pull request contract for the software-team package.
status: stable
---

# GitHub Integration

This contract defines how the `software-team` package uses GitHub.
Scope is GitHub only. Azure DevOps is out of scope for this package.
Project Memory is the durable project context. The GitHub Project is the delivery projection.
The teams are Project-Lead, Research-Team, Architect-Team, PM-Team, Dev-Team, and UX-Team.

## 1. Authority

Project-Lead is the sole board writer.
Every other team emits requested board changes in its handoff envelope. Project-Lead validates those requests and applies them.
Concrete consequence:
- No team except Project-Lead runs `gh project` mutation commands.
- No team except Project-Lead runs `gh issue create`.
- No team except Project-Lead runs `gh issue edit`.
- No team except Project-Lead runs `gh issue close`.
- No team except Project-Lead runs `gh label create`, `gh label edit`, or `gh label delete`.
Reading is unrestricted.
All teams may run read commands:
```bash
gh project list --owner <owner>
gh project view <N> --owner <owner>
gh project field-list <N> --owner <owner> --format json
gh issue view <number>
gh issue list --repo <owner>/<repo>
gh pr view <number>
gh pr list --repo <owner>/<repo>
```
Mutation exceptions:
- Dev-Team creates its own pull request with `gh pr create`.
- Dev-Team merges its own pull request with `gh pr merge` only after Project-Lead records acceptance.
- Project-Lead grants merge permission through the handoff envelope.
Board authority never moves with delegation.

## 2. Authentication pre-flight

Before any board work or pull request work, run the pre-flight.
```bash
gh auth status
git ls-remote origin HEAD
gh auth status
```
The first command verifies GitHub CLI authentication. The second verifies repository access through `origin`. The third is read for token scopes.
Projects v2 requires the `project` token scope. `gh auth status` shows token scopes.
If `project` is missing, use:
```bash
gh auth refresh -s project
```
Failure rule:
| Failure | Required action |
|---|---|
| `gh auth status` fails | Stop. Project-Lead reports missing GitHub authentication to the user. |
| `git ls-remote origin HEAD` fails | Stop. Project-Lead reports missing repository access to the user. |
| `project` scope is absent | Stop. Project-Lead reports the required `gh auth refresh -s project` action. |
Nothing is half-created. If pre-flight fails, no issue, label, project, project item, branch, or pull request is created.
A non-Project-Lead team returns the failure to Project-Lead. Project-Lead is the only team that reports it to the user.

## 3. The Project

The board is a GitHub Projects v2 project titled `<repo> Delivery`.
Detection order:
1. Read `.project-memory/project-link.md`.
2. If it records a project, use that project.
3. Otherwise list projects for the owner.
4. Match by exact title `<repo> Delivery`.
5. Only if no exact match exists, create the project.
Commands:
```bash
gh project list --owner <owner> --format json
gh project create --owner <owner> --title "<repo> Delivery"
```
Hazard: `gh project create` is not idempotent. It silently creates duplicate projects with the same title. Title matching must happen before creation.
The owner is the GitHub repository owner. For `https://github.com/<owner>/<repo>.git` and `git@github.com:<owner>/<repo>.git`, use `<owner>` and `<repo>`.
Discover field and option ids:
```bash
gh project field-list <N> --owner <owner> --format json
```
Required field: `Status`, single-select.
Required Status options:
| Column |
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
Persist the link at `.project-memory/project-link.md`.
```markdown
# GitHub Project Link

- owner: <org-or-user>
- project_number: <N>
- project_url: https://github.com/orgs/<owner>/projects/<N>
- project_id: <PVT_...>
- status_field_id: <PVTSSF_...>
- status_options:
    Intake: <option-id>
    "In Review": <option-id>
    "Ready for Discovery": <option-id>
    "In Discovery": <option-id>
    "In Spec": <option-id>
    "In Architecture": <option-id>
    "Ready for Dev": <option-id>
    "In Dev": <option-id>
    "In Acceptance": <option-id>
    Done: <option-id>
    Parked: <option-id>
    Blocked: <option-id>
- requirement_issue_type: <Requirement | label:requirement>
```
`project_id` is the Projects v2 node id, usually `PVT_...`; `status_field_id` is the Status field id, usually `PVTSSF_...`; `status_options` maps every column name to its option id.
Add a Requirement issue to the Project:
```bash
gh project item-add <N> --owner <owner> --url <issue-url>
```
Set a Status value:
```bash
gh project item-edit --id <item-id> --project-id <project-id> --field-id <status-field-id> --single-select-option-id <option-id>
```
Project-Lead uses option ids from `project-link.md`. Agents do not hard-code option ids.
The board Status field is not OKF `status` and is not the requirement lifecycle field. If the board drifts, `sync` corrects it from repository documents.

## 4. Issue model

GitHub issues provide traceability. The issue tree mirrors the delivery tree.
| Level | GitHub item | Title convention | Label |
|---|---|---|---|
| Requirement | Requirement issue | `[REQ-NNN] <title>` | `requirement` when custom type is unavailable |
| Feature | Feature issue | `[REQ-NNN] <feature title>` | `feature` |
| Story | Story issue | `<feature title>: <story title>` | `story` |
One Requirement has one Requirement issue. One Requirement may have many Feature issues. One Feature may have many Story issues.
### 4.1 Requirement issue
Prefer a custom GitHub issue type named `Requirement`. The `gh` CLI has no
`--type` flag on `gh issue create` (verified against gh 2.86.0), so both detection
and creation go through the GraphQL API.

GraphQL detection:
```bash
gh api graphql -f query='query($owner: String!) { organization(login: $owner) { issueTypes(first: 100) { nodes { id name } } } }' -f owner=<owner>
```
Capture the `id` of the node named `Requirement`. An error or an empty node list
means issue types are unavailable on this owner — use the label fallback.

Record the outcome in `project-link.md`:
```markdown
- requirement_issue_type: Requirement
- requirement_issue_type_id: <IT_...>
```
or:
```markdown
- requirement_issue_type: label:requirement
```
Create with a custom type — create the issue first, then set its type:
```bash
url=$(gh issue create --repo <owner>/<repo> --title "[REQ-NNN] <title>" --body-file <body.md>)
number=${url##*/}
issue_id=$(gh api graphql -f query='query($owner:String!,$repo:String!,$number:Int!){repository(owner:$owner,name:$repo){issue(number:$number){id}}}' -f owner=<owner> -f repo=<repo> -F number="$number" --jq '.data.repository.issue.id')
gh api graphql -f query='mutation($issue:ID!,$type:ID!){updateIssueIssueType(input:{issueId:$issue,issueTypeId:$type}){issue{number}}}' -f issue="$issue_id" -f type=<IT_...>
```
Fallback create:
```bash
gh issue create --repo <owner>/<repo> --title "[REQ-NNN] <title>" --body-file <body.md> --label requirement
```
### 4.2 Feature issues
Title: `[REQ-NNN] <feature title>`.
Create:
```bash
gh issue create --repo <owner>/<repo> --title "[REQ-NNN] <feature title>" --body-file <body.md> --label feature
```
Feature issue body requirements:
- Link to the spec file on the default branch.
- Link to the parent Requirement issue.
- Name `workstream_id` when assigned.
- List child Story issues when known.
Spec link shape:
```text
https://github.com/<owner>/<repo>/blob/<default-branch>/docs/specs/REQ-NNN/<spec-file>.md
```
### 4.3 Story issues
Title: `<feature title>: <story title>`.
Create:
```bash
gh issue create --repo <owner>/<repo> --title "<feature title>: <story title>" --body-file <body.md> --label story
```
Story issue body requirements:
- Link to the spec file on the default branch.
- Link to the parent Feature issue.
- Link to the parent Requirement issue.
- Name `workstream_id` when assigned.
- State acceptance criteria copied or referenced from the spec.
### 4.4 Parenting
Prefer native GitHub sub-issues. The `gh` CLI exposes no sub-issue flag or
subcommand (verified against gh 2.86.0), so parenting goes through GraphQL.

Resolve both issues to node ids, then add the child to the parent:
```bash
parent_id=$(gh api graphql -f query='query($owner:String!,$repo:String!,$number:Int!){repository(owner:$owner,name:$repo){issue(number:$number){id}}}' -f owner=<owner> -f repo=<repo> -F number=<parent-number> --jq '.data.repository.issue.id')
child_id=$(gh api graphql -f query='query($owner:String!,$repo:String!,$number:Int!){repository(owner:$owner,name:$repo){issue(number:$number){id}}}' -f owner=<owner> -f repo=<repo> -F number=<child-number> --jq '.data.repository.issue.id')
gh api graphql -H 'GraphQL-Features: sub_issues' -f query='mutation($parent:ID!,$child:ID!){addSubIssue(input:{issueId:$parent,subIssueId:$child}){issue{number}}}' -f parent="$parent_id" -f child="$child_id"
```
Apply this twice: Requirement issue as parent of each Feature issue, and Feature
issue as parent of each Story issue.

If the mutation is unavailable on this repository, fall back.
- Add a `parent:REQ-NNN` label.
- Add `Parent: #<n>` to the issue body.
```bash
gh label create "parent:REQ-NNN" --repo <owner>/<repo> --description "Fallback parent marker for REQ-NNN" --color 6f42c1 || true
gh issue edit <child-issue> --repo <owner>/<repo> --add-label "parent:REQ-NNN" --body-file <updated-body.md>
```
The fallback is not a real relationship. It can go stale.

## 5. Labels

Labels are repository-level. Project-Lead creates and maintains them. Creation is idempotent: check first or use `|| true`.
| Label | Purpose | Color |
|---|---|---|
| `requirement` | Requirement issue fallback when issue type is unavailable. | `5319e7` |
| `feature` | Feature issue. | `1d76db` |
| `story` | Story issue. | `0e8a16` |
| `workstream:ws<k>` | Workstream assignment. | `fbca04` |
| `blocked` | Work cannot proceed. | `d73a4a` |
| `needs-decision` | Stakeholder or Project-Lead decision needed. | `b60205` |
```bash
gh label create requirement --repo <owner>/<repo> --description "Stakeholder requirement" --color 5319e7 || true
gh label create feature --repo <owner>/<repo> --description "Feature under a requirement" --color 1d76db || true
gh label create story --repo <owner>/<repo> --description "User story under a feature" --color 0e8a16 || true
gh label create "workstream:ws<k>" --repo <owner>/<repo> --description "Assigned delivery workstream ws<k>" --color fbca04 || true
gh label create blocked --repo <owner>/<repo> --description "Work cannot proceed" --color d73a4a || true
gh label create needs-decision --repo <owner>/<repo> --description "Decision needed before work continues" --color b60205 || true
```
For concrete workstreams, replace `<k>`: `gh label create "workstream:ws1" --repo <owner>/<repo> --description "Assigned delivery workstream ws1" --color fbca04 || true`.

## 6. Pull requests

Dev-Team owns implementation pull requests. Project-Lead owns acceptance.
Pull request title: `[REQ-NNN] <workstream title>`.
Pull request body includes:
- Requirement id.
- Workstream id.
- Workstream title.
- Story issues it closes.
- Link to the spec file on the default branch.
- Validation summary.
- Acceptance request to Project-Lead.
Closing syntax:
```markdown
Closes #<story-issue>
Closes #<story-issue>
```
Create:
```bash
gh pr create --repo <owner>/<repo> --base <default-branch> --head <workstream-branch> --title "[REQ-NNN] <workstream title>" --body-file <body.md>
```
Merge only after Project-Lead records acceptance. The ordering rule is strict: acceptance precedes merge.
Project-Lead grants permission through the handoff envelope. Dev-Team performs the merge.
```bash
gh pr merge <pr-number> --repo <owner>/<repo> --squash --delete-branch
```
After merge, Project-Lead applies board updates and records the event in Project Memory.

## 7. Board request queue

Teams request board changes in the handoff envelope. Project-Lead applies board changes.
Schema:
```yaml
board_requests:
  - action: item.create | item.link | item.status | item.label | item.comment | item.close
    target:
      kind: requirement | feature | story | project_item | issue | pull_request
      ref: "<stable-reference>"
    args:
      # action-specific keys
    reason: "<why this change is needed>"
    requested_by: Project-Lead | Research-Team | Architect-Team | PM-Team | Dev-Team | UX-Team
```
Actions:
| Action | Meaning | Project-Lead mutation |
|---|---|---|
| `item.create` | Create a GitHub issue or Project item. | `gh issue create`, `gh project item-add` |
| `item.link` | Link issues or Project items. | `addSubIssue` GraphQL mutation (§4.4), document update |
| `item.status` | Move a Project item to a Status option. | `gh project item-edit` |
| `item.label` | Add or remove labels. | `gh issue edit --add-label` or `--remove-label` |
| `item.comment` | Add an issue or PR comment. | `gh issue comment` or `gh pr comment` |
| `item.close` | Close an issue. | `gh issue close` |
Project-Lead validates every request against the lifecycle before applying it. Project-Lead may reject a request with a reason.
Validation checks:
- The target exists or can be created idempotently.
- The requested status is a valid Status option in `project-link.md`.
- The requested transition matches the requirement lifecycle.
- The request does not bypass acceptance.
- The request does not transfer board-writing authority.
- The request has a clear reason.
Example: PM-Team requests Feature and Story issues.
```yaml
board_requests:
  - action: item.create
    target: { kind: feature, ref: "REQ-014.feature.export-format-selection" }
    args:
      title: "[REQ-014] Export format selection"
      labels: ["feature"]
      spec_path: "docs/specs/REQ-014/export-format-selection.md"
      parent_requirement: "REQ-014"
      workstream_id: "ws1"
    reason: "Spec is approved and the feature needs traceability before development."
    requested_by: PM-Team
  - action: item.create
    target: { kind: story, ref: "REQ-014.feature.export-format-selection.story.csv-option" }
    args:
      title: "Export format selection: CSV option"
      labels: ["story", "workstream:ws1"]
      spec_path: "docs/specs/REQ-014/export-format-selection.md"
      parent_feature_ref: "REQ-014.feature.export-format-selection"
      workstream_id: "ws1"
    reason: "Story is assigned to workstream ws1."
    requested_by: PM-Team
```
Project-Lead applies it with:
```bash
gh issue create --repo <owner>/<repo> --title "[REQ-014] Export format selection" --body-file <body.md> --label feature
gh issue create --repo <owner>/<repo> --title "Export format selection: CSV option" --body-file <body.md> --label story --label "workstream:ws1"
# then parent them with the addSubIssue mutation from §4.4
```
Example: Dev-Team requests acceptance status.
```yaml
board_requests:
  - action: item.status
    target: { kind: project_item, ref: "REQ-014" }
    args:
      status: "In Acceptance"
      project_item_id: "PVTI_..."
    reason: "Pull request is ready for Project-Lead acceptance."
    requested_by: Dev-Team
  - action: item.comment
    target: { kind: pull_request, ref: "#42" }
    args:
      body: "Workstream ws1 is ready for acceptance. Validation is recorded in the PR body."
    reason: "Project-Lead needs a direct acceptance handoff on the PR."
    requested_by: Dev-Team
```
Project-Lead applies the status with `gh project item-edit` using ids from `project-link.md`.
Project-Lead may reject the request if validation is missing, the PR does not close the named Story issues, or the workstream does not match the spec.

## 8. Failure handling

Failures are explicit. No GitHub mutation is silently ignored.
Rate limits:
- Stop the current mutation batch.
- Back off according to the reset time when available.
- Record the attempted operation in the ledger.
- Report the paused state to Project-Lead.
- Project-Lead reports to the user if delivery is waiting on the limit.
Inspect limits: `gh api rate_limit`.
Partial creation:
- Record what was created in the ledger before continuing.
- Record issue numbers, PR numbers, Project item ids, and URLs.
- Re-read GitHub before retrying.
- Reuse existing items when they match the ledger or document links.
Ledger entry shape:
```markdown
- GitHub: created Feature issue #<n> for REQ-NNN / <feature title>.
- GitHub: added Project item <PVTI_...> for issue #<n>.
- GitHub: linked issue #<child> under issue #<parent>.
```
Re-read commands:
```bash
gh issue view <number> --json number,title,labels,url,state
gh project item-list <N> --owner <owner> --format json
```
Missing permissions:
- Stop.
- Do not try alternate mutation paths.
- Record the failed command shape without secrets.
- Return the failure to Project-Lead.
- Project-Lead reports the missing permission to the user.
Common causes: Project commands fail without the `project` token scope; issue type rejection uses the `label:requirement` fallback; sub-issue rejection uses the fallback parent marker; push or PR failure means repository permission is missing.
The board is a projection. It is not the source of truth.
Sources of truth are `docs/requirements/`, `docs/specs/`, `docs/architecture/`, `.project-memory/`, pull requests, and the ledger.
If GitHub drifts from repository documents, `sync` corrects GitHub from the documents rather than the reverse.
Sync reads:
```bash
gh project item-list <N> --owner <owner> --format json
gh issue list --repo <owner>/<repo> --state all --json number,title,labels,state,url
gh pr list --repo <owner>/<repo> --state all --json number,title,state,url,mergedAt
```
Sync writes only through Project-Lead authority. Other teams may report drift, but they do not repair the board directly.
