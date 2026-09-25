#!/usr/bin/env zsh
# ziro-shell — environment detection
# Layer: 0 (shared helper)
# Spec: 008
# AUTO-GENERATED: no
#
# Detects: server | desktop
# Override: export ZSH_ENV_TYPE=server|desktop
# Root user is FORCED to server mode.

typeset -g _ZIRO_ENV_TYPE_CACHE=""

ziro_env_type() {
  if [[ -n "$_ZIRO_ENV_TYPE_CACHE" ]]; then
    print "$_ZIRO_ENV_TYPE_CACHE"
    return 0
  fi

  local env_type="desktop"

  # 1. Explicit override
  if [[ "$ZSH_ENV_TYPE" == "server" || "$ZSH_ENV_TYPE" == "desktop" ]]; then
    env_type="$ZSH_ENV_TYPE"
  # 2. Root is always server
  elif (( EUID == 0 )); then
    env_type="server"
  # 3. SSH session without display → server
  elif [[ -n "$SSH_CONNECTION" ]] && [[ -z "$DISPLAY" ]] && [[ -z "$WAYLAND_DISPLAY" ]]; then
    env_type="server"
  # 4. No display server at all → server
  elif [[ -z "$DISPLAY" ]] && [[ -z "$WAYLAND_DISPLAY" ]] && [[ "$OSTYPE" != darwin* ]]; then
    env_type="server"
  fi

  _ZIRO_ENV_TYPE_CACHE="$env_type"
  print "$env_type"
}

ziro_is_server() { [[ "$(ziro_env_type)" == "server" ]] }
ziro_is_desktop() { [[ "$(ziro_env_type)" == "desktop" ]] }
