---
title: XDG path layout
tags: [xdg, paths, config, concept]
sourceRefs: ["/home/ali/.ziro/lib/xdg.zsh", "/home/ali/.ziro/.specify/specs/000-architecture/spec.md"]
lastReviewed: 2026-09-24
---

`lib/xdg.zsh` is the single source of truth for ziro's paths (Constitution
IV). Hot path: sourced by [[entities/shell-bootstrap]] and every command.

## Defaults

| Var | Default |
|---|---|
| `XDG_CACHE_HOME` | `$HOME/.cache` |
| `XDG_CONFIG_HOME` | `$HOME/.config` |
| `XDG_DATA_HOME` | `$HOME/.local/share` |
| `ZIRO_HOME` | `$HOME/.ziro` |

All four print to stdout via `print` (not `echo`) — safe with special
characters. ~23 lines, zero dependencies.

## Ziro-derived paths

| Path | Location | Owner |
|---|---|---|
| `ZIRO_CACHE` | `${XDG_CACHE_HOME:-$HOME/.cache}/ziro` | not exported; derived at use |
| Log file | `$ZIRO_CACHE/logs/ziro.log` | [[entities/cli]] |
| Analysis cache (Schema A) | `$ZIRO_CACHE/analysis/<plugin>.json` | [[entities/plugin-analyzer]] |
| Generated plugin list (Schema C) | `$ZIRO_CONFIG/derived/plugins.gen.zsh` | [[entities/tag-system]] |
| Tag files (Schema B) | `$XDG_CONFIG_HOME/ziro/tags/plugins/<plugin>.toml` | [[entities/tag-system]] |
| Tools registry | `$XDG_CONFIG_HOME/ziro/tools.toml` | spec 006 |

## Boundary rule

Layer 1 is forbidden from writing to `~/.config/ziro/` — tag files are
Layer 2's job. This keeps [[entities/plugin-analyzer]] and
[[entities/tag-system]] cleanly separated, and keeps the hot path free of
file parsing ([[concepts/hot-path-cold-path]]).

## Gotcha

`lib/log.zsh` sets `typeset -g _ZIRO_LOG_LEVEL` at **source time**, so
re-sourcing does not reset it (default `warn`). Priority map:
`debug 0, info 1, warn 2, error 3`; `error`/`warn` print to stderr. This is
why command modules must not assume log level persists across re-source.
