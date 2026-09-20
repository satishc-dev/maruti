# software-team

A simulated software organisation for GitHub Copilot CLI. One stakeholder-facing
lead, five specialist teams, and a quality gate none of them can talk their way
past.

You describe what you want. `St-Project-Lead` researches it, specifies it,
designs it, builds it in parallel, accepts it against your requirement, and
merges it — and it is the only agent that ever talks to you.

## Why this exists

This package replaces three earlier packages — [`project-lead/`](../project-lead/),
[`pm-team/`](../pm-team/) and [`dev-team/`](../dev-team/) — which each work well
alone and compose badly. Those three remain installable and untouched; this is a
clean-sheet successor, not a migration.

What went wrong in the originals, and what changed here:

| Problem | Fix |
|---|---|
| PM wrote specs to `docs/specs/<initiative>/`; Dev never read them, and looked for requirement docs only the Lead wrote. Specs were orphaned. | Everything is keyed on `REQ-NNN`. One traceability chain, end to end. |
| PM contained zero references to the Lead. It never parented its issues under the requirement. | Teams are commissioned by the Lead and hand back through a typed envelope. |
| Dev opened a PR and stopped — nothing closed the issue or moved the board. | The loop closes: acceptance, merge, close, board `Done`. |
| Handoffs were prose: "now run `/dev-team 123`". A human was the integration layer. | Handoff is data — an envelope in a committed ledger, with receipts. |
| Three competing status systems, no tracker mapping. | One lifecycle, one mapping table, one board owner. |
| The Copilot builds dispatched agents that the packages never shipped. | Every agent named here exists as a real file. |
| Nothing owned research, architecture, or engineering standards. | Research-Team, Architect-Team, and binding development principles. |
| One PM team, one Dev team, one work item at a time. | Workstreams, with teams running in parallel. |
| Review was a single binary `go`/`no-go` pass. | Every team has an independent critic and iterates until it passes. |

## The teams

| Team | Lead | Critic | Owns |
|---|---|---|---|
| **Project-Lead** | `St-Project-Lead` | — | Requirements, Project Memory, the board, acceptance |
| **Research-Team** | `St-Research-Lead` | `St-Research-Duck` | `docs/research/` |
| **Architect-Team** | `St-Architect` | `St-Architect-Duck` | `docs/architecture/` — architecture, ADRs, development principles |
| **PM-Team** | `St-Pm-Lead` | `St-Pm-Duck` | `docs/specs/REQ-NNN/` |
| **Dev-Team** | `St-Dev-Lead` | `St-Dev-Duck` | Code, tests, branches, PRs |
| **UX-Team** | `St-Ux-Designer` | `St-Ux-Duck` | `docs/ux/REQ-NNN/` |

Three rules bind all of them:

1. **One voice.** Project-Lead is the only agent that speaks to you.
2. **One writer per surface.** Project-Lead is the only agent that writes to the
   board. Every document path has exactly one owning team.
3. **Nothing ships unreviewed.** Every team but Project-Lead has a critic, and no
   team's work is done until its critic passes it.

## The flow

```
bootstrap → research → requirement → [ux] → spec → architecture + principles → delivery → acceptance → done
           Research      PL          UX    PM-Team   PL + Architect            Dev-Teams       PL
            ↕ critic              ↕ critic  ↕ critic     ↕ critic               ↕ critic
            ↕ PL ↕ Architect                  ↕ Architect     │ principles          ↕ Architect
                                                              └── binding on Dev ────┘
```

**Research comes first and is deliberately off the board.** It is exploratory, it
may be discarded, and it predates any committed work. Its output is committed and
cited so PM-Team can build on it.

**Architecture comes after specs.** Project-Lead and Architect-Team partner once
the problem *and* the proposed solution are both known. The Architect then derives
the repository's development principles from that architecture — coding standards,
testing standards, dependency policy — and those are **binding on Dev-Team**, not
advisory.

**Acceptance comes before merge.** Project-Lead checks the diff against the
requirement's acceptance criteria — the requirement, not the spec, because the spec
is an interpretation and the requirement is the commitment. Only then does Dev-Team
merge.

## The review gate

Each team is critiqued by its own duck: an independent agent, in its own context,
that reviews the team's output and decides whether it may proceed. At least two
rounds always run, even when the first one passes.

The interesting part is what the lead is *not* told.

A lead that knows the passing standard will aim at the standard — it works out what
it can get away with, does exactly that much, and stops. So the standard is kept
from it. The standard lives in exactly one file, loaded only by ducks. Lead agents
contain no score, no threshold, and no severity vocabulary. A lead that asks its
duck what it would take to pass has that request recorded against it as a defect.

The duck is guarded from the other direction too. Its verdict is *computed* from
findings that each cite concrete evidence, so it cannot simply assert that work is
good enough to end the loop — and anyone reading the ledger afterwards can
recompute the verdict and check that it was earned. It is also told explicitly that
a change satisfying the letter of a finding without its substance — narrowing scope
to dodge a criterion, deleting a failing case, weakening a test — is not a fix.

