# browser-pilot

A skill package that teaches Claude Code and GitHub Copilot agents how to
effectively use the `browser-pilot` MCP server for browser automation tasks.

## What this package provides

A **skill** (not a multi-agent team) that activates when the user mentions
browsing, web interaction, Chrome, or checking a website. The skill instructs
the agent on:

- When to use browser-pilot tools vs. other approaches
- How to sequence multi-step browser workflows (navigate -> wait -> interact)
- Best practices for reliable automation (selectors, waits, screenshots)
- Error recovery patterns

## Layout

```
packages/browser-pilot/
├── README.md                              # this file
├── claude-code/
│   ├── .claude-plugin/plugin.json         # plugin manifest
│   ├── skills/browser-pilot/SKILL.md      # skill prompt
│   └── README.md                          # install/usage
└── github-copilot/
    ├── skills/browser-pilot/SKILL.md      # skill prompt (same body)
    └── README.md                          # install/usage
```

## Relationship to the MCP tool

The MCP server lives at `mcp-tools/browser-pilot/` and provides the actual
browser automation capabilities. This package is a **prompt layer** that helps
agents use those capabilities effectively. The MCP tool works standalone with
any MCP client; this plugin adds an enhanced experience for Claude Code and
GitHub Copilot specifically.

## Install

See platform-specific READMEs:
- [Claude Code](claude-code/README.md)
- [GitHub Copilot CLI](github-copilot/README.md)
