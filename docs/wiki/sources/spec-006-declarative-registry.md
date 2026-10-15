# Spec 006: Declarative Tools Registry & Generator Architecture

**Status**: Active  
**Version**: 0.2.0 (Declarative Architecture)  
**Date**: 2026-10-15  
**Parent Architecture**: Layer 0 CLI / Layer 3 Runtime  
**Target Version**: `v1.1.0`  

---

## 1. Executive Summary

Ziro Shell uses a declarative tool registry (`core/tools_factory.toml`) as the single source of truth for all tools, plugins, and CLI integrations.

Prior to v1.1.0, generation logic in `core/generator.py` relied on imperative branching (`if prompt == 'starship'`, etc.) and a hardcoded load-order list. With Spec 006 v0.2.0, all tool metadata, load mechanisms, timing, and safety guards are declared in TOML. The Python generator is strictly a generic reader and emitter with zero tool-specific branching.

---

## 2. Declarative Schema

Each tool in `core/tools_factory.toml` defines what the tool is, how it is loaded, when it executes, and how it is guarded.

### Required Fields

| Field | Type | Description |
|---|---|---|
| `name` | `string` | Unique kebab-case tool identifier (e.g. `fast-syntax-highlighting`) |
| `type` | `enum` | Tool classification: `plugin`, `binary`, `builtin`, `bootstrap` |
| `category` | `enum` | Functional component slot: `prompt`, `auto_suggest`, `syntax_highlighting`, `completions`, `colors`, `navigation`, `fuzzy_finder`, `core`, `infra` |
| `load_method` | `enum` | Invocation pattern: `binary-eval`, `clone-eval`, `clone-source`, `local-source`, `builtin-load`, `bootstrap-source` |
| `load_timing` | `enum` | Execution lifecycle: `eager`, `defer`, `eval`, `prompt` |
| `load_order` | `integer` | Numerical sequence of emission in `plugins.gen.zsh` |
| `guard` | `enum` | Safety guard before shell execution: `none`, `binary-check` |

### Conditional Fields

- `source`: GitHub repository (`user/repo`) or script path for cloned/bootstrap components.
- `subpath`: Subdirectory within repository (e.g. `plugins/git` for Oh My Zsh).
- `binary_name`: Executable name checked via `(( $+commands[name] ))` when `guard = "binary-check"`.
- `init_command`: Shell command string evaluated for `binary-eval`.
- `eval_command`: In-repo command executed for `clone-eval`.
- `local_path`: Local file path (supports `$ZIRO_HOME` interpolation).
- `cache_key`: Identifier for Znap eval cache.
- `alternatives_only`: If `true`, tool is omitted from default generation unless explicitly selected.
- `conflicts_with`: List of mutually exclusive tools.
- `github`: Canonical upstream project URL.
- `description`: Human-readable summary.

---

## 3. Tool Loading Patterns

The generator maps `load_method`, `load_timing`, and `guard` to shell constructs deterministically:

1. **`binary-eval`** (External compiled CLI):
   ```zsh
   (( $+commands[starship] )) && znap eval starship 'starship init zsh --print-full-init'
   ```
2. **`clone-eval`** (Repo-scoped script cached via Znap):
   ```zsh
   znap eval marlonrichert/zcolors "./zcolors ${(q)LS_COLORS}"
   ```
3. **`clone-source`** (Git repository plugin):
   ```zsh
   znap source zsh-users/zsh-completions
   # or with deferral:
   ziro-defer znap source zdharma-continuum/fast-syntax-highlighting
   ```
4. **`local-source`** (Built-in Ziro plugin):
   ```zsh
   ziro-defer source $ZIRO_HOME/ghost/ghost.zsh
   ```

---

## 4. FR-011: Declarative Purity

The generator (`core/generator.py`) complies with the following strict invariants:
- **Zero Tool Hardcoding**: Zero `if name == ...` branches in Python source.
- **Dynamic Load Order**: Numerical order is derived from `load_order` in TOML, eliminating hardcoded order arrays.
- **Behavior Preservation**: Output in `plugins.gen.zsh` remains 100% byte-compatible with previous releases.
- **Failure Resilience**: External binaries are wrapped in `(( $+commands[...] ))` guards so missing binaries never emit shell errors.

---

## 5. Developer Guide: Adding a Tool (v0.2.0+)

Adding or updating a tool is a declarative, zero-Python task:

1. Add a `[[tool]]` table to `core/tools_factory.toml`:
   ```toml
   [[tool]]
   name = "my-plugin"
   type = "plugin"
   category = "core"
   load_method = "clone-source"
   load_timing = "defer"
   load_order = 15
   guard = "none"
   source = "username/my-plugin"
   github = "https://github.com/username/my-plugin"
   description = "My awesome plugin."
   ```
2. If configurable by the user, register it under `defaults.toml`.
3. Run `ziro plugin update` or `python3 -m core install --default`.
4. The tool is automatically discovered, validated, ordered, and emitted.