Neither side can shortcut the gate, which is the point.

## Concurrency

> Project-Lead runs as the root agent. Every team may run at most 2 subagents in
> parallel. More than 2 is not allowed.

Project-Lead may have at most two teams active at once, so at most four agents are
ever working. The limit is fixed rather than dynamically allocated because agents
cannot reliably share a counter across separate contexts — a static rule is
verifiable by inspection, and `list_agents` confirms it at runtime.

Parallel work is isolated by **workstream**: each declares a file scope that may not
intersect another's, and gets its own git worktree and branch.

## What it writes

```
.project-memory/          Project Memory          Project-Lead
.software-team/           Ledgers, workstreams    append-only
docs/requirements/        REQ-NNN                 Project-Lead
docs/research/            Findings, cited         Research-Team
docs/ux/                  Briefs, wireframes      UX-Team
docs/specs/REQ-NNN/       Feature specs           PM-Team
docs/architecture/        Architecture, ADRs, principles   Architect-Team
```

Every one of these is an [Open Knowledge Format](https://openknowledgeformat.org)
v0.2 bundle: typed documents, explicit provenance, ISO-8601 timestamps with UTC
offsets, real markdown links, and footnote labels that resolve to declared sources.
That last rule matters most for research — a claim without a source is not a
finding.

## Install

```
copilot plugin marketplace add satishc-dev/maruti
copilot plugin install software-team@maruti
```

Then, in the repository you want to work in:

```
@st-project-lead bootstrap
```

Bootstrap is idempotent — it reports what it created versus what was already there,
never overwrites, and is safe to re-run.

After that, just talk to it:

```
@st-project-lead I want users to be able to export their account data as CSV
```

## Contracts

The behaviour of every agent is defined in [`docs/`](docs/). Agents load these; they
are not background reading.

| Contract | Defines |
|---|---|
| [`ROLES.md`](docs/ROLES.md) | The six teams, their authority, the RACI, escalation |
| [`RUBBER-DUCK-PROTOCOL.md`](docs/RUBBER-DUCK-PROTOCOL.md) | The review standard — **duck agents only** |
| [`PARALLELISM.md`](docs/PARALLELISM.md) | Workstreams, worktrees, the concurrency limit |
| [`LIFECYCLE.md`](docs/LIFECYCLE.md) | States, gates, compare-and-swap transitions |
| [`HANDOFF-PROTOCOL.md`](docs/HANDOFF-PROTOCOL.md) | Envelopes, receipts, consultation, escalation |
| [`ARTIFACTS.md`](docs/ARTIFACTS.md) | Every document schema and naming convention |
| [`OKF-PROFILE.md`](docs/OKF-PROFILE.md) | OKF v0.2 across all six bundles |
| [`MEMORY-SCHEMA.md`](docs/MEMORY-SCHEMA.md) | Project Memory, ownership, projections |
| [`GITHUB-INTEGRATION.md`](docs/GITHUB-INTEGRATION.md) | Projects v2, issues, PRs |
| [`CADENCE.md`](docs/CADENCE.md) | Cycles, journals, budgets, retrospectives |
| [`GLOSSARY.md`](docs/GLOSSARY.md) | One meaning per term |

`RUBBER-DUCK-PROTOCOL.md` is restricted. If you are working on this package, note
that pasting its contents into any lead agent silently defeats the review design —
there is an audit for exactly this.

## Concurrency correctness

The Project Memory design this package inherits assumed a single writer. Running six
teams at once breaks that assumption, so each hazard is addressed explicitly:

| Hazard | Countermeasure |
|---|---|
| Many roles writing shared memory | One owning writer per path; others propose |
| `REQ-NNN` allocated by scanning files — two writers collide | Project-Lead is the sole, serialized allocator |
| Lifecycle edits are last-write-wins | `version` field with a compare-and-swap predicate |
| Union-merged log has no ordering or identity | Ledger entries carry event id, actor, workstream |
| Registers and indexes are hand-edited summaries | Demoted to generated projections |
| No multi-team namespace | `workstream_id` and `owner` on every artifact |
| Board state oscillates between writers | One board writer; the rest queue requests |
| Unbounded agent fan-out | Fixed limit of 2 subagents per team, 2 teams at once |

## Scope

**GitHub only.** Azure DevOps is not supported.

**Copilot CLI only.** There is no Claude Code variant — Copilot CLI supports nested
agent dispatch and multi-turn peer messaging between agents, and this design depends
on both.

Roles deliberately left out, to hold the team at six: security reviewer, technical
writer, release engineer, bug triage, scrum master. [`ROLES.md`](docs/ROLES.md#9-roles-deliberately-not-included)
records where their duties currently land, so any of them can be split out later
without redesigning the protocol.
