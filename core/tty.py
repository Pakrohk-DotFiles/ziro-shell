"""ziro-shell — TTY detection and passthrough helpers.

Layer: 3 (Python core)
Spec: 008 R6, R7
"""

from __future__ import annotations

import os
import sys
from typing import TextIO


def is_tty(stream: TextIO | None = None) -> bool:
    """Check if stream (default sys.stdout) is an interactive TTY.

    Respects CI and NO_COLOR environment variables.
    """
    target = stream if stream is not None else sys.stdout
    if not hasattr(target, "isatty"):
        return False
    try:
        if not target.isatty():
            return False
    except (ValueError, OSError):
        return False

    # Disable rich / interactive decorations in CI or when NO_COLOR is set
    if os.environ.get("CI") in ("1", "true", "True"):
        return False
    if os.environ.get("NO_COLOR"):
        return False

    return True


def ensure_tty_output() -> bool:
    """Redirect stdout to /dev/tty if stdout is not currently a TTY.

    Returns True if stdout is a TTY (originally or redirected), False otherwise.
    Safe and non-fatal when /dev/tty cannot be opened.
    """
    if is_tty(sys.stdout):
        return True

    try:
        if os.path.exists("/dev/tty") and os.access("/dev/tty", os.W_OK):
            tty_out = open("/dev/tty", "w")
            sys.stdout = tty_out
            return True
    except (OSError, Exception):
        pass

    return False
