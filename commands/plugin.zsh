#!/usr/bin/env zsh
# ziro-shell — plugin command
# Layer: 0 (CLI)
# Spec: 001 FR-001
# AUTO-GENERATED: no

_ziro_cmd_plugin() {
  emulate -L zsh
  : ${ZIRO_HOME:="$HOME/.ziro"}
  : ${ZIRO_CONFIG:="${XDG_CONFIG_HOME:-$HOME/.config}/ziro"}

  if [[ "$1" == "list" && $# -eq 1 ]]; then
    local pdir="$ZIRO_HOME/plugins"
    if [[ ! -d "$pdir" ]]; then
      print "(no plugins installed)"
      return 0
    fi
    local -a dirs
    dirs=("$pdir"/*(N/))
    if [[ ${#dirs} -eq 0 ]]; then
      print "(no plugins installed)"
      return 0
    fi
    for d in "${dirs[@]}"; do
      print "${d:t}"
    done
    return 0
  fi

  if ! command -v python3 &>/dev/null; then
    print -u2 "ziro: python3 not found"
    return 1
  fi

  (cd "$ZIRO_HOME" && ZIRO_HOME="$ZIRO_HOME" ZIRO_CONFIG="$ZIRO_CONFIG" \
    python3 -m core plugin "$@")
}
