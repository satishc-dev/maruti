# software-team — GitHub Copilot CLI

The Copilot CLI build of the [`software-team`](../README.md) package. This is the
only platform variant; there is no Claude Code build.

## Install

```
copilot plugin marketplace add satishc-dev/maruti
copilot plugin install software-team@maruti
```

Or, from a local clone, copy what you need into the consuming repository:

```
.github/agents/st-*.agent.md
.github/skills/st-*/
.github/prompts/st-*.prompt.md
```

## Use

Start in the repository you want to work in:

```
@st-project-lead bootstrap
```

Installed agents are namespaced by plugin, so the fully-qualified name is
`software-team:st-project-lead`. Use that form wherever a bare name is not
resolved, including `copilot --agent software-team:st-project-lead` for
non-interactive runs.

Bootstrap also copies the contracts into `.software-team/contracts/`, which every
agent reads from. Run it before commissioning any team.

Then talk to `St-Project-Lead` in plain language. It is the only agent you address;
it commissions the rest.

```
@st-project-lead I want users to be able to export their account data as CSV
@st-project-lead approve REQ-007
@st-project-lead status
```

## What ships

### Agents

| Agent | Role |
|---|---|
| `St-Project-Lead` | Root agent. Your only point of contact. Owns requirements, memory, the board, acceptance. |
| `St-Research-Lead` · `St-Research-Duck` | Research-Team — cited findings, before anything is specified |
| `St-Architect` · `St-Architect-Duck` | Architect-Team — solution architecture, ADRs, binding development principles |
| `St-Pm-Lead` · `St-Pm-Duck` · `St-Feature-Analyst` | PM-Team — feature specs and acceptance criteria |
| `St-Dev-Lead` · `St-Dev-Duck` · `St-Implementer` · `St-Test-Engineer` · `St-Code-Reviewer` | Dev-Team — implementation, tests, review, PR |
| `St-Ux-Designer` · `St-Ux-Duck` | UX-Team — experience briefs and wireframes |

Only `St-Project-Lead` is meant to be addressed directly. The rest are dispatched.
They will answer if you tag them, but they will not initiate contact with you, and
they report to whoever commissioned them.

### Skills

Shared contracts, loaded rather than restated — which is why no agent file
duplicates them.

| Skill | Loaded by | Holds |
|---|---|---|
| `st-okf-memory` | all | Document format, provenance, path ownership |
| `st-handoff` | all | Envelopes, receipts, consultation, escalation |
| `st-board-ops` | all | Board authority and request queue |
| `st-cadence` | leads and crew | Cycles, journals, budgets, safety |
| `st-rubber-duck` | **ducks only** | The review standard |

`st-rubber-duck` is restricted by design. Lead agents must not load it — see below.

### Prompts

| Prompt | Does |
|---|---|
| `st-bootstrap` | Makes a repository ready for the team. Idempotent. |
| `st-status` | Read-only funnel report. |
| `st-sync` | Reconciles board and register drift from the documents. |
| `st-lint` | Advisory conformance check. |

## Why the review standard is hidden

Each team is critiqued by its own duck, and iterates until the duck passes the work
— at least two rounds, always.

The lead is never told how it is judged. A lead that knows the passing standard aims
at the standard rather than at the work: it calculates what it can afford, does
exactly that, and stops. So the standard lives in one file that only ducks load, and
every lead agent is free of any score, threshold or severity vocabulary. A lead that
asks its duck what would make the work pass has that request recorded as a defect.

The duck is constrained too: its verdict is computed from findings that must each
cite concrete evidence, so it cannot simply declare work acceptable to end the loop.
The ledger keeps the findings, so any verdict can be recomputed and checked later.

**If you modify this package:** pasting that standard into a lead agent silently
defeats the whole design. Keep it in `skills/st-rubber-duck/` and nowhere else.

## Runtime requirements

This package depends on two Copilot CLI capabilities:

- **Nested agent dispatch.** Team leads dispatch their own crews, so the agent tree
  is more than two levels deep.
- **Multi-turn peer messaging.** `write_agent` / `read_agent` carry the lead-to-duck
  review dialogue and the research roundtable. These are conversations, not
  single-shot reviews.

It also expects `gh` authenticated with the `project` scope for GitHub Projects v2.
Bootstrap checks this before creating anything.

## Concurrency

> Project-Lead runs as the root agent. Every team may run at most 2 subagents in
> parallel. More than 2 is not allowed.

At most two teams run at once, so at most four agents work simultaneously. The limit
is static rather than dynamically allocated — agents in separate contexts cannot
reliably share a counter — and `list_agents` verifies it at runtime.

## Scope

GitHub only; Azure DevOps is not supported. See the
[package README](../README.md) for the full design and the
[contracts](contracts/) for agent behaviour. Those contracts ship with this
plugin and are copied into each repository at `.software-team/contracts/`.
