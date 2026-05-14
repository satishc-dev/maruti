---
description: Drive an Azure DevOps work item or GitHub issue through design, parallel implementation, code review, and PR creation via the dev-team subagents. Platform auto-detected from the git remote.
argument-hint: <work-item-id> [--cycles <N>]
---

Invoke the `team-lead` subagent (via the `Task` tool) to drive a work item end-to-end under a Scrum cadence.

User arguments: $ARGUMENTS

Parse `$ARGUMENTS` as follows:

1. The first positional token is the work-item ID — typically a numeric ID (e.g., `1234`, `42`).
2. Optional flag `--cycles <N>` sets the project cycle budget. `<N>` MUST be an integer `>= 3`. Default is `12`. If the user passes a value below `3`, fall back to the default and warn the user once.
3. Optional flag `--platform <ado|gh>` overrides platform detection; otherwise leave detection to `team-lead`.

If `$ARGUMENTS` is empty or unparseable as a work-item ID, ask the user to re-issue the command with an ID.

Then dispatch to the `team-lead` subagent with the prompt:

> Drive work item `<work-item-id>` from intake to a merge-ready PR under a Scrum cadence with a cycle budget of `<N>` (default 12; warn threshold `<N-2>`; hard halt at `<N>` unless the user extends). Auto-detect the platform from `git remote get-url origin` (`github.com` → `gh`, `dev.azure.com` / `visualstudio.com` → `ado`); if it's ambiguous, ask the user once. Then follow your standard Scrum workflow: read `.scrum/lessons.md` (Phase 0), fetch the work item (Phase 1), produce a plan and get explicit user signoff before dispatching any subagent (Phase 2), initialize the Scrum journal and branch/worktrees (Phase 3), run the cycle loop with dispatch / collect / journal / blocker-handling / cycle-budget checks (Phase 4), write the retrospective and distill lessons into `.scrum/lessons.md` with FIFO trim to 5 KB (Phase 5), ship the PR (Phase 6), and report back with outcome, PR URL, cycle count consumed, retrospective path, and lessons added (Phase 7).

The team-lead handles everything from there. Do not attempt the workflow yourself in the main agent — delegate.
