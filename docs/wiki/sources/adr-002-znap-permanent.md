---
title: ADR-002 — znap permanent + ziro-defer canonical
tags: [adr, backend, znap, ziro-defer]
sourceRefs: ["/home/ali/.ziro/.specify/decisions/ADR-002-znap-permanent-zirodefer.md"]
lastReviewed: 2026-09-24
---

See [[entities/znap-runtime]] for the current spec impact.

## Decision

1. znap is the **permanent** runtime backend (ADR-001 superseded).
2. ziro-defer is the **canonical** deferral engine (fork of upstream zsh-defer).
3. Upstream zsh-defer remains available for users who prefer it; ziro-defer is
   a superset.

## Benchmark that settled it (PR #19)

| Config | command_lag |
|---|---|
| Znap eager | 17.6 ms |
| **Znap + zsh-defer** | **0.04 ms ← winner** |
| Zinit eager | 17.0 ms |
| Zinit turbo | 17.2 ms |

## Consequences

- Spec 005 rewritten: "znap Optimization + ziro-defer"
- Constitution: add Principle XI, bump to v0.1.4
- Spec 002 renamed: "Layer 3 znap Runtime"
- Spec 004 bootstrap installs ziro-defer (fallback to zsh-defer)
