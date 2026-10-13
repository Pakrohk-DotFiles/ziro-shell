"""ziro-shell — config command.

Layer: 3 (Python core, cold-path only)
Spec: 006 R4
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _config_dir() -> Path:
    base = os.environ.get("ZIRO_CONFIG")
    if base:
        return Path(base)
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "ziro"


def cmd_show(argv: list[str]) -> int:
    cfg = _config_dir()
    print(f"config dir: {cfg}")
    print()
    for name in ("defaults.toml", "tools.toml", ".theme.conf", "prompt.conf"):
        p = cfg / name
        status = "✅" if p.is_file() else "❌ (missing)"
        print(f" {name:20s} {status}")
    return 0


def cmd_edit(argv: list[str]) -> int:
    cfg = _config_dir()
    target = argv[0] if argv else "defaults.toml"
    path = cfg / target
    if not path.is_file():
        print(f"config file not found: {path}", file=sys.stderr)
        return 1
    editor = os.environ.get("EDITOR", "vi")
    print(f"opening {path} with {editor}")
    if not sys.stdin.isatty():
        print("(non-tty; not launching editor)", file=sys.stderr)
        return 0
    try:
        subprocess.run([editor, str(path)])
    except FileNotFoundError:
        print(f"editor not found: {editor}", file=sys.stderr)
        return 1
    return 0


def cmd_set(argv: list[str]) -> int:
    print("NOTE: config set is not yet implemented.", file=sys.stderr)
    print(" Use `config edit` for now.", file=sys.stderr)
    return 1


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: config <show|edit|set>", file=sys.stderr)
        return 2
    sub, rest = argv[0], argv[1:]
    handlers = {
        "show": cmd_show,
        "edit": cmd_edit,
        "set": cmd_set,
    }
    handler = handlers.get(sub)
    if handler is None:
        print(f"unknown config subcommand: {sub}", file=sys.stderr)
        return 2
    return handler(rest)


__all__ = ["main"]
