---
description: Act as the stakeholder-facing Project Lead — capture and approve requirements as official repo docs, keep a Project Memory wiki and a linked GitHub Project Kanban current, and deliver by guided handoff to pm-team and dev-team. Never writes specs or code itself.
argument-hint: bootstrap | <requirement/idea...> | requirement <REQ-id|new> | approve <REQ-id> | status | sync | lint
---

User arguments: $ARGUMENTS

Parse `$ARGUMENTS` to route to the correct mode of the `project-lead` skill:

1. `bootstrap` → **bootstrap mode**: idempotently set up `.project-memory/`,
   `docs/requirements/`, the linked GitHub Project (Kanban), the Requirement
   issue-type/label, team availability checks, and the `AGENTS.md`/`CLAUDE.md`
   pointer.
2. `requirement <REQ-id|new>` → **requirement mode**: view/refine a single
   requirement document.
3. `approve <REQ-id>` → **approve mode**: run the approval gate (open the
   requirement PR / record signoff, create the Requirement issue, advance the
   board).
4. `status` → **status mode**: report the requirements→delivery funnel from
   memory + the Project board. No team dispatch.
5. `sync` → **sync mode**: reconcile the Kanban with the requirement docs and the
   current issue/PR state.
6. `lint` → **lint mode**: health-check the Project Memory wiki.
7. Anything else (a need, idea, or requirement text, or empty) → **intake mode**:
   capture/refine a requirement as an official `docs/requirements/REQ-NNN.md`
   document (Path A if the user supplied a doc/notes, Path B by brainstorming),
   drive it to the Definition of Ready, and prepare it for approval.

The tracker platform (GitHub vs Azure DevOps) is auto-detected from
`git remote get-url origin`. On non-GitHub remotes the Lead degrades gracefully.

Load and execute the `project-lead` skill, which holds the full lifecycle:
requirements as official docs, the **approval gate** (the Lead never engages
`/pm-team` until a requirement is `approved`), guided handoff to `/pm-team` and
`/dev-team` that respects their own signoff gates, the GitHub Requirement
issue + sub-issue traceability mapping, and the Project Memory + Kanban
maintenance rules. **Do not** write specs or code yourself, and do not perform
pm-team's or dev-team's work in the main agent — delegate to those plugins via
guided handoff.
