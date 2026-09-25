# ziro-shell

> A fast, modular Zsh configuration framework.
> Layer 0 bootstrap → Layer 3 plugin runtime.

## What it does

**ziro-shell** manages your Zsh config as a layered framework instead of a
monolithic `.zshrc`. Each layer has one responsibility and a strict performance
budget. The hot path — sourced on every shell start — targets **< 5ms**
(Spec 004 R1).

## Architecture

```
~/.zshrc                     ← entrypoint (sources integration.zsh)
~/.ziro/integration.zsh      ← Layer 0: bootstrap
~/.ziro/lib/                 ← shared helpers
~/.ziro/commands/            ← Zsh CLI command modules
~/.ziro/core/                ← Python core (cold-path only)
~/.ziro/vendor/              ← vendored runtimes (znap, ziro-defer)
~/.ziro/prompts/             ← prompt themes
~/.ziro/themes/              ← color schemes
```

### The layers

| Layer | Responsibility | Location |
|-------|---------------|----------|
| 0 | Shell bootstrap | `integration.zsh` |
| 1 | Config parsing & plugin analysis | Python core (`core/`) |
| 2 | Plugin resolution & generation | Python core → `plugins.gen.zsh` |
| 3 | Plugin runtime | `vendor/znap/` |

The full layer model and the reasoning behind the Python/Zsh split are recorded
in [ADR-003](.specify/decisions/ADR-003-two-layer-architecture.md).

## Backend

Ziro does not write its own plugin manager. It builds on two proven projects:

- **znap** — the permanent runtime backend. Installed at `~/.ziro/znap/`,
  exposed at `vendor/znap/znap.zsh` via a symlink.
- **ziro-defer** — a fork of upstream `zsh-defer` with additional features.
  Ziro's canonical deferral engine.

The deferral fallback chain in `integration.zsh` (Spec 004 R2):

```
ziro-defer.plugin.zsh → zsh-defer.plugin.zsh → zsh-defer command → eager stub
```

See [ADR-002](.specify/decisions/ADR-002-znap-permanent-zirodefer.md) for the
benchmark (`command_lag 0.04ms` for znap + zsh-defer vs `17.2ms` for zinit
turbo) and the decision record.

## Getting started

Requirements: **Zsh ≥ 5.2**, **git**. Python is optional — only needed for the
plugin analyzer and Rich progress bars (ADR-003).

```sh
git clone https://github.com/<user>/ziro-shell.git ~/.ziro
ln -sf ~/.ziro/.zshrc ~/.zshrc   # or source it from your existing ~/.zshrc
```

Then start a new shell. Ziro is idempotent — the `(( ${+ZIRO_LOADED} ))` guard
makes re-sourcing safe.

## Layout conventions

- **Hot path** (`integration.zsh`): sourced every shell start. No Python, no
  subprocess, no network. Stays under the 5ms budget.
- **Cold path** (`core/` Python core): heavy analysis, tag resolution, file
  generation. Invoked via subprocess only when needed.
- **CLI** (`commands/`, `lib/`, `ziro.zsh`): always available, sourceable
  standalone, minimal overhead.
- **Generated files** (`*.gen.zsh`): machine-written, never hand-edited.

## Specs & decisions

Architecture decisions live in `.specify/decisions/` as ADRs. They are local
to this machine and are **not** committed to the public repo (see
`.gitignore`).

| ADR | Topic |
|-----|-------|
| [ADR-002](.specify/decisions/ADR-002-znap-permanent-zirodefer.md) | znap permanent backend + ziro-defer |
| [ADR-003](.specify/decisions/ADR-003-two-layer-architecture.md) | Two-layer Python/Zsh architecture |
| [ADR-004](.specify/decisions/ADR-004-ziro-defer-fork-timing.md) | ziro-defer fork timing |

## License

MIT
