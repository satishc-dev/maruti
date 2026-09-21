---
type: Team Contract
title: Software Team — Parallelism Contract
description: Fixed concurrency, workstream decomposition, worktree isolation, dispatch, ordering, and recovery rules for the software-team package.
status: stable
---

# Parallelism Contract

This contract refines `ROLES.md`. It tells Project-Lead and team leads how to run parallel work without losing ownership, corrupting git state, or exceeding the agent limit.

Where this contract and `ROLES.md` disagree, `ROLES.md` wins.

## 1. The concurrency rule

**The limit is fixed. It is not negotiated at runtime.**

- Project-Lead runs as the root agent and is NOT a subagent.
- Project-Lead may have at most 2 teams active concurrently.
- Every team lead may run at most 2 of its own subagents in parallel (crew and duck both count).
- More than 2 is not allowed. There are no dynamic quotas and no borrowing.
- Peak working agents = 2 teams x 2 subagents = 4.
- A lead awaiting its dispatched children is not "working" — the limit governs actively running agents.
- Enforcement: before dispatching, a lead calls `list_agents` (scope children) and must not dispatch if 2 children are already live. Project-Lead does the same for teams.

This rule is static by design. LLM agents cannot reliably share a distributed counter. They run in separate contexts, wake at different times, and cannot prove that a shared number is still current when they act on it. A fixed static rule is verifiable by inspection.

If 2 children are already live, wait. Do not borrow capacity, create an exception, or split work into extra dispatches to bypass the rule.

## 2. Workstreams

A workstream is an independently deliverable slice of an approved requirement. It has its own scope, owner, files, branch, worktree, and delivery result.

Workstream identifiers are scoped to a requirement. The local form is `ws<k>`. The full form is `REQ-NNN/ws<k>`.

```text
REQ-007/ws1
REQ-007/ws2
REQ-012/ws1
```

Project-Lead records every workstream before dispatch.

```yaml
workstream_id: "REQ-007/ws2"
req: "REQ-007"
title: "Implement account recovery email flow"
stories:
  - "REQ-007-US-003"
  - "REQ-007-US-004"
file_scope:
  - "src/accounts/recovery/**"
  - "tests/accounts/recovery/**"
depends_on:
  - "REQ-007/ws1"
team_id: "dev-team-REQ-007-ws2"
status: "pending"
```

All fields shown in the record are mandatory.

Recommended states: `pending`, `ready`, `active`, `handoff`, `accepted`, `failed`, `parked`.

`handoff` means the team has returned its result and the team's duck must pass the work before Project-Lead considers acceptance.

## 3. Decomposition rules

Project-Lead performs decomposition. No specialist team owns the full split.

### 3.1 Decompose only after the inputs exist

Project-Lead decomposes only after the requirement is approved, specs exist, architecture exists, and development principles are set.

Before those inputs exist, the boundaries are guesses. Guessing creates false independence, bad dependencies, and file contention.

### 3.2 Declare file scope up front

Every workstream declares `file_scope` as glob patterns before dispatch.

```yaml
file_scope:
  - "src/billing/invoices/**"
  - "tests/billing/invoices/**"
  - "docs/architecture/decisions/ADR-018-invoice-numbering.md"
```

A team may read outside its `file_scope`. It may not write outside it. If the scope is wrong, the team returns the issue to Project-Lead and waits for a new split.

Use precise patterns. Avoid `src/**` unless the workstream truly owns that whole surface.

### 3.3 Reject overlapping write scopes

If two workstreams' `file_scope` intersect, the decomposition is invalid and must be redone.

Concrete check:

1. Expand every glob against the repository tree.
2. Add each matched path to that workstream's write set.
3. For future paths, compare glob patterns structurally.
4. Treat identical patterns as intersecting.
5. Treat parent and child patterns as intersecting.
6. Treat patterns that can match the same future path as intersecting.
7. Compare every pair of workstreams.
8. If `write_set(A) ∩ write_set(B)` is not empty, reject the split.

Invalid:

```yaml
workstreams:
  - workstream_id: "REQ-007/ws1"
    file_scope:
      - "src/accounts/**"
  - workstream_id: "REQ-007/ws2"
    file_scope:
      - "src/accounts/recovery/**"
```

### 3.4 Declare dependencies before dispatch

Dependencies are declared, not discovered. A workstream may not start until every item in `depends_on[]` is delivered.

If a team finds a real dependency during execution, it stops that path and returns the issue to Project-Lead. Project-Lead updates the record, fixes the split, and dispatches only when the graph is valid again.

### 3.5 Prefer fewer, larger workstreams

Each workstream costs a team. Prefer fewer, larger workstreams over many tiny ones.

