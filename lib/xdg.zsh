#!/usr/bin/env zsh
# ziro-shell — XDG path helpers
# Layer: 0 (shared helper)
# Spec: 008
# AUTO-GENERATED: no
#
# Single source of truth for canonical paths (Constitution IV).
# Fallback-aware: respects XDG_* env vars, falls back to HOME.
# Idempotent: safe to source multiple times.

ziro_xdg_cache() {
  print "${XDG_CACHE_HOME:-$HOME/.cache}/ziro"
}

ziro_xdg_config() {
  print "${XDG_CONFIG_HOME:-$HOME/.config}/ziro"
}

ziro_xdg_data() {
  print "${XDG_DATA_HOME:-$HOME/.local/share}/ziro"
}

ziro_xdg_home() {
  print "${ZIRO_HOME:-$HOME/.ziro}"
}

# --- ensure helpers (cold-path only; make dir if missing) ---

ziro_xdg_ensure_cache() {
  local dir
  dir="$(ziro_xdg_cache)"
  [[ -d "$dir" ]] || mkdir -p "$dir"
  print "$dir"
}

ziro_xdg_ensure_config() {
  local dir
  dir="$(ziro_xdg_config)"
  [[ -d "$dir" ]] || mkdir -p "$dir"
  print "$dir"
}

ziro_xdg_ensure_data() {
  local dir
  dir="$(ziro_xdg_data)"
  [[ -d "$dir" ]] || mkdir -p "$dir"
  print "$dir"
}
