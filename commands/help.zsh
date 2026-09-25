#!/usr/bin/env zsh
# ziro-shell — help command
# Layer: 0 (CLI)
# Spec: 008
# AUTO-GENERATED: no

_ziro_cmd_help() {
  local notice="${1:-}"

  (( ${+notice} )) && [[ -n "$notice" ]] && print -u2 "ziro: $notice"

  << 'HELP'
ziro — fast, layered Zsh runtime customization

Usage:
  ziro <command> [args...]

Commands:
  install    Install ziro with defaults or custom profile
  plugin     Manage plugins (add, remove, list, show)
  tag        Manage plugin tags (add, remove, list)
  suggest    Manage auto-suggest component
  theme      Manage themes
  prompt     Manage prompt
  config     Manage configuration
  doctor     Diagnose installation
  bench      Benchmark performance
  help       Show this help

For more: https://github.com/Pakrohk-DotFiles/ziro-shell
HELP
}
