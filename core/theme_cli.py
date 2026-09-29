"""ziro-shell — theme CLI subcommands.

Layer: 3 (Python core, cold-path only)
Spec: 006 R4
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from core.theme import (
    COMPONENTS, ThemeSelection,
    list_themes, read_theme_conf, theme_path, write_theme_conf,
)


def _config_dir() -> Path:
    base = os.environ.get("ZIRO_CONFIG")
    if base:
        return Path(base)
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "ziro"


def _themes_dir() -> Path:
    home = os.environ.get("ZIRO_HOME", Path.home() / ".ziro")
    return Path(home) / "themes"


def cmd_list(argv: list[str]) -> int:
    component = "prompt"
    if "--component" in argv:
        idx = argv.index("--component")
        if idx + 1 < len(argv):
            component = argv[idx + 1]
    themes = list_themes(_themes_dir(), component)
    if not themes:
        print(f"(no themes for component: {component})")
        return 0
    for name in themes:
        print(name)
    return 0


def cmd_current(argv: list[str]) -> int:
    sel = read_theme_conf(_config_dir())
    print(f"prompt: {sel.prompt} ({sel.prompt_component})")
    print(f"auto_suggest: {sel.auto_suggest} ({sel.auto_suggest_component})")
    print(f"colors: {sel.colors}")
    print(f"syntax_highlighting: {sel.syntax_highlighting}")
    return 0


def cmd_apply(argv: list[str]) -> int:
    if not argv:
        print("usage: theme apply <name> [--component <comp>]", file=sys.stderr)
        return 2
    name = argv[0]
    component = "prompt"
    if "--component" in argv:
        idx = argv.index("--component")
        if idx + 1 < len(argv):
            component = argv[idx + 1]
    if component not in COMPONENTS:
        print(f"unknown component: {component}", file=sys.stderr)
        return 2

    cfg = _config_dir()
    sel = read_theme_conf(cfg)
    data = {
        "prompt": sel.prompt,
        "prompt_component": sel.prompt_component,
        "auto_suggest": sel.auto_suggest,
        "auto_suggest_component": sel.auto_suggest_component,
        "colors": sel.colors,
        "syntax_highlighting": sel.syntax_highlighting,
    }
    data[component] = name
    sel = ThemeSelection(**data)
    write_theme_conf(cfg, sel)
    print(f"applied: {component} = {name}")
    return 0


def cmd_reset(argv: list[str]) -> int:
    cfg = _config_dir()
    write_theme_conf(cfg, ThemeSelection())
    print("theme reset to defaults")
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: theme <list|current|apply|reset>", file=sys.stderr)
        return 2
    sub, rest = argv[0], argv[1:]
    handlers = {
        "list": cmd_list,
        "current": cmd_current,
        "apply": cmd_apply,
        "reset": cmd_reset,
    }
    handler = handlers.get(sub)
    if handler is None:
        print(f"unknown theme subcommand: {sub}", file=sys.stderr)
        return 2
    return handler(rest)


__all__ = ["main"]
