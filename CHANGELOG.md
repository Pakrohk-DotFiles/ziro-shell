# Changelog

All notable changes to ziro-shell are documented here.

## [1.0.0] — 2026-09-24

### Added

- **Layer 0**: Shell bootstrap (`integration.zsh`, `ziro.zsh` dispatcher)
- **Layer 1**: Plugin analyzer with regex signal detection (compdef, ZLE, hooks, bindkey, eval, PATH)
- **Layer 2**: Tag system (7 built-in tags, conflict detection, TOML-based user overrides)
- **Layer 3**: `ziro_load` frozen interface + plugins.gen.zsh generator
- **T1/T2/T3**: Prompt abstraction (starship, p10k, pure, none) + theme provider + resolver
- **CLI**: `install`, `plugin`, `tag`, `config`, `suggest`, `theme`, `prompt`, `doctor`, `bench`
- **Analyzer cache**: hash-based invalidation in `~/.cache/ziro/analysis/`
- **Async analysis**: `analyze_many` with asyncio parallel execution
- **Hook re-registration**: compensating registration for `wd`, `alias-tips`
- **--raw escape hatch**: verbatim injection for power users
- **Parity test suite**: deferred vs eager behavior equivalence
- **CI**: GitHub Actions test workflow (Python 3.11, 3.12)

### Benchmarks

- Hot-path: `< 5ms` Ziro contribution (target met)
- 127 unit tests + 2 integration tests

### Architecture

- See `ARCHITECTURE.md` for layer model and frozen interfaces
- State management: config/cache/derived separation per Constitution Principle V

### Documentation

- `README.md` — quick start
- `INSTALL.md` — installation guide
- `ARCHITECTURE.md` — layer model
- `.specify/specs/` — 9 active specs + constitution (local-only)

## Pre-release history

See git log for Phase 0 through Phase 6d commits.
