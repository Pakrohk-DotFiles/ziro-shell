---
title: ADR-003 — Two-Layer Architecture
tags: [adr, architecture, python, zsh]
sourceRefs: ["/home/ali/.ziro/.specify/decisions/ADR-003-two-layer-architecture.md"]
lastReviewed: 2026-09-24
---

Ziro needs both performance (hot-path < 5 ms) and rich functionality. Split:

## Layer A — Python Core (`~/.ziro/ziro/` or `core/`)

Used ONLY for heavy operations that run in cold path:
- Plugin source analysis (Layer 1 analyzer)
- Tag resolution (Layer 2 resolver)
- `plugins.gen.zsh` generation (Layer 2 generator)
- Rich progress bars and formatted output (spec 008)

**Never loaded in hot path.** Invoked via subprocess only when needed.
Stdlib only, no PyO3. Python 3.12+.

## Layer B — Zsh CLI + Plugins

CLI dispatch, small commands, shell integration, ZLE plugins
([[entities/ghost-plugin]]).

Related: spec 008 (Modular CLI), spec 001 (Plugin Analyzer).
Contrast with the runtime-layer model in [[entities/ziro]]:
Layer A ≈ L1+L2 of spec 000, Layer B ≈ L0+L3.

## Trace

Layer A/B are the *implementation* axes; Layers 0–3 of spec 000 are the
*responsibility* axes. Both models describe the same code:
`analyzer/`/`resolver/`/`runtime/`/`cli/`/`prompts/`/`themes/`/`shared` under
`ziro/` (roadmap Phase 0, Step 1).

## Sovereignty invariant

Layer A (Python core) is never a runtime dependency of a published plugin —
see [[concepts/plugin-sovereignty]].
