# Ziro-Shell Architecture

Ziro is layered Zsh runtime customization system. Each layer has
one responsibility, communicates via frozen interfaces, and runs
either in hot-path (< 5ms) or cold-path (user-invoked).

## Layered Model

```
┌─────────────────────────────────────────────────────────────┐
│ L0 — Shell Bootstrap (< 5ms, hot)                           │
│     integration.zsh → source vendor + plugins.gen.zsh       │
├─────────────────────────────────────────────────────────────┤
│ L1 — Plugin Analyzer (cold)                                 │
│     Static regex scan → Schema A (analysis JSON)            │
├─────────────────────────────────────────────────────────────┤
│ L2 — Tag System (cold)                                      │
│     Merge analysis + user tags → Schema C                   │
├─────────────────────────────────────────────────────────────┤
│ L3 — znap Runtime (hot, emit-only)                          │
│     ziro_load interface → znap source / ziro-defer          │
└─────────────────────────────────────────────────────────────┘
```

## Hot-path budget

- **Target**: Ziro contribution < 5ms per shell startup
- **Measured by**: `ziro bench` (min-of-11)
- **Enforced by**: no Python, no subprocess, no file parsing in L0

## Frozen interfaces

| Interface   | Location                                  | Consumed by   |
|-------------|-------------------------------------------|---------------|
| Schema A    | `~/.cache/ziro/analysis/*.json`           | L2 resolver   |
| Schema B    | `~/.config/ziro/tags/`                    | L2 resolver   |
| Schema C    | `~/.config/ziro/derived/plugins.gen.zsh`  | L0 bootstrap  |
| `ziro_load` | `core/ziro_load.py`                       | L2 generator  |

## State management

| Location                     | Category       | Deletable        |
|------------------------------|----------------|------------------|
| `~/.config/ziro/`            | user config    | No               |
| `~/.config/ziro/derived/`    | generated      | Yes (regenerate) |
| `~/.cache/ziro/`             | ephemeral      | Yes              |
| `~/.ziro/`                   | vendored runtime | No             |

## CLI surface

| Command                                    | Layer   | Spec      |
|--------------------------------------------|---------|-----------|
| `ziro install`                             | L0      | 006       |
| `ziro plugin add/remove/list/show`         | L1+L2+L3| 001, 002, 003 |
| `ziro tag list/show/add/remove/reset`      | L2      | 003       |
| `ziro config show/edit`                    | L0      | 006       |
| `ziro suggest list/set/disable`            | L0      | 006       |
| `ziro theme list/current/apply/reset`      | T2      | 006       |
| `ziro prompt list/current/set`             | T1      | 006       |
| `ziro doctor`                              | L0      | 006 SC-1  |
| `ziro bench`                               | L0      | 005 SC-1  |

## Non-goals

- Zinit integration (permanently removed, ADR-002)
- IRIS integration (permanently removed)
- Python in hot-path
- Network access in hot-path

## See also

- `README.md` — user guide
- `INSTALL.md` — installation
- `CHANGELOG.md` — version history
- `.specify/specs/` — detailed specifications (local-only)

## Legacy code

`~/.ziro/ziro/` contains early DDD hexagonal architecture that is
**deprecated** as of v1.0.0. It is not imported by any active code.
See `~/.ziro/ziro/DEPRECATED.md` for full explanation and removal timeline.

Active code lives in:
- `~/.ziro/core/` — Python core (flat modules)
- `~/.ziro/commands/` — Zsh CLI modules
- `~/.ziro/lib/` — Zsh helpers
- `~/.ziro/prompts/` — Prompt adapters
- `~/.ziro/themes/` — Theme files
