#!/usr/bin/env zsh
# ziro-shell — prompt: starship
# Layer: T1 (Prompt Backend)
# Spec: 006
# AUTO-GENERATED: no
#
# Uses znap eval (cached) to avoid subprocess on every shell.

typeset -g ZIRO_PROMPT_NAME="starship"
typeset -g ZIRO_PROMPT_THEME_SUPPORTED=true
typeset -g ZIRO_PROMPT_THEME_TYPE="toml"
typeset -g ZIRO_PROMPT_THEME_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/starship"

# Apply STARSHIP_CONFIG from ziro theme config if present
if [[ -r "$ZIRO_CONFIG/.theme.conf" ]]; then
	local _theme_file
	_theme_file=$(grep '^prompt_theme_file=' "$ZIRO_CONFIG/.theme.conf" 2>/dev/null | cut -d= -f2-)
	if [[ -n "$_theme_file" && -r "$_theme_file" ]]; then
		export STARSHIP_CONFIG="$_theme_file"
	fi
fi

# Load via znap eval (cached output)
if (( $+functions[znap] )); then
	znap eval starship 'starship init zsh --print-full-init'
else
	# Fallback: eager source if znap not yet loaded
	eval "$(starship init zsh --print-full-init 2>/dev/null)"
fi
