---
description: Run a board operation (create, update, or query) directly against the project's ADO or GitHub Kanban board, independent of the PM flow. Platform auto-detected from the git remote.
argument-hint: <natural-language request> [--cycles <N>]
---

User request: $ARGUMENTS

Parse `$ARGUMENTS` as follows:

1. Strip out the optional flag `--cycles <N>` and capture it. `<N>` MUST be an integer `>= 3`. Default is `12`. If the user passes a value below `3`, fall back to the default and warn the user once.
2. Strip out the optional flag `--platform <ado|gh>` if present; the subagent honors it and skips auto-detection.
3. The remaining text is the freeform board request.

Multi-WI operations (e.g., "create 5 user stories from this list", or any request that requires multiple sequential WI creates / updates) MUST run under the Scrum cadence — the `pm-team` skill orchestrates plan + user signoff, journals each WI as a task in the cycle loop, and respects the cycle budget. For multi-WI requests, dispatch the `pm-team` skill instead of invoking `board-manager` directly so the Scrum mechanics apply.

Single-WI operations (one create, one update, one query) bypass the cycle budget — dispatch the `board-manager` subagent (via the `Task` tool) directly with the user's request as its prompt. The cycle budget is IGNORED for single-WI operations.

For direct (single-WI) dispatches, the `board-manager` subagent will:

1. Detect the platform from `git remote get-url origin` (or honor `--platform <ado|gh>` if present).
2. Parse the request into one of: **create**, **update**, **query**.
3. Execute via the appropriate tool (`gh` CLI, `az`, or `mcp__azure-devops-mcp__*`).
4. Return URLs and a one-line confirmation per affected WI.

If the request is ambiguous (missing WI type, missing title, ambiguous WI ID), `board-manager` will ask one focused clarifying question. Do not attempt the operation yourself in the main agent — delegate.
