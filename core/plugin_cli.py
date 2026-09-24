"""ziro-shell — plugin command.

Layer: 3 (Python core, cold-path only)
Spec: 001 FR-001
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def _config_dir() -> Path:
    base = os.environ.get("ZIRO_CONFIG")
    if base:
        return Path(base)
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "ziro"


def _plugins_dir() -> Path:
    home = os.environ.get("ZIRO_HOME", Path.home() / ".ziro")
    return Path(home) / "plugins"


def cmd_list(argv: list[str]) -> int:
    pdir = _plugins_dir()
    if not pdir.is_dir():
        print("(no plugins installed)")
        return 0
    plugins = sorted(p.name for p in pdir.iterdir() if p.is_dir())
    if not plugins:
        print("(no plugins installed)")
        return 0
    for name in plugins:
        print(name)
    return 0


def cmd_show(argv: list[str]) -> int:
    if not argv:
        print("usage: plugin show <name>", file=sys.stderr)
        return 2
    name = argv[0]
    pdir = _plugins_dir() / name
    if not pdir.is_dir():
        print(f"plugin not found: {name}", file=sys.stderr)
        return 1
    print(f"plugin: {name}")
    print(f"path: {pdir}")
    files = list(pdir.rglob("*.zsh"))
    print(f"zsh files: {len(files)}")
    return 0


def cmd_add(argv: list[str]) -> int:
    if not argv:
        print("usage: plugin add <name> [@tags...]", file=sys.stderr)
        return 2
    name = argv[0]
    tags = [a for a in argv[1:] if a.startswith("@")]

    print(f"ziro plugin add: {name}")
    if tags:
        print(f"tags: {', '.join(tags)}")
    print("NOTE: full installation pipeline (clone+analyze+generate) not yet wired.")
    print(" This is a skeleton — full impl in Phase 6b.")
    return 0


def cmd_remove(argv: list[str]) -> int:
    if not argv:
        print("usage: plugin remove <name>", file=sys.stderr)
        return 2
    name = argv[0]
    pdir = _plugins_dir() / name
    if not pdir.is_dir():
        print(f"plugin not found: {name}", file=sys.stderr)
        return 1
    print(f"(dry) would remove: {pdir}")
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: plugin <add|remove|list|show>", file=sys.stderr)
        return 2
    sub, rest = argv[0], argv[1:]
    handlers = {
        "add": cmd_add,
        "remove": cmd_remove,
        "list": cmd_list,
        "show": cmd_show,
    }
    handler = handlers.get(sub)
    if handler is None:
        print(f"unknown plugin subcommand: {sub}", file=sys.stderr)
        return 2
    return handler(rest)


__all__ = ["main"]
