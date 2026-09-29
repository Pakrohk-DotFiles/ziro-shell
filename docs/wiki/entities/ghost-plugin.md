---
title: ziro-ghost plugin
tags: [ghost, zle, autosuggestion, plugin, sovereignty]
sourceRefs: ["/home/ali/.ziro/ghost/ghost.zsh", "/home/ali/.ziro/.specify/specs/009-ziro-ghost-plugin/spec.md"]
lastReviewed: 2026-09-24
---

ZLE autosuggestion plugin. Reference implementation of
[[concepts/plugin-sovereignty]]. Current spec is **009**; spec 007 is
deprecated.

## Files

- `ghost/ghost.zsh` — ZLE widget registration and behavior
- `ghost/ghost-pl.zsh` — prompt-loop machinery
- `ghost/ghost-config.zsh` — configuration
- `ghost/ghost-completion.zsh` — completion integration

## Sovereignty in practice

- Lives at `$ZIRO_HOME/ghost/`, but is **not** a ziro module. It is a
  standalone plugin that can be sourced anywhere.
- Loaded in `.zshrc` conditionally: if `ZSH_AUTOSUGGEST_DISABLE == "yes"`,
  `source` ghost directly instead of loading zsh-autosuggestions via znap
  ([[concepts/znap-plugin-loading]]).
- No `source`-time dependency on ziro's runtime state.

## ZLE hooks

1 ZLE hook (`zle-line-pre-redraw`) + 4 custom widgets (`accept_full`, `accept_word`, `dismiss`, `popup`). Only `zle-line-pre-redraw` is registered as a ZLE hook; the other 4 are user-defined widgets bound to keys, not hooks. Verified against `ghost/ghost.zsh:209-213`. No background timers, no polling.

Load-ordering constraint: must source after `compinit` because it registers
ZLE widgets. Deferred via `ziro-defer source` — see
[[entities/znap-runtime]].

## Related

[[entities/shell-bootstrap]] · [[concepts/plugin-sovereignty]]
