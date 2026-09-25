"""ziro-shell — suggest command (auto_suggest component).

Layer: 3 (Python core, cold-path only)
Spec: 006 R4
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from core.theme import read_theme_conf, write_theme_conf, ThemeSelection


def _config_dir() -> Path:
    base = os.environ.get("ZIRO_CONFIG")
    if base:
        return Path(base)
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "ziro"


def cmd_list(argv: list[str]) -> int:
    print("available auto_suggest options:")
    print(" * ziro-ghost (default)")
    print(" zsh-autosuggestions (classic alternative)")
    print(" none (disable)")
    return 0


def cmd_set(argv: list[str]) -> int:
    if not argv:
        print("usage: suggest set <name>", file=sys.stderr)
        return 2
    name = argv[0].lower()
    valid = ("ziro-ghost", "zsh-autosuggestions", "none")
    if name not in valid:
        print(f"unsupported: {name}", file=sys.stderr)
        print(f"choose from: {', '.join(valid)}", file=sys.stderr)
        return 2
    cfg = _config_dir()
    sel = read_theme_conf(cfg)
    sel = ThemeSelection(
        prompt=sel.prompt,
        prompt_component=sel.prompt_component,
        auto_suggest=name,
        auto_suggest_component=sel.auto_suggest_component,
        colors=sel.colors,
        syntax_highlighting=sel.syntax_highlighting,
    )
    write_theme_conf(cfg, sel)
    print(f"auto_suggest set to: {name}")
    return 0


def cmd_disable(argv: list[str]) -> int:
    return cmd_set(["none"])


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: suggest <list|set|disable>", file=sys.stderr)
        return 2
    sub, rest = argv[0], argv[1:]
    handlers = {
        "list": cmd_list,
        "set": cmd_set,
        "disable": cmd_disable,
    }
    handler = handlers.get(sub)
    if handler is None:
        print(f"unknown suggest subcommand: {sub}", file=sys.stderr)
        return 2
    return handler(rest)


__all__ = ["main"]
