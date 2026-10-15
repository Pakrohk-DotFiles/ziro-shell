# Spec 010: pf — Cross-Shell Package Manager Helper

**Status**: Draft (Approved for Design)  
**Date**: 2026-10-15  
**Spec ID**: 010  
**Parent Spec**: `000-architecture` (Layer 3 Plugin)  
**Target Version**: `v1.1.5` (Phase 9)  
**Repository**: `https://github.com/Pakrohk-DotFiles/ziro-pf`  
**Relates to**: Constitution Principle XIV (Plugin Sovereignty), ADR-008, ADR-009 (Candidate)  

---

## 1. Purpose & Overview

The `pf` (Package-Fzf) component is a unified, cross-shell command-line wrapper and interactive menu designed to streamline daily package management tasks across heterogeneous Unix environments. 

Rather than requiring developers to memorize divergent CLI flags across Arch Linux (`pacman`/`paru`), macOS (`brew`), Debian/Ubuntu (`apt`), Fedora/RHEL (`dnf`), Alpine Linux (`apk`), or openSUSE (`zypper`), `pf` provides a cohesive, single-interface developer experience.

### Dual-Mode Operation
- **Interactive TUI Mode (`pf` with no arguments)**:
  Launches an instant, keyboard-driven `fzf` selection menu displaying all available actions (search, install, remove, list orphans, inspect package info, and system update). Ideal for interactive terminal sessions.
- **Direct CLI / Scripting Mode (`pf <subcommand> [args...]`)**:
  Bypasses interactive prompts and executes commands directly (e.g. `pf install ripgrep fd-find` or `pf search neovim`). Enables deterministic scripting, composability in shell functions, and pipeline automation.

---

## 2. Why Standalone (Constitution Principle XIV Compliance)

In accordance with **Constitution Principle XIV (Plugin Sovereignty)**:
- **Zero Runtime Couplings**: `pf` MUST NOT assume the existence, installation, or configuration of Ziro Shell (`~/.ziro/`) or Python. It is an independent utility that functions equally well in vanilla shells, Oh My Zsh, Prezto, or bare server deployments.
- **Autonomous Repository**: Development, issue tracking, versioning, and distribution occur in an isolated GitHub repository: `Pakrohk-DotFiles/ziro-pf`.
- **Ecosystem Integration**: When installed inside the Ziro Shell ecosystem, Ziro's Layer 0 (`integration.zsh`) and znap runtime clone and load `pf` as a standard sovereign plugin into `~/.local/share/ziro/plugins/ziro-pf/`.

---

## 3. Cross-Shell Architecture

To achieve universal compatibility across developer environments, `pf` uses a layered shell architecture:

1. **POSIX sh Core Engine (`bin/pf`)**:
   - Written in 100% strict POSIX-compliant shell syntax (`#!/bin/sh` or `#!/usr/bin/env sh`).
   - Contains backend detection, argument parsing, caching logic, and `fzf` execution pipelines.
   - Completely free of bash-isms, zsh-isms, or local environment assumptions.
   - Directly executable from `PATH` by **Bash, Zsh, Dash, Ash, and Fish**.
2. **Optional Zsh Plugin Wrapper (`pf.plugin.zsh`)**:
   - Provides native Zsh ergonomics when loaded via znap, Ziro, or Oh My Zsh.
   - Adds `bin/` to `PATH` dynamically upon source.
   - Registers shell completions and optional interactive ZLE keybindings (e.g. `Ctrl-P` for package search).
3. **Completion Script (`completions/_pf`)**:
   - Standard `#compdef pf` script providing context-aware completion for subcommands, flags, and cached package names in Zsh.

---

## 4. Command Surface

The command syntax is modeled after standard POSIX CLI conventions:

| Command | Arguments | Description |
|---|---|---|
| `pf` | *(none)* | Launch interactive `fzf` action menu. |
| `pf install` | `[pkg...]` | Install specified package(s), or open interactive search if no package is given. |
| `pf remove` | `[pkg...]` | Remove specified package(s), or open interactive list of installed packages. |
| `pf search` | `<query>` | Query repositories using native backend with cached results. |
| `pf info` | `<pkg>` | Display package metadata, dependencies, and file lists. |
| `pf orphans` | `[--remove]` | List orphaned packages (unused dependencies); `--remove` cleans them up. |
| `pf update` | *(none)* | Synchronize repository databases and update installed packages. |
| `pf list` | `[--explicit\|--foreign]` | List installed packages (filtering by explicit install or AUR/external). |
| `pf backend` | *(none)* | Display detected package manager and configuration paths. |
| `pf help` | `[subcommand]` | Show help text and flag descriptions. |

