"""Plain (stdlib-only) console UI implementation. Matches existing ui.py behavior."""

from __future__ import annotations

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


class PlainConsoleUI:
    def __init__(self, *, is_tty: bool | None = None, term: str | None = None,
                 no_color: str | None = None, stdin_tty: bool | None = None) -> None:
        if is_tty is not None:
            self._tty = is_tty
        else:
            self._tty = sys.stdout.isatty()
        if term is not None:
            self._term = term
        else:
            self._term = os.environ.get("TERM")
        if no_color is not None:
            self._no_color = no_color
        else:
            self._no_color = os.environ.get("NO_COLOR")
        if stdin_tty is not None:
            self._stdin_tty = stdin_tty
        else:
            self._stdin_tty = sys.stdin.isatty()
        self._use_color = self._tty and self._term != "dumb" and self._no_color is None
        self._colors = {"[i]": BLUE, "[+]": GREEN, "[!]": YELLOW, "[x]": RED}
        self._icons = {"[i]": "[i]", "[+]": "[+]", "[!]": "[!]", "[x]": "[x]"}
        self._ttyicons = {"[i]": "[*]", "[+]": "[✓]", "[!]": "[!]", "[x]": "[✗]"}

    def _emit(self, icon: str, msg: str, stream=None) -> None:
        if stream is None:
            stream = sys.stdout
        color = self._colors.get(icon, "") if self._use_color else ""
        glyph = self._ttyicons.get(icon, icon) if self._tty else self._icons.get(icon, icon)
        print(f"{color}{glyph}{RESET} {msg}", file=stream, flush=True)

    def info(self, msg: str) -> None:
        self._emit("[i]", msg)

    def success(self, msg: str) -> None:
        self._emit("[+]", msg)

    def warn(self, msg: str) -> None:
        self._emit("[!]", msg)

    def error(self, msg: str) -> None:
        self._emit("[x]", msg, stream=sys.stderr)

    def installed(self, msg: str) -> None:
        self.success(f"Installed {msg}")

    def present(self, msg: str) -> None:
        self.success(f"Already present: {msg}")

    def configured(self, msg: str) -> None:
        self.success(f"Configured {msg}")

    def updated(self, msg: str) -> None:
        self.success(f"Updated {msg}")

    def skipped(self, msg: str) -> None:
        self.warn(f"Skipped: {msg}")

    def failed(self, msg: str) -> None:
        self.error(f"Failed: {msg}")

    def section(self, title: str) -> None:
        if self._tty:
            print(f"\n{BLUE}{'─' * 18} {title} {'─' * 18}{RESET}\n")
        else:
            print(f"\n──── {title} ────\n")

    def banner(self) -> None:
        print(f"""{BLUE}=========================================={RESET}
{GREEN}         Ziro Configuration Installer     {RESET}
{BLUE}=========================================={RESET}""")

    def prompt(self, msg: str) -> None:
        print(f"{BOLD}{msg}{RESET} ", end="", flush=True)

    def confirm(self, question: str, default_yes: bool = True) -> bool:
        if not self._stdin_tty:
            return default_yes
        self.prompt(f"{question} [Y/n] " if default_yes else f"{question} [y/N] ")
        try:
            answer = input().strip().lower()
        except EOFError:
            return default_yes
        if not answer:
            return default_yes
        return answer in ("y", "yes")

    def getting_started(self, lines: list[str]) -> None:
        print(f"\n{GREEN}========== Getting started =========={RESET}")
        for line in lines:
            print(f"  {line}")
        print(f"{GREEN}====================================={RESET}\n")
