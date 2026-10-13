#!/usr/bin/env zsh
# ziro-shell — terminal capability detection
# Layer: 0 (shared helper)
# Spec: 008
# AUTO-GENERATED: no
#
# Detects: Nerd Font availability, truecolor support.

typeset -g _ZIRO_NERD_FONT_CACHE=""
typeset -g _ZIRO_TRUECOLOR_CACHE=""

ziro_has_nerd_font() {
  if [[ -n "$_ZIRO_NERD_FONT_CACHE" ]]; then
    [[ "$_ZIRO_NERD_FONT_CACHE" == "yes" ]]
    return $?
  fi

  local has_font="no"

  # 1. Explicit opt-in
  if [[ "$NERD_FONT" == "1" || "$NERD_FONT" == "yes" ]]; then
    has_font="yes"
  # 2. Check font list
  elif command -v fc-list &>/dev/null; then
    if fc-list 2>/dev/null | grep -qi 'nerd font'; then
      has_font="yes"
    fi
  # 3. macOS font directories
  elif [[ "$OSTYPE" == darwin* ]]; then
    if ls ~/Library/Fonts 2>/dev/null | grep -qi 'nerd'; then
      has_font="yes"
    fi
  fi

  _ZIRO_NERD_FONT_CACHE="$has_font"
  [[ "$has_font" == "yes" ]]
}

ziro_has_truecolor() {
  if [[ -n "$_ZIRO_TRUECOLOR_CACHE" ]]; then
    [[ "$_ZIRO_TRUECOLOR_CACHE" == "yes" ]]
    return $?
  fi

  local has_tc="no"

  if [[ "$COLORTERM" == "truecolor" || "$COLORTERM" == "24bit" ]]; then
    has_tc="yes"
  elif [[ "$TERM" == *256color* ]]; then
    # 256color is not truecolor, but supports rich colors
    has_tc="no"
  fi

  _ZIRO_TRUECOLOR_CACHE="$has_tc"
  [[ "$has_tc" == "yes" ]]
}

ziro_color_count() {
  if ziro_has_truecolor; then
    print "16777216"
  elif [[ "$TERM" == *256color* ]]; then
    print "256"
  else
    print "16"
  fi
}

ziro_can_use_nerd_font_icons() {
  ziro_has_nerd_font && [[ "$(ziro_env_type)" == "desktop" ]]
}
