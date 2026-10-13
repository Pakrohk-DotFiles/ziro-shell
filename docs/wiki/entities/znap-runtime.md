---
title: zsnap / znap runtime (Layer 3)
tags: [layer3, znap, ziro-defer, runtime, backend]
sourceRefs: ["/home/ali/.ziro/.specify/specs/005-znap-optimization/spec.md", "/home/ali/.ziro/.specify/decisions/ADR-002-znap-permanent-zirodefer.md", "/home/ali/.ziro/integration.zsh"]
lastReviewed: 2026-09-29
---

Layer 3 is the runtime backend: plugin fetching, caching, deferred loading.
Spec 002. Frozen as znap by [[sources/adr-002-znap-permanent]] — backend
migrations are a non-goal.

## Components

- **znap** — plugin management: `znap source <owner>/<repo>` clones and
  sources. Local `.zsh` files are **not** supported — see
  [[concepts/znap-plugin-loading]].
- **ziro-defer** — canonical deferral engine, a fork of upstream zsh-defer.
  Upstream remains available; ziro-defer is a superset.
  Loaded from `$ZIRO_HOME/ziro-defer/ziro-defer.plugin.zsh` (canonical fork
  dir, v0.1.0 — see [[entities/ziro-defer]]).

## Contract

- **in**: Schema C — `$ZIRO_CONFIG/derived/plugins.gen.zsh` (see
  [[entities/tag-system]])
- **out**: loaded, functional plugins
- **budget**: hot path, shares the 5 ms total ([[concepts/hot-path-cold-path]])
- **constraint**: Layer 1/2 never depend on backend identity — they emit
  `ziro_load` calls to an adapter

## Deferred loading

ZLE plugins are deferred, e.g. ghost:

```zsh
ziro-defer source "$ZIRO_HOME/ghost/ghost.zsh"
```

Deferred plugins still respect [[concepts/plugin-sovereignty]]: they must work
if loaded eagerly instead.

## Why znap

Benchmark, not preference — PR #19: znap + zsh-defer hit **0.04 ms** command
lag against ~17 ms for zinit turbo and ~17.6 ms for znap eager.
