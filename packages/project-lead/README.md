# Project Lead

A stakeholder-facing **Project Lead** agent for Claude Code and GitHub Copilot CLI. The Project Lead is the lead and front-face of a project to its stakeholder (you). It owns the conversation — requirements in, status out — and **gets the work done by delegating** to the [`pm-team`](../pm-team/) and [`dev-team`](../dev-team/) plugins. It never writes specs or code itself.

The Lead maintains two complementary surfaces:

- **Project Memory** — a pure-markdown, Obsidian-readable compounding wiki under `.project-memory/`, following [Karpathy's LLM knowledge-base pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). This is the Lead's working brain; you can open the folder in Obsidian to inspect how the agent reasons and works.
- **GitHub Project (v2)** — a linked Kanban board that is the stakeholder-facing progress view. The Lead keeps it current so at any point you can see the requirements→delivery funnel and discuss it.

Requirements are first-class, **official repo documents** under `docs/requirements/`, approved through a **requirement PR** before any spec work begins.

## Roles

- **`project-lead`** (skill on Claude Code / chat-mode agent on Copilot) — the orchestrator and stakeholder interface. Captures and refines requirements, maintains the Project Memory and the GitHub Project Kanban, and runs the **guided-handoff** lifecycle: it launches/recommends `/pm-team` and `/dev-team` at the right moments and reconciles their outputs back into memory + the board. It respects the existing signoff gates of those teams and adds its own **requirements approval gate**.
- **`/project-lead`** (slash command on Claude Code) — kickoff with subcommands: `bootstrap`, intake (no subcommand), `requirement`, `approve`, `status`, `sync`, `lint`.

## Install

**Claude Code** — from a Claude Code session in the target repo:

```
/plugin marketplace add satishc2437/maruti
/plugin install project-lead@maruti
```

**GitHub Copilot CLI** — from a Copilot CLI session in the target repo:

```
copilot plugin marketplace add satishc2437/maruti
copilot plugin install project-lead@maruti
```

For each platform, the marketplace-add line is one-time per machine; subsequent installs only need the install line. For local-checkout and project-local-copy alternatives, see [`claude-code/README.md`](claude-code/README.md#install) and [`github-copilot/README.md`](github-copilot/README.md).

The Project Lead is designed to be installed into **all your repos** and bootstrapped once per repo, so future development across your projects follows the same model.

## Relationship to pm-team and dev-team

```
Stakeholder (you)
      │  requirements / questions / status
      ▼
┌──────────────────────────────────────────────┐
│  Project Lead                                  │
│  - requirements interface + approval gate      │
│  - maintains .project-memory/ (the wiki)       │
│  - maintains the GitHub Project (Kanban)       │
│  - guided handoff orchestration                │
└───────┬────────────────────────┬───────────────┘
        │ launches/recommends     │ launches/recommends
        ▼                         ▼
   /pm-team  ──spec PR / issues──►  /dev-team ──► PR
        │                         │
        └── outputs reconciled ───┘
            back into memory + board by the Lead
```

The Lead does **not** replace pm-team or dev-team — it sits above them as the
single stakeholder-facing coordinator and the keeper of durable project context.

## Bootstrap

`/project-lead bootstrap` is idempotent and re-runnable. It:

1. Scaffolds `.project-memory/` (the wiki skeleton + `schema.md`).
2. Scaffolds `docs/requirements/` (`_template.md` + an empty `README.md` register).
3. Detects or helps you create + link a **GitHub Project (v2)** Kanban, persisting the link in `.project-memory/project-link.md`.
4. Detects the org's custom **issue type "Requirement"** (falls back to a `requirement` label) and, on GitHub, ensures the `requirement` label exists.
5. Checks that `pm-team` and `dev-team` are available, and guides you to install them if not.
6. Writes a pointer to the Project Lead conventions into `AGENTS.md` / `CLAUDE.md`.

## Requirements & the approval gate

Requirements live as official, versioned repo docs and are approved before pm-team engages. Two intake paths both converge on a doc you approve:

- **Path A — you author it:** drop a short requirement doc or rough notes; the Lead formalizes it into `docs/requirements/REQ-NNN-<slug>.md`.
- **Path B — brainstorm:** brainstorm the vision/scenario with the Lead; it drafts the doc for your review.

**Approval = a requirement PR** (mirrors pm-team's spec-PR pattern): the Lead opens a PR with the doc, you review & approve/merge, and that merge is the official signoff. An express in-chat signoff is available for tiny edits. The Lead **must not** invoke `/pm-team` until the requirement is `approved`.

GitHub-native concepts are leveraged for tracking: each requirement gets a **Requirement issue** (custom issue type when the org has it, else a `requirement` label), and pm-team's Feature/Story issues become **sub-issues** of it — giving end-to-end Requirement → Feature → Story traceability with roll-up on the board.

The full memory layout, requirement doc schema, lifecycle, Definition of Ready, and approval contract are in [`MEMORY-SCHEMA.md`](MEMORY-SCHEMA.md).

## Lifecycle (guided handoff)

| Phase | Lead action | Requirement status | Board column |
|---|---|---|---|
| Capture | Create `docs/requirements/REQ-NNN.md` (Path A or B) + log + draft item | `draft` | Intake |
| Refine | Iterate doc; apply Definition of Ready | `in-review` | In Review |
| **Approve** | Open requirement PR; you approve/merge; create Requirement issue | `approved` | Ready for Spec |
| Spec | Launch/recommend `/pm-team`; spec PR | `in-spec` | In Spec |
| Seed | pm-team seeds Feature/Story issues as sub-issues | `specced` | Ready for Dev |
| Build | Recommend `/dev-team <issue>` per child; PRs | `in-delivery` | In Dev / In Review |
| Accept | Verify against acceptance criteria; optional acceptance signoff | `delivered` | Done |

## Platform notes

- **GitHub Projects (v2) is GitHub-specific.** On repos whose tracker is Azure
  DevOps, the Lead degrades gracefully: Project Memory and the guided handoff
  still work, and the Kanban step uses ADO Boards instead. The primary target is
  GitHub.
- The teams keep their own `.scrum/` working memory; the Lead's
  `.project-memory/` is the higher-level, durable project wiki that references
  (never duplicates) team artifacts.

## Layout

```
packages/project-lead/
├── README.md                                    # this file
├── MEMORY-SCHEMA.md                             # .project-memory/ + docs/requirements/ layout, schemas, workflows
├── claude-code/                                 # installable Claude Code plugin
│   ├── .claude-plugin/plugin.json
│   ├── README.md                                # install / usage
│   ├── skills/
│   │   └── project-lead/
│   │       └── SKILL.md
│   └── commands/
│       └── project-lead.md
└── github-copilot/                              # installable Copilot CLI plugin
    ├── agents/
    │   └── project-lead.agent.md
    └── README.md
```

## Future extensions (not built)

- A scheduled status digest the Lead posts to the stakeholder.
- Azure DevOps "Requirement" work-item-type parity with the GitHub mapping.
- A small search tool over `.project-memory/` once a project's wiki grows large.
