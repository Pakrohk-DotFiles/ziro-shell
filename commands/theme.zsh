#!/usr/bin/env zsh
# ziro-shell — theme command
# Layer: 0 (CLI)
# Spec: 006 R4
# AUTO-GENERATED: no

_ziro_cmd_theme() {
  emulate -L zsh
  : ${ZIRO_HOME:="$HOME/.ziro"}
  : ${ZIRO_CONFIG:="${XDG_CONFIG_HOME:-$HOME/.config}/ziro"}

  # Check Python availability
  if ! command -v python3 &>/dev/null; then
    print -u2 "ziro: python3 not found"
    return 1
  fi

  # Delegate to Python CLI (must run from $ZIRO_HOME for import to work)
  (cd "$ZIRO_HOME" && ZIRO_HOME="$ZIRO_HOME" ZIRO_CONFIG="$ZIRO_CONFIG" \
    python3 -m core theme "$@")
}
