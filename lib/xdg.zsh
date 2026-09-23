#!/usr/bin/env zsh
# ziro-shell — XDG path helpers
# Layer: 0 (shared helper)
# Spec: 008
# AUTO-GENERATED: no
#
# Single source of truth for canonical paths (Constitution IV).

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