---

## 5. Backend Matrix & Detection Hierarchy

### Auto-Detection Hierarchy
When initializing, `pf` evaluates available binaries in `PATH` in strict priority order:
```text
paru → pacman → brew → apt-get → dnf → apk → zypper
```
*Note: Arch Linux prioritizes `paru` over native `pacman` to seamlessly handle both official repositories and the Arch User Repository (AUR).*

### Backend Mapping Matrix

| Backend | Platform | Search Command | Install Command | Remove Command | Orphans Command | Update Command |
|---|---|---|---|---|---|---|
| **paru** | Arch Linux / Manjaro | `paru -Slq` | `paru -S` | `paru -Rns` | `paru -Qdtq` | `paru -Syu` |
| **pacman** | Arch Linux | `pacman -Slq` | `sudo pacman -S` | `sudo pacman -Rns` | `pacman -Qdtq` | `sudo pacman -Syu` |
| **brew** | macOS / Linuxbrew | `brew formulae` | `brew install` | `brew uninstall` | `brew autoremove` | `brew upgrade` |
| **apt** | Debian / Ubuntu / Mint | `apt-cache pkgnames` | `sudo apt install` | `sudo apt purge` | `sudo apt autoremove` | `sudo apt update && sudo apt upgrade` |
| **dnf** | Fedora / RHEL / Alma | `dnf list available` | `sudo dnf install` | `sudo dnf remove` | `sudo dnf autoremove` | `sudo dnf upgrade` |
| **apk** | Alpine Linux / Containers | `apk list` | `sudo apk add` | `sudo apk del` | `apk info -e` | `sudo apk update && sudo apk upgrade` |
| **zypper** | openSUSE / SLES | `zypper search` | `sudo zypper install` | `sudo zypper remove` | `zypper packages --orphaned` | `sudo zypper update` |

### Sudo Elevation Strategy
- Commands requiring administrative privileges dynamically prefix `sudo` only when executing as non-root (`[ "$(id -u)" -ne 0 ]`).
- In environments where `sudo` is absent (e.g. minimalist Alpine Docker containers), `pf` falls back to `doas` or executes directly if running as `root`.

---

## 6. File Structure & Repository Layout

The standalone repository `Pakrohk-DotFiles/ziro-pf` will adhere to the following directory layout:

```text
ziro-pf/
├── bin/
│   └── pf                     # POSIX sh executable entry point
├── lib/
│   ├── detect.sh              # Backend detection and sudo resolution
│   ├── cache.sh               # Cache read, write, and invalidation helpers
│   ├── fzf.sh                 # Standardized fzf preview and UI configurations
│   └── backends/
│       ├── paru.sh            # Paru / AUR implementation
│       ├── pacman.sh          # Pacman implementation
│       ├── brew.sh            # Homebrew implementation
│       ├── apt.sh             # APT implementation
│       ├── dnf.sh             # DNF implementation
│       ├── apk.sh             # APK implementation
│       └── zypper.sh          # Zypper implementation
├── completions/
│   └── _pf                    # Zsh tab completion definition
├── pf.plugin.zsh              # Zsh plugin entry point (exports PATH & functions)
├── tests/
│   ├── test_detect.sh         # Mocked detection tests
│   └── test_cli.sh            # Command syntax and exit code tests
├── LICENSE                    # MIT License
└── README.md                  # Public documentation & installation guide
```

---

## 7. Caching Strategy & Performance

Real-time querying of package repositories over slow network links or massive package databases (such as Debian or Fedora) causes noticeable latency in interactive `fzf` pickers. `pf` implements an isolated, filesystem-based caching layer:

