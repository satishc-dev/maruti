# marketing-guru

A proactive MBA-grade marketing advisor persona for use during an MBA Marketing Management course simulation, framed around running and growing a **bike company** and beating the competition.

Currently ships **Claude Code only**, as a Skill that activates proactively on marketing/strategy topics.

## Layout

```
packages/marketing-guru/
├── README.md                                          # this file
└── claude-code/
    ├── .claude-plugin/plugin.json                     # plugin manifest
    ├── skills/marketing-guru/SKILL.md                 # the skill body
    └── README.md                                      # Claude Code install + usage
```

## Install (Claude Code)

Recommended — via the maruti marketplace:

```
/plugin marketplace add satishc2437/maruti
/plugin install marketing-guru@maruti
```

See [`claude-code/README.md`](claude-code/README.md) for local-checkout and project-local-copy alternatives.

## Behavior at a glance

- **Trigger**: any marketing strategy, performance, positioning, or simulation conversation. Activates without being asked.
- **Style**: Socratic first (≤3 sharp questions), directive when you ask for a call.
- **Frameworks**: STP, 4Ps/7Ps, Porter's Five Forces, Ansoff, BCG, Brand Pyramid, Customer Journey, JTBD — one or two per decision.
- **Data discipline**: never invents market numbers. Reads simulation files from the working folder; will use a connected Playwright MCP server **read-only** to browse the live simulation UI. Never modifies simulation state.
