---
type: Architecture Note
title: Board sync design
description: Draft reconciliation design between requirement lifecycle and the GitHub Project Status field.
tags: [architecture, sync]
generated: { by: project-lead-claude-code/0.2.0, at: 2026-09-19T20:45:00Z }
status: draft
---

# Design

Sync reads each requirement document's `lifecycle`, computes the expected board
Status column, and compares it with the GitHub Project item. The OKF `status`
key is checked only for consistency with the lifecycle mapping.
