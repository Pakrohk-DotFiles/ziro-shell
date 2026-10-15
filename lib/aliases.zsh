#!/usr/bin/env zsh
# ziro-shell — Modern CLI tool aliases (Auto-Detect)
# Layer: 0 (Shell Aliases) · Spec: 006 v0.2.1
# Loaded via ziro-defer: hot-path cost is 0ms.
# Only defines aliases when modern CLI binaries exist in PATH.

# ─── ls → eza ───
if (( $+commands[eza] )); then
  alias ls='eza --icons --group-directories-first'
  alias ll='eza -la --icons --group-directories-first'
  alias la='eza -a --icons --group-directories-first'
  alias lt='eza --tree --level=2 --icons'
fi

# ─── cat → bat ───
if (( $+commands[bat] )); then
  alias cat='bat --style=plain'
fi

# ─── grep → ripgrep (rg) ───
if (( $+commands[rg] )); then
  alias grep='rg'
fi

# ─── find → fd ───
if (( $+commands[fd] )); then
  alias find='fd'
fi

# ─── diff → delta ───
if (( $+commands[delta] )); then
  alias diff='delta'
fi
