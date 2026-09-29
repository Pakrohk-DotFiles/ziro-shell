---
title: Ziro framework overview
tags: [overview, architecture, layers, roadmap]
sourceRefs: ["/home/ali/.ziro/.specify/specs/000-architecture/spec.md", "/home/ali/.ziro/.specify/roadmap.json", "/home/ali/.ziro/.specify/memory/constitution.md"]
lastReviewed: 2026-09-29
---

Ziro is a **zsh configuration framework**: fast startup, plugin analysis, and
tag-driven plugin loading. Znap-based, ziro-defer-deferred, Python-3.12 core.

## Governing documents (rank order)

1. **Constitution** (`.specify/memory/constitution.md`) — outranks roadmap
   principles on conflict. Key principles: IV (XDG), XII (Layered
   Optionality), XIII (Prompt Neutrality), XIV
   ([[concepts/plugin-sovereignty]]).
2. **Roadmap** (`.specify/roadmap.json`) — principles P1–P5, phases.
3. **Specs** 000–009 (below).
4. **ADRs** — ADR-002, ADR-003; ADR-001 **superseded**.
5. **Code** — fallback when no spec covers it.

## Layer model (spec 000)

| Layer | Responsibility | Page |
|---|---|---|
| 0 | Shell bootstrap | [[entities/shell-bootstrap]] |
| 1 | Plugin analysis (Python) | [[entities/plugin-analyzer]] |
| 2 | Tag resolution + generation (Python) | [[entities/tag-system]] |
| 3 | Runtime backend (znap + ziro-defer) | [[entities/znap-runtime]] |

## Implementation axes (ADR-003)

**Layer A** — Python core (L1+L2 responsibilities), cold path only.
**Layer B** — zsh CLI + plugins (L0+L3), hot path.
Axes and layers are orthogonal: A/B is *how it's built*, 0–3 is *what it
does*. See [[sources/adr-003-two-layer-architecture]].

## Spec map

| Spec | Title | Status |
|---|---|---|
| 000 | Architecture | current |
| 001 | Plugin Analyzer (Layer 1) | current |
| 002 | Tag System (Layer 2) | current |
| 003 | Tag Resolution (Layer 2) | current |
| 004 | Shell Bootstrap | current |
| 005 | znap Optimization + ziro-defer | current |
| 006 | Tools Registry (`tools.toml`) | current |
| 008 | Modular CLI | current |
| 009 | Ghost autosuggest | current |
| 007 | Ghost autosuggest | **deprecated** — superseded by 009 |

## v1.0.0 layout (flat `core/`)

The `ziro/` DDD hexagonal package (`domain/`, `ports/`, `adapters/`,
`application/`) is **DEPRECATED** as of v1.0.0 (see `ziro/DEPRECATED.md`).
The live codebase is flat: `core/` holds all Python modules (`analyzer.py`,
`resolver.py`, `generator.py`, `ziro_load.py`, CLI modules, …), with
`commands/`, `lib/`, `tests/`, `vendor/`, and `docs/` alongside.

Deprecated package, not deleted, because it documents the pre-ADR-003 design.

## Non-goals

- No backend churn: znap is permanent post-ADR-002. The `ziro_load` adapter
  contract means Layer 1/2 never depend on backend identity.
- No prompt lock-in: Constitution XIII (Prompt Neutrality).

## Audit (2026-09-29)

Full audit in `docs/audit/FEATURE-AUDIT.md`:
- **35 components**: 32 PASS, 3 PARTIAL (bug #2 defer naming, bench granularity, plugins.d design gap)
- **129 tests pass**
- **Start-up**: 3.22 ms total zsh startup (min), within 5 ms budget
- **Doctor**: 8/8 healthy
- **Verdict**: ready for v1.0.0

