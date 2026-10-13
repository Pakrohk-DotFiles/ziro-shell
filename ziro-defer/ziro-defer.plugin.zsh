#!/usr/bin/env zsh
# ════════════════════════════════════════════════════════════════
# ziro-defer — progressive fork of zsh-defer
# Version: 0.1.0 (MVP)
# Spec: 005 (znap Optimization + ziro-defer)
# ADR:  ADR-004 (fork timing)
# ════════════════════════════════════════════════════════════════
#
# Location rationale:
#   ziro-defer is a FORK of third-party code (romkatv/zsh-defer).
#   It does NOT belong in vendor/ (that's pristine third-party).
#   It does NOT belong in ghost/ (that's ziro-original code).
#   It lives in ziro-defer/ as a first-class fork directory.
#
#   In v1.1.0, this directory becomes the Pakrohk-DotFiles/ziro-defer
#   repository on GitHub, installable via:
#     znap source Pakrohk-DotFiles/ziro-defer
#
# Roadmap:
#   v0.1.0 (now)   : MVP wrapper — --wait=N → -t N
#   v0.2.0 (v1.1)  : --slot=a|b|c sub-slot priority
#   v0.3.0 (v1.1)  : --lazy-by-command, --lazy-by-function
#   v0.4.0 (v1.2)  : --atinit, --atload, auto re-registration
#   v1.0.0 (future): full spec 005 feature set
#
# License: MIT (our wrapper) + MIT (upstream, see LICENSE files)
# ════════════════════════════════════════════════════════════════

typeset -g ZIRO_DEFER_VERSION="0.1.0"
typeset -g ZIRO_DEFER_DIR="${0:A:h}"

# ─── Source upstream engine (vendored inside this dir) ───
if [[ -r "${ZIRO_DEFER_DIR}/upstream/zsh-defer.plugin.zsh" ]]; then
  source "${ZIRO_DEFER_DIR}/upstream/zsh-defer.plugin.zsh"
else
  print -u2 "ziro-defer: upstream/zsh-defer.plugin.zsh not found"
  return 1
fi

# ─── ziro-defer API (fork-style wrapper) ───
# Translates fork-style args to upstream where possible;
# silently ignores fork-only args (documented with TODO).
ziro-defer() {
  emulate -L zsh
  local -a args=()
  local arg

  for arg in "$@"; do
    case "$arg" in
      # v0.1.0 — delay translation
      --wait=*)
        args+=("-t" "${arg#--wait=}")
        ;;

      # ─── v0.2.0: sub-slot priority ───
      # TODO(v0.2.0): implement slot-based ordering queue
      --slot=*)
        : # accepted but ignored in v0.1.0
        ;;

      # ─── v0.3.0: lazy-by-command/function ───
      # TODO(v0.3.0): map to trigger-load mechanism
      --lazy-by-command=*|--lazy-by-function=*)
        : # accepted but ignored in v0.1.0
        ;;

      # ─── v0.4.0: init/load hooks ───
      # TODO(v0.4.0): wrap command execution with hooks
      --atinit=*|--atload=*)
        : # accepted but ignored in v0.1.0
        ;;

      # Pass-through: upstream args + command
      *)
        args+=("$arg")
        ;;
    esac
  done

  zsh-defer "${args[@]}"
}

# ─── Compatibility alias ───
ziro_defer() {
  ziro-defer "$@"
}

# ════════════════════════════════════════════════════════════════
# End of ziro-defer.plugin.zsh v0.1.0
# Next: v0.2.0 — implement --slot=a|b|c
# ════════════════════════════════════════════════════════════════
