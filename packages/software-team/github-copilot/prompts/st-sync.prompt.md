---
description: 'Reconcile software-team drift by treating lifecycle documents as source of truth, correcting board projection, regenerating indexes and registers, and logging changes.'
---
# Sync mode
You run as `St-Project-Lead` and assume that agent's authority. Project-Lead is the only board writer. Governing rule: documents are the source of truth for lifecycle; the board is a projection corrected to match, never the reverse.
## 1. Run conformance check
1. Run the advisory OKF checks from `lint` across all six bundles.
2. Do not stop for advisory findings.
3. Stop only for unsafe conflicts: duplicate `REQ-NNN`, unreadable Requirement documents, invalid project-link ids, or a GitHub permission failure; report them and make no GitHub mutation for affected Requirements.
## 2. Update repository state
1. Run:
   ```bash
   git fetch --all --prune
   git pull --ff-only
   ```
2. If fast-forward fails, stop and report that sync cannot safely reconcile stale local state.
3. Do not perform manual merge resolution in sync.
## 3. Normalize logs before reading
1. Normalize `.project-memory/log.md`: preserve preamble, group bare descending `## YYYY-MM-DD` headings, deduplicate identical bullets, preserve same-day order.
2. Remember that ledgers are union-merged and must be normalized after any merge before entries are interpreted.
3. Normalize `.software-team/**/ledger.md` only as safe append-preserving cleanup.
## 4. Read canonical inputs
1. Read `.project-memory/project-link.md`.
2. Extract owner, project number, Project id, Status field id, every Status option id, and requirement issue handling.
3. Read `.project-memory/overview.md` and `.project-memory/requirements-register.md`; treat both as projections.
4. Enumerate `docs/requirements/REQ-*.md`.
5. Enumerate `.software-team/REQ-*/workstreams.md` and `.software-team/REQ-*/ledger.md`.
## 5. Read GitHub projection
Use read commands before any write:
```bash
gh project item-list <N> --owner <owner> --format json
gh issue list --repo <owner>/<repo> --state all --json number,title,labels,state,url,body,updatedAt
gh pr list --repo <owner>/<repo> --state all --json number,title,state,url,body,updatedAt,mergedAt,isDraft
```
Read linked items when needed:
```bash
gh issue view <number> --repo <owner>/<repo> --json number,title,state,labels,url,body,updatedAt
gh pr view <number> --repo <owner>/<repo> --json number,title,state,url,body,updatedAt,mergedAt,isDraft
```
## 6. Enumerate every Requirement
For each `docs/requirements/REQ-*.md`:
1. Parse frontmatter.
2. Verify filename id and frontmatter `id` agree.
3. Verify `lifecycle` is canonical.
4. Record `version` for compare-and-swap edits.
5. Extract OKF `status`, approval fields, `requirement_issue`, `links.project_item`, `links.child_issues[]`, `links.prs[]`, `links.specs[]`, `links.architecture[]`, and `links.workstreams[]`.
6. Read Change log entries for the last lifecycle transition.
7. Mark duplicate ids as unsafe conflicts.
## 7. Compare document lifecycle, OKF status, issues and PRs
1. Derive OKF status from lifecycle:
| Lifecycle | OKF status |
|---|---|
| `draft` | `draft` |
| `in-review` | `draft` |
| `approved` | `stable` |
| `in-discovery` | `stable` |
| `in-spec` | `stable` |
| `in-architecture` | `stable` |
| `ready-for-dev` | `stable` |
| `in-dev` | `stable` |
| `in-acceptance` | `stable` |
| `delivered` | `stable` |
| `parked` | `deprecated` |
| `blocked` | unchanged |
2. If lifecycle is not `blocked` and OKF status differs, correct the Requirement document with compare-and-swap, increment `version`, and append a Change log entry.
3. If lifecycle is `blocked`, preserve OKF status.
4. Compare requirement issue state, sub-issue states, and open pull requests to document links.
5. Do not advance lifecycle because GitHub changed. Lifecycle transitions still require gates.
## 8. Compute expected board column
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
Use the Requirement document lifecycle to choose the expected board column.
## 9. Correct board projection
1. Use ids from `.project-memory/project-link.md`; never hard-code option ids.
2. If a linked Project item has the wrong Status, run:
   ```bash
   gh project item-edit --id <item-id> --project-id <project-id> --field-id <status-field-id> --single-select-option-id <option-id>
   ```
3. If an approved-or-later Requirement has an issue but no Project item, add it when policy allows:
   ```bash
   gh project item-add <N> --owner <owner> --url <issue-url>
   ```
4. Re-read after adding, then set Status.
5. If no issue URL exists, report unresolved drift.
6. If a board item has no matching Requirement document, report orphaned board work and do not invent a Requirement.
## 10. Regenerate projections
Regenerate from sources rather than hand-editing:
1. `docs/requirements/index.md` from `docs/requirements/REQ-*.md`.
2. `docs/requirements/README.md` when present or expected.
3. `.project-memory/requirements-register.md` from Requirements, workstream records, and GitHub links.
4. `.project-memory/index.md` from the fixed Project Memory tree.
5. Nested Project Memory indexes from child concept pages.
6. Status sections of `.project-memory/overview.md` from Requirements, ledgers, decisions, risks, workstreams, and board projection. Preserve the thesis unless a recorded decision changes it.
## 11. Reconcile issue, PR and child links
1. Ensure each Requirement issue is recorded in `requirement_issue`.
2. Ensure each Project item is recorded in `links.project_item`.
3. Add confirmed child Feature and Story issues to `links.child_issues[]`.
4. Add clearly related pull requests to `links.prs[]`.
5. Prefer native sub-issues:
   ```bash
   gh issue edit <requirement-issue> --add-sub-issue <feature-issue>
   gh issue edit <feature-issue> --add-sub-issue <story-issue>
   ```
6. Use documented fallback parent markers only when native sub-issues are unavailable.
7. Never remove a link unless verified stale and named in the summary.
## 12. Append Sync entry and output
1. Append:
   ```markdown
   - **Sync**: [<ISO-8601 timestamp>] St-Project-Lead — Reconciled software-team projections: <document status fixes>; <board status fixes>; <registers regenerated>; <links reconciled>; <unresolved drift reported>.
   ```
2. If nothing changed, include `no changes required`.
3. Print:
   ```markdown
   # Software Team Sync
   Repository: <owner>/<repo>
   Project: <project title> (#<N>)
   Rule: documents are source of truth for lifecycle; board is projection.
   ## Changes made
   | Area | Requirement | Change |
   |---|---|---|
   | <Board|Document|Projection|Links> | <REQ-NNN|all> | <specific change> |
   ## Unresolved drift
   | Requirement or item | Drift | Reason not changed | Next action |
   |---|---|---|---|
   | <ref> | <drift> | <reason> | <action> |
   ```
4. Stop after documents, projections, links and board Status values are reconciled or explicitly reported.
