# PM-Team — GitHub Copilot variant

Installable form of PM-Team for use in GitHub Copilot CLI as a custom agent.

## Install

From a Copilot CLI session in the target repository:

```
copilot plugin marketplace add satishc2437/maruti
copilot plugin install pm-team@maruti
```

The first command is one-time per machine; subsequent installs only need the second line.

## Manual install

If you prefer to vendor the agent directly into a repo (no plugin system):

```bash
mkdir -p .github/agents
cp agents/pm-team.agent.md .github/agents/pm-team.agent.md
```

Copilot CLI also reads `~/.copilot/agents/` for personal-scope agents if you want it available across all your projects.

## Usage

Once installed, switch to the **PM-Team** agent in your Copilot CLI session. PM-Team has three modes:

```
# Fresh: kick off a new initiative
@pm-team I want to plan a feature for detecting duplicate uploads

# Feedback: address comments on an open spec PR
@pm-team address comments on PR 1234

# Approved: seed the board after the spec PR is merged
@pm-team PR 1234 is approved, proceed
```

In `fresh` mode, PM-Team interviews you, decomposes the initiative into 2–5 features, drafts a spec per feature at `docs/specs/<initiative-slug>/<feature-slug>.md`, self-reviews them, and opens a spec PR — then stops for your review. After you merge, invoke `approved <pr#>` and it seeds the Kanban board with parent Features and child User Stories ready for the `Dev-Team` agent to pick up.

The tracker platform (Azure DevOps vs GitHub) is auto-detected from `git remote get-url origin`.

## Notes vs. the Claude Code variant

The Claude Code variant of `pm-team` is structured as a `pm-team` skill that fans out to `requirements-analyst`, `spec-reviewer`, and `board-manager` subagents in parallel. Copilot CLI's chat-mode model collapses this into one orchestrator agent that runs the interview, drafts and self-reviews specs, and seeds the board in-line. Use the `agent` tool inside PM-Team to delegate when corresponding subagents are available in the consuming environment.
