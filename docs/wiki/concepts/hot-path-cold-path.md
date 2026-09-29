---
title: Hot path vs cold path
tags: [performance, hot-path, cold-path, budget, concept]
sourceRefs: ["/home/ali/.ziro/.specify/roadmap.json", "/home/ali/.ziro/.specify/specs/000-architecture/spec.md", "/home/ali/.ziro/integration.zsh"]
lastReviewed: 2026-09-24
---

Roadmap principle **P1**: ziro's central architectural invariant. Two budgets.

## Hot path — every shell startup

- **Budget: 5 ms total**
- Runs on every interactive shell launch.
- **Forbidden**: any Python, any subprocess, file parsing, network I/O,
  regenerating `plugins.gen.zsh`.
- Owned by Layer 0 ([[entities/shell-bootstrap]]) and Layer 3
  ([[entities/znap-runtime]]) — Layer B per
  [[sources/adr-003-two-layer-architecture]].

## Cold path — analysis and generation

- **Budget: 5 s per plugin**, async, parallel.
- Runs only when the user invokes analysis or tags change.
- Python is allowed here (Layer A): [[entities/plugin-analyzer]],
  [[entities/tag-system]].
- Output is cached to disk so the hot path never re-derives it.

## The boundary rule

Layer 1 and Layer 2 are **forbidden from running in the hot path**. They write
Schema A / Schema C artifacts to cache; Layer 3 sources the prebuilt
`plugins.gen.zsh` in < 2 ms. This is why the analyzer can be rich Python
without costing startup time — see [[concepts/xdg-path-layout]] for where the
caches live.

## Verification

Startup is benchmarked, not assumed. The backend choice itself was settled by
benchmark (PR #19): znap + zsh-defer at **0.04 ms** command lag vs ~17 ms for
alternatives — [[sources/adr-002-znap-permanent]].
