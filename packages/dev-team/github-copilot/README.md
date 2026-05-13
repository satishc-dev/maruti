# Dev-Team — GitHub Copilot variant

Installable form of Dev-Team for use in GitHub Copilot CLI as a custom agent.

## Install

From a Copilot CLI session in the target repository:

```
copilot plugin marketplace add satishc2437/maruti
copilot plugin install dev-team@maruti
```

The first command is one-time per machine; subsequent installs only need the second line.

## Manual install

If you prefer to vendor the agent directly into a repo (no plugin system):

```bash
mkdir -p .github/agents
cp agents/dev-team.agent.md .github/agents/dev-team.agent.md
```

Copilot CLI also reads `~/.copilot/agents/` for personal-scope agents if you want it available across all your projects.

## Usage

Once installed, switch to the **Dev-Team** agent in your Copilot CLI session and give it a work item:

```
@dev-team Drive work item 1234
```

Dev-Team will detect whether the tracker is Azure DevOps or GitHub from `git remote get-url origin`, fetch the work item, design the implementation, execute it (decomposing into independent units when worthwhile), self-review against the acceptance criteria, and open the PR.

## Notes vs. the Claude Code variant

The Claude Code variant of `dev-team` fans out work to a `team-lead` orchestrator plus parallel `software-developer` and `code-reviewer` subagents. Copilot CLI's chat-mode model collapses this into one orchestrator agent that does design, implementation, and self-review in-line. Use the `agent` tool inside Dev-Team to delegate genuinely independent units when worthwhile.
