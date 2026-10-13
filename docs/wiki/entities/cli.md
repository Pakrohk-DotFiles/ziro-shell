---
title: CLI dispatcher and command modules
tags: [cli, commands, dispatcher, zsh]
sourceRefs: ["/home/ali/.ziro/ziro.zsh", "/home/ali/.ziro/commands/help.zsh", "/home/ali/.ziro/.specify/specs/008-modular-cli/spec.md"]
lastReviewed: 2026-09-24
---

`ziro.zsh` (~31 lines) routes `ziro <command>` to
`$ZIRO_HOME/commands/<cmd>.zsh`. Layer B per
[[sources/adr-003-two-layer-architecture]].

## Dispatch logic

```zsh
emulate -L zsh
local cmd="${1:-help}"
local module="$ZIRO_HOME/commands/${cmd}.zsh"
```

- `emulate -L zsh` locks option compatibility to zsh defaults — prevents
  user-set options from breaking dispatch.
- Bare `ziro` → `help`.
- Hardcoded path: commands outside `commands/` are never discovered.
- Unknown command → `_ziro_cmd_help "unknown command: $cmd"` to stderr,
  exit 1.

## Command modules

Each `commands/*.zsh` is sovereign (spec 008). Shared helpers live in
`lib/*.zsh` — `lib/log.zsh`, `lib/xdg.zsh` (see [[concepts/xdg-path-layout]]).

`commands/help.zsh` (~32 lines): prints usage to stderr **only** if a message
is passed and non-empty (`print -u2`); always exits 0.

## Rich output (spec 008)

| Command | Presentation | Library |
|---|---|---|
| `ziro plugin show` | Panel + syntax highlight | `rich.panel`, `rich.syntax` |

Spec 008 also defines **R8 — TTY Passthrough Mechanism (CRITICAL)** for
interactive TUIs inside command modules.
