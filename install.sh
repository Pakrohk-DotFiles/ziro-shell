#!/usr/bin/env bash
# Ziro launcher - single source of truth is the Python engine (ziro/).
# Works when: run from file, piped via curl|bash, or from a git checkout.
set -euo pipefail

REPO_URL="https://github.com/Pakrohk-DotFiles/ziro-shell.git"

# --- Locate Python 3 ---
PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && \
       "$candidate" -c 'import sys; sys.exit(0 if sys.version_info[0] >= 3 else 1)' 2>/dev/null; then
        PYTHON="$candidate"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    echo "error: Python 3 is required. Install python3 and retry." >&2
    exit 1
fi

# --- Locate the engine (ziro/) ---
SCRIPT_DIR=""

# 1. When run from a file (not piped), BASH_SOURCE[0] points to the script.
if [ -n "${BASH_SOURCE[0]:-}" ]; then
    SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
fi

# 2. If empty or engine not found, try git rev-parse (user is inside a checkout).
if [ -z "$SCRIPT_DIR" ] || [ ! -d "$SCRIPT_DIR/ziro" ]; then
    if git rev-parse --show-toplevel >/dev/null 2>&1; then
        SCRIPT_DIR="$(git rev-parse --show-toplevel)"
    fi
fi

# 3. Still not found? We were piped outside a checkout. Clone to temp dir.
if [ -z "$SCRIPT_DIR" ] || [ ! -d "$SCRIPT_DIR/ziro" ]; then
    TMPDIR_INSTALL="$(mktemp -d)"
    echo "[*] Cloning Ziro to $TMPDIR_INSTALL ..."
    if ! git clone --depth 1 "$REPO_URL" "$TMPDIR_INSTALL" 2>/dev/null; then
        echo "error: failed to clone $REPO_URL" >&2
        rm -rf "$TMPDIR_INSTALL"
        exit 1
    fi
    exec bash "$TMPDIR_INSTALL/install.sh" "$@"
fi

exec "$PYTHON" "$SCRIPT_DIR/ziro/" "${@:-install}"
