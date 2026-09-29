#!/usr/bin/env zsh
# ziro-shell — prompt: pure
# Layer: T1 (Prompt Backend)
# Spec: 006
# AUTO-GENERATED: no
#
# Pure uses env vars only; no theme system.

typeset -g ZIRO_PROMPT_NAME="pure"
typeset -g ZIRO_PROMPT_THEME_SUPPORTED=false

# Load pure if installed
local _pure_path="${PURE_PATH:-$HOME/pure/pure.zsh}"
if [[ -r "$_pure_path" ]]; then
	if (( $+functions[ziro-defer] )); then
		ziro-defer source "$_pure_path"
	else
		source "$_pure_path"
	fi
else
	print -u2 "ziro: pure not installed at $_pure_path"
fi
