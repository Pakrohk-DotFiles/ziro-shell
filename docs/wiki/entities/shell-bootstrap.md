---
title: Shell bootstrap (Layer 0)
tags: [layer0, bootstrap, startup, integration]
sourceRefs: ["/home/ali/.ziro/integration.zsh", "/home/ali/.ziro/.specify/specs/004-shell-bootstrap/spec.md"]
lastReviewed: 2026-09-24
---

`integration.zsh` is the hot-path entry point sourced from `.zshrc`. Owns the
5 ms startup budget — see [[concepts/hot-path-cold-path]].

## Sourcing order

1. `lib/xdg.zsh` — paths, canonical ([[concepts/xdg-path-layout]])
2. `lib/log.zsh` — logging
3. `plugins.zsh` — generated plugin list (Schema C)
4. Theme
5. `theme/*.zsh` — optional
6. ZLE plugins — e.g. `ziro-defer source` of `ghost/ghost.zsh`
   ([[entities/ghost-plugin]])
7. `aliases.zsh`

## Constraints

- **Forbidden**: any Python, any subprocess, file parsing, network I/O
- Installs ziro-defer with fallback to upstream zsh-defer
  ([[sources/adr-002-znap-permanent]])
- Local plugins are `source`d directly, never `znap source`
  ([[concepts/znap-plugin-loading]])
- ZLE plugins must source after `compinit` — they register widgets

## Output contract

- **out**: `ziro_load` calls per Schema C + the adapter implementation file
- **budget**: sourcing `plugins.gen.zsh` < 2 ms; post-prompt lazy loads not
  counted

Related: [[entities/znap-runtime]], [[concepts/plugin-sovereignty]].
