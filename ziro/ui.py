"""Console UI helpers: colored, TTY-aware status messages.

Status vocabulary: Installed / Already present / Configured / Updated /
Skipped / Failed.
"""

import os
import sys

_TTY = sys.stdout.isatty()

if _TTY and os.environ.get("TERM") != "dumb" and os.environ.get("NO_COLOR") is None:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    BLUE = "\033[0;34m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    CYAN = "\033[0;36m"
else:
    RESET = BOLD = BLUE = GREEN = YELLOW = RED = CYAN = ""

_COLORS = {"[i]": BLUE, "[+]": GREEN, "[!]": YELLOW, "[x]": RED}
_ICONS = {"[i]": "[i]", "[+]": "[+]", "[!]": "[!]", "[x]": "[x]"}
_TTYICONS = {"[i]": "[*]", "[+]": "[✓]", "[!]": "[!]", "[x]": "[✗]"}


def _emit(icon: str, msg: str, stream=sys.stdout) -> None:
    color = _COLORS[icon] if _TTY else ""
    glyph = _TTYICONS[icon] if _TTY else _ICONS[icon]
    print(f"{color}{glyph}{RESET} {msg}", file=stream, flush=True)


def info(msg: str) -> None:
    _emit("[i]", msg)


def success(msg: str) -> None:
    _emit("[+]", msg)


def warn(msg: str) -> None:
    _emit("[!]", msg)


def error(msg: str) -> None:
    _emit("[x]", msg, stream=sys.stderr)


def installed(msg: str) -> None:
    success(f"Installed {msg}")


def present(msg: str) -> None:
    success(f"Already present: {msg}")


def configured(msg: str) -> None:
    success(f"Configured {msg}")


def updated(msg: str) -> None:
    success(f"Updated {msg}")


def skipped(msg: str) -> None:
    warn(f"Skipped: {msg}")


def failed(msg: str) -> None:
    error(f"Failed: {msg}")


def section(title: str) -> None:
    print(f"\n{BLUE}{'─' * 18} {title} {'─' * 18}{RESET}\n" if _TTY else f"\n──── {title} ────\n")


def banner() -> None:
    print(f"""{BLUE}=========================================={RESET}
{GREEN}         Ziro Configuration Installer     {RESET}
{BLUE}=========================================={RESET}""")


def prompt(msg: str) -> None:
    print(f"{BOLD}{msg}{RESET} ", end="", flush=True)


def _read_line() -> str:
    """Read one line from the controlling terminal.

    curl|bash pipelines leave stdin bound to the script text, so answer
    from /dev/tty when present; otherwise fall back to stdin.
    """
    try:
        with open("/dev/tty", "r") as tty:
            return tty.readline()
    except OSError:
        try:
            return input()
        except EOFError:
            return ""


def confirm(question: str, default_yes: bool = True) -> bool:
    if not sys.stdin.isatty():
        return default_yes
    suffix = "[Y/n]" if default_yes else "[y/N]"
    prompt(f"{question} {suffix} ")
    answer = _read_line().strip().lower()
    if not answer:
        return default_yes
    return answer in ("y", "yes")


def getting_started(lines: list[str]) -> None:
    print(f"\n{GREEN}========== Getting started =========={RESET}")
    for line in lines:
        print(f"  {line}")
    print(f"{GREEN}====================================={RESET}\n")
