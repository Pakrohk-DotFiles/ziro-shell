#!/usr/bin/env zsh
# ziro-shell — Layer 0 bootstrap integration
# Layer: 0 (Shell Bootstrap)
# Spec: 004
# AUTO-GENERATED: no
#
# Hot-path file. Must stay under the 5ms budget (spec 004 R1).
# Sources znap, ziro-defer, and the generated plugin list.

# Idempotency guard
(( ${+ZIRO_LOADED} )) && return 0

# Resolve paths (cached, XDG-aware)
: ${ZIRO_HOME:="$HOME/.ziro"}
: ${ZIRO_CONFIG:="${XDG_CONFIG_HOME:-$HOME/.config}/ziro"}
: ${ZIRO_CACHE:="${XDG_CACHE_HOME:-$HOME/.cache}/ziro"}
export ZIRO_HOME ZIRO_CONFIG ZIRO_CACHE

# Source znap (permanent backend, ADR-002)
if [[ -r "$ZIRO_HOME/vendor/znap/znap.zsh" ]]; then
  source "$ZIRO_HOME/vendor/znap/znap.zsh"
fi

# Fallback chain (per Spec 004 R2 + ADR-002):
# 1. Ziro-defer (canonical fork — when available)
# 2. Zsh-defer upstream (current interim)
# 3. Eager stub (safe no-op)
if [[ -r "$ZIRO_HOME/vendor/ziro-defer/ziro-defer.plugin.zsh" ]]; then
  source "$ZIRO_HOME/vendor/ziro-defer/ziro-defer.plugin.zsh"
elif [[ -r "$ZIRO_HOME/vendor/ziro-defer/zsh-defer.plugin.zsh" ]]; then
  source "$ZIRO_HOME/vendor/ziro-defer/zsh-defer.plugin.zsh"
elif (( $+commands[zsh-defer] )); then
  source "$commands[zsh-defer]"
else
  # Eager fallback: run the command immediately
  ziro-defer() { "$@"; }
fi

# Source the generated plugin list if present
[[ -r "$ZIRO_CONFIG/derived/plugins.gen.zsh" ]] && \
  source "$ZIRO_CONFIG/derived/plugins.gen.zsh"

# Mark bootstrap complete
export ZIRO_LOADED=1
