#!/usr/bin/env zsh
# ziro-shell — logging utilities
# Layer: 0 (shared helper)
# Spec: 008
# AUTO-GENERATED: no

typeset -g _ZIRO_LOG_LEVEL="${ZIRO_LOG_LEVEL:-warn}"

ziro_log() {
  emulate -L zsh
  local level="${1:-info}"
  shift
  local msg="$*"

  local -A priority=(debug 0 info 1 warn 2 error 3)

  (( ${priority[$level]:-1} < ${priority[$_ZIRO_LOG_LEVEL]:-2} )) && return 0

  : ${ZIRO_CACHE:="${XDG_CACHE_HOME:-$HOME/.cache}/ziro"}
  local logfile="${ZIRO_CACHE}/logs/ziro.log"
  mkdir -p "${logfile:h}"

  printf '[%s] [%s] %s\n' "$(date -Iseconds)" "$level" "$msg" >> "$logfile"

  case "$level" in
    error) print -u2 "❌ $msg" ;;
    warn)  print -u2 "⚠️  $msg" ;;
  esac
}