### Cache Locations (XDG Compliant)
- Base directory: `${XDG_CACHE_HOME:-$HOME/.cache}/pf` (falls back to `~/.cache/ziro/pf` inside Ziro Shell).
- Repository package list: `<cache_dir>/<backend>-list.txt`.
- Package metadata: `<cache_dir>/info/<backend>/<package>.txt`.

### Cache Lifecycle & TTL
1. **Time-To-Live (TTL)**: Default TTL is **3600 seconds (1 hour)**. If the cache file exists and its modification time is within 1 hour, `pf` reads from the local file instantly (< 10ms) without invoking the slow backend package manager.
2. **Forced Refresh**: Passing `--refresh` or `-r` forces a cache rebuild.
3. **Automatic Invalidation**: Successful execution of `pf install`, `pf remove`, or `pf update` automatically purges or marks the list cache stale.

---

## 8. Code Style Compliance (ADR-009 Candidate)

All code authored for `ziro-pf` in Phase 9 must comply with the principles established in **ADR-009 (Candidate: Function-Based, Idiom-First)**:

### 1. POSIX sh Core (`bin/pf` & `lib/*.sh`)
- Rely strictly on POSIX parameter expansions (`${var:-default}`, `${var#prefix}`, `${var%suffix}`).
- Avoid non-standard extensions (no `declare`, `typeset -A`, `[[ ]]`, or process substitution `<(...)`).
- Write function-based pipelines with early returns (`[ -f "$file" ] || return 0`).
- Ensure no subshells are spawned inside iteration loops.

### 2. Zsh Layer (`pf.plugin.zsh`)
- Use associative array dispatch tables (`typeset -A _pf_handlers`) for command routing rather than sprawling `if/elif` blocks.
- Leverage Zsh array expansion flags and glob qualifiers `*(.)` when resolving local helper scripts.
- Maintain idempotency: sourcing `pf.plugin.zsh` multiple times must have zero unintended side-effects.

---

## 9. Acceptance Criteria (for Phase 9 Milestone)

Implementation in Phase 9 (`v1.1.5`) must satisfy the following verifiable criteria:

1. **Performance Budget**:
   - `pf` with no arguments launches the interactive `fzf` menu in **≤ 100ms** on warmed cache.
   - `pf backend` executes in **< 10ms**.
2. **Platform Verification**:
   - Successfully detects and installs packages on Arch Linux (paru/pacman), Ubuntu (apt), Fedora (dnf), Alpine (apk), and macOS (brew).
3. **Cross-Shell Portability**:
   - `sh -c 'pf backend'` outputs the correct manager.
   - `bash -c 'pf backend'` outputs the correct manager.
   - `zsh -f -c 'source pf.plugin.zsh; pf backend'` outputs the correct manager.
4. **Standalone Verification**:
   - Zero occurrences of `~/.ziro` or `ZIRO_*` variables in `bin/pf` or `lib/*.sh`.
   - Utility operates 100% correctly when cloned to a system with zero Ziro Shell files present.
5. **Completion Quality**:
   - `pf <TAB>` suggests all valid subcommands.
   - `pf remove <TAB>` suggests currently installed packages.

---

## 10. Dependencies & Environmental Requirements

### Mandatory Runtime Dependencies
- **`fzf`** (version >= 0.29.0): Required for all interactive selection dialogs and fuzzy searching.
- **Native Package Manager**: At least one supported package manager (`paru`, `pacman`, `brew`, `apt-get`, `dnf`, `apk`, `zypper`) available in `$PATH`.

### Optional Dependencies
- **`zsh`** (version >= 5.8): Required only if using `pf.plugin.zsh` wrapper or Zsh completion.

### Explicitly Excluded Dependencies
- **No Python Runtime**: `pf` does not require Python or Python virtual environments.
- **No Heavyweight TUI Libraries**: Relies exclusively on `fzf` and native terminal escape sequences.

---

## 11. Out of Scope

The following items are explicitly out of scope for Phase 9:
- Direct graphical user interfaces (GUI) or custom non-fzf ncurses/bubbletea TUIs.
- Automatic installation or bootstrapping of package managers themselves (e.g. installing Homebrew if absent).
- Unofficial or esoteric package managers (e.g. `nix-env`, `guix`, `snap`, `flatpak`).
- Native Windows support without WSL (Ziro Shell and `pf` strictly target Unix/POSIX environments).
