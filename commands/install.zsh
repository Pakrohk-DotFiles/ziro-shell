#!/usr/bin/env zsh
# ziro-shell — install command
# Layer: 0 (CLI)
# Spec: 006 R1
# AUTO-GENERATED: no

_ziro_cmd_install() {
  emulate -L zsh
  : ${ZIRO_HOME:="$HOME/.ziro"}
  : ${ZIRO_CONFIG:="${XDG_CONFIG_HOME:-$HOME/.config}/ziro"}

  local venv_py="${XDG_DATA_HOME:-$HOME/.local/share}/ziro/venv/bin/python3"
  local py="python3"
  [[ -x "$venv_py" ]] && py="$venv_py"

  if ! command -v "$py" &>/dev/null && ! command -v python3 &>/dev/null; then
    print -u2 "ziro: python3 not found"
    return 1
  fi

  local ret=0
  if [[ -t 0 && -r /dev/tty ]]; then
    (cd "$ZIRO_HOME" && ZIRO_HOME="$ZIRO_HOME" ZIRO_CONFIG="$ZIRO_CONFIG" \
      "$py" -m core install "$@" < /dev/tty)
    ret=$?
  else
    (cd "$ZIRO_HOME" && ZIRO_HOME="$ZIRO_HOME" ZIRO_CONFIG="$ZIRO_CONFIG" \
      "$py" -m core install "$@")
    ret=$?
  fi

  local comp_dir="${XDG_DATA_HOME:-$HOME/.local/share}/ziro/completions"
  if [[ -d "$comp_dir" && ! ${fpath[(Ie)$comp_dir]} ]]; then
    fpath=("$comp_dir" $fpath)
  fi

  return $ret
}
