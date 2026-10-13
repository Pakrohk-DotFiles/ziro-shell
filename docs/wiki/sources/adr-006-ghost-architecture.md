---
title: ADR-006 — Ghost Architecture Decisions
tags: [adr, ghost, autosuggest, architecture]
sourceRefs: ["/home/ali/.ziro/.specify/decisions/ADR-006-ghost-architecture.md"]
lastReviewed: 2026-10-13
---

# ADR-006: Ziro Ghost Architecture Decisions

**Status**: Adopted  
**Date**: 2026-10-13  
**Authors**: Ziro Shell Architecture Team  
**Relates to**: [[entities/ghost-plugin]], Spec 009 (`009-ziro-ghost-plugin`), [[concepts/plugin-sovereignty]], Constitution Principle XIV  

---

## Context

Ziro Ghost (`ghost.plugin.zsh` / `ghost/ghost.zsh`) is Ziro's self-maintained history autosuggestion component, providing `POSTDISPLAY` ghost-text rendering and fuzzy matching.

In preparing the `v1.1.0` implementation (`feat/ghost-v1.1.0`), three fundamental architectural tensions were identified between standalone plugin sovereignty, Ziro's configuration ecosystem, and shell interaction ergonomics:

1. **Config Source (Tension T1)**: Spec 009 ZR-004 specifies `zstyle` as the configuration mechanism, whereas Ziro's runtime uses declarative TOML (`~/.config/ziro/defaults.toml`, etc.).
2. **Plugin Sovereignty vs. Python Runtime (Tension T2)**: Ziro's control layer uses Python (`core/`), whereas Constitution Principle XIV dictates that every published plugin must be standalone pure Zsh with zero assumption of Ziro or Python presence.
3. **Keybinding Ergonomics (Tension T3)**: Spec 009 FR-002 defines `Ctrl-G` for history popup, raising questions regarding interaction with completion plugins like `fzf-tab` bound to `Tab`.

---

## Decisions

### 1. Configuration Source: Hybrid Model (zstyle for Hot Path, TOML for Cold Path)

- **Hot-Path Runtime**: `ghost.plugin.zsh` exclusively reads `zstyle` (pattern `:znap:ziro-ghost:*` or `:ziro:ghost:*`) and environment variables (`ZIRO_GHOST_*`). No TOML parsing, disk I/O, or external subprocesses occur on keystroke redraw.
- **Cold-Path / Ziro Management**: Ziro's declarative configuration (`defaults.toml` / `tools.toml`) manages user preferences at the ecosystem level. When generating shell configurations or running CLI helpers, Ziro emits corresponding `zstyle` directives.
- **Standalone Compatibility**: Non-Ziro users configure Ghost using standard Zsh idioms (`zstyle` in `.zshrc`) without needing TOML parsers or Ziro CLI.

### 2. Plugin Sovereignty: Pure Zsh Core with Optional Python Cold-Path Enrichment

- **Core Sovereignty**: `ghost.plugin.zsh` is implemented in 100% pure Zsh with optional `fzf` invocation. It MUST execute standalone with zero external Python dependencies:
  ```console
  $ zsh -f -c 'source ghost.plugin.zsh; echo OK'
  ```
- **Optional Python Integration**: Any Python-assisted functionality (e.g. `ziro ghost stats`, offline history indexing, semantic clustering) lives strictly in `core/` as cold-path commands. Ghost operates with full core functionality when Python is unavailable.

### 3. Keybinding Ergonomics: Complementary Roles for Tab and Ctrl-G

- **Separation of Concerns**:
  - `Tab`: Reserved for the completion system (`compsys`), optionally enhanced by `fzf-tab` for argument and file completion menus.
  - `Ctrl-G` (or configured `popup-key`): Dedicated to history candidate browsing via `_ziro_ghost_popup`.
- **Non-Conflicting Coexistence**: `Ctrl-G` operates as a full-buffer history picker that replaces or modifies `BUFFER` upon selection, whereas `Tab` completes tokens at cursor position. Both can be active simultaneously without hook or keymap collisions.

---

## Consequences

- **Spec 009 Alignment**:
  - ZR-004 is clarified to codify the hybrid model: `zstyle` remains authoritative in the plugin, while TOML acts as upstream source in Ziro.
  - ZR-006 and Constitution Principle XIV are strictly preserved: no Python code is required inside `ghost.plugin.zsh`.
  - FR-002 is affirmed as complementary to `fzf-tab`.
- **Implementation Scope for v1.1.0**:
  - `ghost/ghost.zsh` / `ghost.plugin.zsh` will be verified against standalone operation.
  - 4 ZLE widgets will be registered and tested.
  - Zstyle configuration keys documented in Spec 009 are respected.

---

## References

- Constitution Principle XIV (Plugin Sovereignty)
- Spec 009: `009-ziro-ghost-plugin`
- ADR-005: `ADR-005-ziro-defer-directory-placement.md`
