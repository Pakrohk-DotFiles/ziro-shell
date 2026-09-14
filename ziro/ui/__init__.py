"""Console UI package. Provides both the new UI port and backward-compatible module-level functions."""

from .plain import PlainConsoleUI

_default_ui = PlainConsoleUI()


def get_ui() -> PlainConsoleUI:
    return PlainConsoleUI()


# Backward-compatible module-level functions (old callers do `from . import ui; ui.info(...)`)
info = _default_ui.info
success = _default_ui.success
warn = _default_ui.warn
error = _default_ui.error
installed = _default_ui.installed
present = _default_ui.present
configured = _default_ui.configured
updated = _default_ui.updated
skipped = _default_ui.skipped
failed = _default_ui.failed
section = _default_ui.section
banner = _default_ui.banner
prompt = _default_ui.prompt
confirm = _default_ui.confirm
getting_started = _default_ui.getting_started

# Color constants for direct use by callers (e.g. installer.py print statements)
BLUE = "\033[0;34m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
RESET = "\033[0m"

__all__ = [
    "PlainConsoleUI", "get_ui",
    "info", "success", "warn", "error", "installed", "present",
    "configured", "updated", "skipped", "failed", "section",
    "banner", "prompt", "confirm", "getting_started",
    "BLUE", "GREEN", "YELLOW", "RED", "CYAN", "BOLD", "RESET",
]
