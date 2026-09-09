#!/usr/bin/env bash
# Ziro launcher - single source of truth is the Python engine (ziro/).
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1 && \
     python -c 'import sys; sys.exit(0 if sys.version_info[0] >= 3 else 1)' 2>/dev/null; then
    PYTHON=python
else
    echo "error: Python 3 is required. Install python3 and retry." >&2
    exit 1
fi
exec "$PYTHON" "$SCRIPT_DIR/ziro/" "$@"
