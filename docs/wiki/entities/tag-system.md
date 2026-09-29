---
title: Tag System (Layer 2)
tags: [layer2, tags, resolver, generator, toml]
sourceRefs: ["/home/ali/.ziro/.specify/specs/002-tag-system/spec.md", "/home/ali/.ziro/.specify/specs/003-tag-resolution/spec.md"]
lastReviewed: 2026-09-24
---

User control and resolution. Specs 002 + 003. Layer A per
[[sources/adr-003-two-layer-architecture]].

## Two specs, one layer

- **spec 002** — user tag files, Schema B:
  `~/.config/ziro/tags/plugins/<plugin>.toml`
- **spec 003** — resolution: Schema A + Schema B → Schema C

## Contract

- **in**: Schema A (from [[entities/plugin-analyzer]]) + Schema B (user tags)
- **out**: Schema C — `$ZIRO_CONFIG/derived/plugins.gen.zsh`
- **budget**: 5 s per plugin, async — cold path only
  ([[concepts/hot-path-cold-path]])
- **constraint**: Layer 1 must not write tag files; Layer 2 owns
  `~/.config/ziro/` (see [[concepts/xdg-path-layout]])

## Output consumer

[[entities/znap-runtime]] (Layer 3) sources the prebuilt `plugins.gen.zsh`
in the hot path — Layer 2 never runs at startup. This separation is what
lets the rich Python resolver coexist with a 5 ms budget.

Default-on but user-disableable (Constitution XII).
