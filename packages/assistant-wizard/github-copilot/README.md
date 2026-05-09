# Assistant-Wizard — GitHub Copilot variant

Installable form of Assistant-Wizard for use in GitHub Copilot Chat.

## Install

### Option A — direct download (no local checkout)

From the root of the target repository:

```bash
# Linux / macOS
mkdir -p .github/agents
curl -fsSL https://raw.githubusercontent.com/satishc2437/maruti/main/packages/assistant-wizard/github-copilot/agents/assistant-wizard.agent.md \
  -o .github/agents/assistant-wizard.agent.md
```

```powershell
# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path .github\agents | Out-Null
Invoke-WebRequest `
  -Uri https://raw.githubusercontent.com/satishc2437/maruti/main/packages/assistant-wizard/github-copilot/agents/assistant-wizard.agent.md `
  -OutFile .github\agents\assistant-wizard.agent.md
```

To pin to a specific tag or branch, replace `main` in the URL.

### Option B — install script (requires a maruti clone)

Run from this directory, passing the path to the consuming repository (defaults to the current directory):

```bash
# Linux / macOS
./install.sh /path/to/target-repo

# Windows (PowerShell)
.\install.ps1 -Target C:\path\to\target-repo
```

The script copies the chat mode into `<target>/.github/agents/`.

### Option C — manual copy

```bash
mkdir -p <target>/.github/agents
cp agents/assistant-wizard.agent.md <target>/.github/agents/
```

## Usage

In VS Code with Copilot Chat, the agent appears in the chat-mode picker as **Assistant-Wizard**.

1. Open Copilot Chat.
2. Switch the chat mode to **Assistant-Wizard**.
3. Describe what you want to build.

Assistant-Wizard will then ask which target environment(s), capture your intent, recommend the right primitive per environment, and generate a deployable payload at `packages/<new-name>/`.
