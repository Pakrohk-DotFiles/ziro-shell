#!/usr/bin/env zsh
# ziro-shell — Layer 0 bootstrap integration
# Layer: 0 (Shell Bootstrap)
# Spec: 004
# AUTO-GENERATED: no
#
# Hot-path file. Must stay under the 5ms budget (spec 004 R1).
# Sources znap, ziro-defer, and the generated plugin list.

# Idempotency guard
(( ${+ZIRO_LOADED} )) && return 0

# Resolve paths (XDG-compliant with legacy fallback)
: ${XDG_DATA_HOME:="$HOME/.local/share"}
: ${XDG_CONFIG_HOME:="$HOME/.config"}
: ${XDG_CACHE_HOME:="$HOME/.cache"}
: ${ZIRO_DATA:="$XDG_DATA_HOME/ziro"}
: ${ZIRO_CONFIG:="$XDG_CONFIG_HOME/ziro"}
: ${ZIRO_CACHE:="$XDG_CACHE_HOME/ziro"}
: ${ZIRO_HOME:="$HOME/.ziro"}  # legacy compat (repo root)
export ZIRO_DATA ZIRO_CONFIG ZIRO_CACHE ZIRO_HOME

# Source znap (permanent backend, ADR-002)
if [[ -r "$ZIRO_DATA/vendor/znap/znap.zsh" ]]; then
  source "$ZIRO_DATA/vendor/znap/znap.zsh"
elif [[ -r "$ZIRO_HOME/vendor/znap/znap.zsh" ]]; then
  source "$ZIRO_HOME/vendor/znap/znap.zsh"
fi

# Fallback chain (per Spec 004 R2 + ADR-002):
# 1. Ziro-defer (canonical fork — when available)
# 2. Zsh-defer upstream (current interim)
# 3. Eager stub (safe no-op)
if [[ -r "$ZIRO_HOME/ziro-defer/ziro-defer.plugin.zsh" ]]; then
  source "$ZIRO_HOME/ziro-defer/ziro-defer.plugin.zsh"
elif [[ -r "$ZIRO_DATA/vendor/ziro-defer/ziro-defer.plugin.zsh" ]]; then
  source "$ZIRO_DATA/vendor/ziro-defer/ziro-defer.plugin.zsh"
elif [[ -r "$ZIRO_HOME/vendor/ziro-defer/ziro-defer.plugin.zsh" ]]; then
  source "$ZIRO_HOME/vendor/ziro-defer/ziro-defer.plugin.zsh"
elif [[ -r "$ZIRO_DATA/vendor/ziro-defer/zsh-defer.plugin.zsh" ]]; then
  source "$ZIRO_DATA/vendor/ziro-defer/zsh-defer.plugin.zsh"
elif [[ -r "$ZIRO_HOME/vendor/ziro-defer/zsh-defer.plugin.zsh" ]]; then
  source "$ZIRO_HOME/vendor/ziro-defer/zsh-defer.plugin.zsh"
elif (( $+commands[zsh-defer] )); then
  source "$commands[zsh-defer]"
else
  # Eager fallback: run the command immediately
  ziro-defer() { "$@"; }
fi

# ─── ziro local source: source + .zwc compile for local plugins ───
# Uses `znap compile` when available; falls back to `zcompile`.
_ziro_local_source() {
  emulate -L zsh
  local path=""
  local defer=""
  local target=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --defer) defer="--defer" ;;
      *) path="${1:A}" ;;
    esac
    shift
  done

  # ۱. Resolve target file
  if [[ -d "$path" ]]; then
    local -a patterns=(
      "$path"/*.plugin.zsh(N)
      "$path"/*/*.plugin.zsh(N)
      "$path"/*.zsh(N)
    )
    for f in "${patterns[@]}"; do
      target="$f"
      break
    done
    if [[ -z "$target" ]]; then
      print -u2 "ziro: no plugin file (.plugin.zsh/.zsh) found in $path"
      return 1
    fi
  elif [[ -f "$path" ]]; then
    target="$path"
  else
    print -u2 "ziro: path not found: $path"
    return 1
  fi

  # ۲. Compile with znap if available, else zcompile
  local zwc="${target}.zwc"
  if [[ ! -f "$zwc" || "$target" -nt "$zwc" ]]; then
    if (( $+functions[znap] )); then
      znap compile "$target" 2>/dev/null || zcompile "$target" 2>/dev/null || true
    else
      zcompile "$target" 2>/dev/null || true
    fi
  fi

  # ۳. Source (eager or deferred)
  if [[ "$defer" == "--defer" ]]; then
    if [[ -o interactive ]]; then
      ziro-defer source "$target"
    else
      # In non-interactive shell (scripts, tests, CI), ZLE idle loop is absent;
      # invoke ziro-defer for queueing then source immediately so definitions are active.
      ziro-defer source "$target" 2>/dev/null || true
      source "$target"
    fi
  else
    source "$target"
  fi
}

# ─── ziro-local dispatcher ───
ziro-local() {
  emulate -L zsh
  case "${1:-}" in
    source) shift; _ziro_local_source "$@" ;;
    *) print -u2 "ziro: unknown local subcommand: ${1:-<none>}"; return 2 ;;
  esac
}

# ─── ziro wrapper for local command ───
if ! (( $+functions[ziro] )); then
  ziro() {
    if [[ "$1" == "local" ]]; then
      shift
      ziro-local "$@"
    elif (( $+functions[_ziro_dispatch] )); then
      _ziro_dispatch "$@"
    elif [[ -r "$ZIRO_HOME/ziro.zsh" ]]; then
      source "$ZIRO_HOME/ziro.zsh"
      _ziro_dispatch "$@"
    else
      print -u2 "ziro: unknown command: $1"
      return 1
    fi
  }
fi

# Source the generated plugin list if present
[[ -r "$ZIRO_CONFIG/derived/plugins.gen.zsh" ]] && \
  source "$ZIRO_CONFIG/derived/plugins.gen.zsh"

# Mark bootstrap complete
export ZIRO_LOADED=1
