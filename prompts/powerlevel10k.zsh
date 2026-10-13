#!/usr/bin/env zsh
# ziro-shell — prompt: powerlevel10k
# Layer: T1 (Prompt Backend)
# Spec: 006
# AUTO-GENERATED: no
#
# p10k theme is wizard-driven; ziro redirects to `p10k configure`.

typeset -g ZIRO_PROMPT_NAME="powerlevel10k"
typeset -g ZIRO_PROMPT_THEME_SUPPORTED=true
typeset -g ZIRO_PROMPT_THEME_TYPE="zsh"
typeset -g ZIRO_PROMPT_THEME_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/p10k"

# Load p10k if installed
local _p10k_path="${P10K_PATH:-$HOME/powerlevel10k/powerlevel10k.zsh-theme}"
if [[ -r "$_p10k_path" ]]; then
	# Use ziro-defer if available (never block startup)
	if (( $+functions[ziro-defer] )); then
		ziro-defer source "$_p10k_path"
	else
		source "$_p10k_path"
	fi
else
	print -u2 "ziro: powerlevel10k not installed at $_p10k_path"
	print -u2 "ziro: run: git clone --depth=1 https://github.com/romkatv/powerlevel10k \$HOME/powerlevel10k"
fi
