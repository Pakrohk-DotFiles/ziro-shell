#!/usr/bin/env zsh
# ziro-shell — platform detection
# Layer: 0 (shared helper)
# Spec: 008
# AUTO-GENERATED: no
#
# Detects: linux | macos | wsl | termux | unknown
# Idempotent: safe to source multiple times.

typeset -g _ZIRO_PLATFORM_CACHE=""

ziro_platform() {
  # Return cached value if available
  if [[ -n "$_ZIRO_PLATFORM_CACHE" ]]; then
    print "$_ZIRO_PLATFORM_CACHE"
    return 0
  fi

  local platform="unknown"

  if [[ -n "$TERMUX_VERSION" ]] || [[ "$PREFIX" == *com.termux* ]]; then
    platform="termux"
  elif [[ -n "$WSL_DISTRO_NAME" ]] || [[ -n "$WSL_INTEROP" ]]; then
    platform="wsl"
  elif [[ "$OSTYPE" == darwin* ]]; then
    platform="macos"
  elif [[ "$OSTYPE" == linux* ]]; then
    platform="linux"
  fi

  _ZIRO_PLATFORM_CACHE="$platform"
  print "$platform"
}

ziro_is_linux() { [[ "$(ziro_platform)" == "linux" ]] }
ziro_is_macos() { [[ "$(ziro_platform)" == "macos" ]] }
ziro_is_wsl() { [[ "$(ziro_platform)" == "wsl" ]] }
ziro_is_termux() { [[ "$(ziro_platform)" == "termux" ]] }

ziro_is_mobile() {
  [[ "$(ziro_platform)" == "termux" ]]
}
