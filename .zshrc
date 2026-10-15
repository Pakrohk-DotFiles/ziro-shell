#!/usr/bin/env zsh
#
# ziro-shell minimal template
# Customize in ~/.config/ziro/defaults.toml
# Add your own aliases and functions below.
#

: ${ZIRO_HOME:="$HOME/.ziro"}

if [[ -f "$ZIRO_HOME/integration.zsh" ]]; then
  source "$ZIRO_HOME/integration.zsh"
fi

# --- user customizations below ---