| Prefer | Avoid |
|---|---|
| One cohesive deliverable per workstream. | One workstream per file. |
| Boundaries that match acceptance. | Boundaries that only mirror tasks. |
| File scopes that do not intersect. | File scopes needing constant exceptions. |
| A simple dependency graph. | Chains created only to keep teams busy. |

## 4. Filesystem and git isolation

**One writer per working tree.** A working tree has one index and one `HEAD`. Two agents editing the same tree will stage each other's half-written files, contend on `index.lock`, and leave debris that cannot be told apart from work in progress. So every writer gets its own worktree and its own branch, and the main working tree is an integration point that nobody authors in.

| Working tree | Who authors there | Branch |
|---|---|---|
| Main working tree, default branch | **Nobody.** Merges and `bootstrap` only. | default |
| `.worktrees/<REQ-NNN>/project-lead/` | Project-Lead | `users/<you>/REQ-NNN-lead` |
| `.worktrees/<REQ-NNN>/research/` | Research-Team | `users/<you>/REQ-NNN-research` |
| `.worktrees/<REQ-NNN>/ux/` | UX-Team | `users/<you>/REQ-NNN-ux` |
| `.worktrees/<REQ-NNN>/pm/` | PM-Team | `users/<you>/REQ-NNN-pm` |
| `.worktrees/<REQ-NNN>/architect/` | Architect-Team | `users/<you>/REQ-NNN-architect` |
| `.worktrees/<REQ-NNN>/ws<k>/` | One Dev-Team workstream | `users/<you>/REQ-NNN-ws<k>` |

Dev-Team is the case with more than one worktree at a time, because a requirement may decompose into several workstreams. Every other team has exactly one.

```bash
.worktrees/REQ-007/project-lead/
.worktrees/REQ-007/research/
.worktrees/REQ-007/pm/
.worktrees/REQ-007/ws1/
.worktrees/REQ-007/ws2/
.worktrees/REQ-012/ws1/
```

### 4.0 Research predates the requirement

Research runs before `REQ-NNN` exists, so it keys on the slug instead, matching the ledger path it already uses:

```bash
.worktrees/pre-REQ-<slug>/research/       # branch users/<you>/pre-REQ-<slug>-research
.worktrees/pre-REQ-<slug>/project-lead/   # branch users/<you>/pre-REQ-<slug>-lead
```

### 4.1 Creating and entering a worktree

The commissioner creates the worktree and names it in the commission envelope. The commissioned team enters it and works nowhere else.

```bash
git worktree add .worktrees/REQ-007/pm -b users/alex/REQ-007-pm
git -C .worktrees/REQ-007/pm status --short
```

Resume rather than recreate when the worktree already exists. Never create a second worktree for the same branch; git refuses, and the attempt signals that two agents believe they own the same work.

### 4.2 Committing and merging

1. Author and commit only inside your own worktree, on your own branch.
2. Never run `git add -A` from the main working tree, and never stage a path you do not own.
3. Report your branch and its commits in your delivery envelope.
4. Project-Lead merges delivered branches into the default branch in the main working tree. Merging is not authoring, which is why it is the one thing the main tree is for.

**Project-Lead merges before it commissions.** Its own branch is long-lived for the requirement and is merged into the default branch at each stage boundary, *before* the next team is dispatched. A team reads the requirement from the default branch, so unmerged lifecycle state would hand it a stale `lifecycle` and `version`. This is a correctness rule, not housekeeping.

Merges between teams are additive by construction: each team writes only under the directory it owns, and §3 already forbids intersecting file scopes. `.project-memory/log.md` and `.software-team/**/ledger.md` carry `merge=union` in `.gitattributes`, so concurrent appends from separate branches combine without conflict.

### 4.3 Teardown

After a branch is merged and its work is accepted, remove the worktree and the branch:

```bash
git worktree remove .worktrees/REQ-007/pm
git branch -d users/alex/REQ-007-pm
```

Do not tear down a failed or dirty worktree. §7 keeps it as evidence.

### 4.4 Branch names

Use sibling branch names.

```bash
# team branch
users/<you>/REQ-NNN-<team>

# feature branch
users/<you>/REQ-NNN-ws<k>

# task branches
users/<you>/REQ-NNN-ws<k>-task-<n>
```

Examples:

```bash
git switch -c users/alex/REQ-007-ws1
git switch -c users/alex/REQ-007-ws1-task-1
git switch -c users/alex/REQ-007-ws1-task-2
```

Never nest a task branch under the feature branch as a path segment:

```bash
# wrong when users/alex/REQ-007-ws1 exists
users/alex/REQ-007-ws1/task-1
```

A git ref cannot be simultaneously a leaf and a directory. If `users/alex/REQ-007-ws1` exists, git cannot also create `users/alex/REQ-007-ws1/task-1`. Git fails with:

