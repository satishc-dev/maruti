---
description: Drive a product idea from intent through interview, parallel feature specs, reviewer gate, spec PR, and (after your approval) work-item creation on the ADO or GitHub Kanban board. Three modes — fresh, feedback, approved.
argument-hint: <intent...> | feedback <pr#> | approved <pr#> [--cycles <N>]
---

User arguments: $ARGUMENTS

Parse `$ARGUMENTS` as follows:

1. Strip out the optional flag `--cycles <N>` and capture it. `<N>` MUST be an integer `>= 3`. Default is `12`. If the user passes a value below `3`, fall back to the default and warn the user once. Pass the resolved cycle budget through to the skill.
2. Strip out the optional flag `--platform <ado|gh>` if present; the skill honors it and skips auto-detection.
3. Route on the remaining argument shape:
   - `feedback <pr#>` (e.g., `feedback 1234`) → **feedback mode**: fetch PR comments, dispatch revisions, re-review, push to the same branch.
   - `approved <pr#>` (e.g., `approved 1234`) → **approved mode**: verify the spec PR is merged, then dispatch `board-manager` to seed the board with WIs.
   - Anything else → **fresh mode**: treat the remaining text as the user's initial intent statement; conduct the interactive interview, decompose into features, fan out to `requirements-analyst`s, gate via `spec-reviewer`, commit specs, open the spec PR, and stop for human review.

The platform (Azure DevOps vs GitHub) is auto-detected from `git remote get-url origin` unless `--platform` was passed.

Load and execute the `pm-team` skill, which has the full mode-routed Scrum workflow (plan + user signoff, cycle budget contract with warn at `<N>-2` and hard halt at `<N>`, schema-d work-logs under `.scrum/<project-slug>/agents/`, retrospective + lessons at completion). Do not perform the workflow yourself in the main agent — delegate to the skill.
