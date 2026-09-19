---
type: Decision
title: Use native sub-issues
description: Track Feature and Story work as native sub-issues under each Requirement issue.
tags: [decision, github]
generated: { by: project-lead/copilot, at: 2026-09-19T21:10:00Z }
verified:
  - { by: human:alex-owner, at: 2026-09-19T21:11:00Z }
  - { by: process:github-merge, at: 2026-09-19T21:12:00Z }
status: stable
sources:
  - id: github-docs
    resource: https://docs.github.com/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues
    title: GitHub sub-issues documentation
    author: GitHub
    usage_count: 11
    last_modified: 2026-09-01T00:00:00Z
    usage_window: { from: 2026-09-01T00:00:00Z, to: 2026-09-10T23:59:59Z }
  - id: kickoff-notes
    resource: /wiki/references/stakeholder-kickoff-notes.md
    title: Stakeholder kickoff notes
usage_window: { from: 2026-09-10T00:00:00Z, to: 2026-09-19T23:59:59Z }
---

# Decision

Use GitHub native sub-issues so each Requirement issue rolls up its Feature and
Story children.[^github-docs]

# Consequences

Project Memory links requirements to the board, while implementation work stays
in GitHub issues and PRs.

[^github-docs]: GitHub documents sub-issues as native issue relationships.