```text
cannot lock ref ... exists
```

Always use sibling naming with a hyphen:

```bash
users/alex/REQ-007-ws1-task-1
```

`.worktrees/` and `.scrum/` are gitignored and machine-local. They may hold worktree state, dispatch notes, handoff notes, ledgers, and forensic evidence. They are not portable project state.

## 5. Dispatch mechanics

A lead checks capacity, dispatches, records the returned agent id, and collects the result.

Before dispatching, call:

```yaml
tool: list_agents
arguments:
  scope: children
```

If 2 children are already live, do not dispatch.

Use the `task` tool with `mode: background` for concurrent work.

```yaml
tool: task
mode: background
purpose: "Run Dev-Team for REQ-007/ws1"
```

Collect with `read_agent`.

```yaml
tool: read_agent
arguments:
  agent_id: "<returned-agent-id>"
```

Team leads use the same mechanics for crew and duck agents. Crew and duck both count. A team cannot run two crew agents and then add its duck as a third live child.

Use `write_agent` and `read_agent` for peer consultation. Example: a Dev-Team lead may ask Architect-Team a technical question mid-build. That is a message exchange with an existing peer, not a new child dispatch by Dev-Team.

The consulted agent counts against nothing for the consulting team because it is not the consulting team's child. It remains governed by its own dispatcher and its own children. Peer consultation is not a way to assign a workstream, add a worker, or bypass Project-Lead's limit.

## 6. Ordering rules

Parallelism follows phase order and dependency order.

| Phase | Parallel rule |
|---|---|
| Research | Single-team. Do not run duplicate Research-Team instances for one question. |
| UX | Runs only for user-visible work. |
| PM | Multiple PM-Teams only when feature sets are genuinely independent. |
| Architecture | Runs after specs exist; principles are set before decomposition. |
| Dev | Normal parallel case: one Dev-Team per valid workstream. |
| Acceptance | Project-Lead accepts delivered work against the requirement. |

Research is single-team. Project-Lead may converse with Research-Team and Architect-Team during the roundtable, but does not split one research question across multiple Research-Team instances.

UX and spec work may overlap only if UX completes first for a given feature.

```text
UX brief first -> PM specification second
```

Multiple PM-Teams are allowed only when feature sets have different surfaces, no shared unresolved UX decision, no shared unresolved architecture question, and no dependency where one spec defines terms the other needs.

Dev-Teams are the normal parallel case. Project-Lead may run up to 2 Dev-Team instances when file scopes do not intersect, dependencies are delivered, each has its own worktree and branch, and Project-Lead has capacity.

Dev-Team does not merge before Project-Lead accepts. If several workstreams finish together, Project-Lead accepts them one at a time.

## 7. Failure and recovery

Failure preserves evidence. Do not delete the worktree to make the attempt look clean.

When a team fails, stalls, or leaves a dirty worktree, Project-Lead records:

```yaml
failure_record:
  workstream_id: "REQ-007/ws2"
  team_id: "dev-team-REQ-007-ws2"
  agent_id: "<agent-id>"
  branch: "users/alex/REQ-007-ws2"
  worktree: ".worktrees/REQ-007/ws2/"
  status: "failed"
  dirty_worktree: true
  completed: []
  remaining: []
  decision: "re-dispatch"
```

Retain failed or dirty worktrees for forensics. They show what changed, what was attempted, and what can be salvaged. Keep the branch, dispatch notes, handoff notes, `.scrum/` records, and ledger entries.

A stalled team does not receive extra children. Project-Lead reads the agent, records the stall, and decides one of: continue, park, re-dispatch, or re-decompose.

Re-dispatch only after the plan is valid:

1. Read the failed team's result.
2. Check the workstream record.
3. Confirm or replace `file_scope`.
4. Confirm or replace `depends_on[]`.
5. Create a new worktree if needed.
6. Create a sibling branch if needed.
7. Call `list_agents` with `scope: children`.
8. Dispatch only if fewer than 2 teams are live.

Replacement dispatch includes the retained evidence and the new target.

```yaml
replacement_dispatch:
  original_workstream_id: "REQ-007/ws2"
  previous_team_id: "dev-team-REQ-007-ws2"
  previous_agent_id: "<agent-id>"
  retained_worktree: ".worktrees/REQ-007/ws2/"
  new_worktree: ".worktrees/REQ-007/ws2-retry-1/"
  branch: "users/alex/REQ-007-ws2"
  recovery_goal: "Complete the original workstream without expanding file scope."
```

Re-dispatch does not permit writes outside `file_scope`. If the scope is wrong, Project-Lead re-decomposes before sending another team. If the live-child count is already 2, the next action is to wait.
