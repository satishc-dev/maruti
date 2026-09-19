---
type: Risk
title: Board API rate limits
description: Large board syncs could hit GitHub API limits and delay status reconciliation.
tags: [risk, github]
generated: { by: project-lead/claude-code, at: 2026-09-18T18:00:00Z }
status: stable
stale_after: 2026-09-19T00:00:00Z
sources:
  - id: github-rate-limits
    resource: https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api
    title: GitHub REST API rate limits
    author: GitHub
    usage_count: 4
    last_modified: 2026-09-01T00:00:00Z
usage_window: { from: 2026-09-01T00:00:00Z, to: 2026-09-18T23:59:59Z }
---

# Risk

A broad sync across many Project items may exhaust the available API budget and
leave the board temporarily stale.[^github-rate-limits]

# Mitigation

Prefer incremental syncs and report partial reconciliation if rate limits are
encountered.

[^github-rate-limits]: GitHub documents primary and secondary API rate limits.
