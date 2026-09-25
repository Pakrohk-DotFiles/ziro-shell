"""ziro-shell — plugin command (full implementation).

Layer: 3 (Python core, cold-path only)
Spec: 001 FR-001
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from core.plugin_pipeline import add_plugin, remove_plugin


def _ziro_home() -> Path:
    return Path(os.environ.get("ZIRO_HOME", Path.home() / ".ziro"))


def _config_dir() -> Path:
    base = os.environ.get("ZIRO_CONFIG")
    if base:
        return Path(base)
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "ziro"


def _list_plugin_dirs(ziro_home: Path) -> list[Path]:
    pdir = ziro_home / "plugins"
    if not pdir.is_dir():
        return []
    return sorted(p for p in pdir.iterdir() if p.is_dir() and not p.name.startswith("."))


def cmd_list(argv: list[str]) -> int:
    dirs = _list_plugin_dirs(_ziro_home())
    if not dirs:
        print("(no plugins installed)")
        return 0
    for p in dirs:
        print(p.name)
    return 0


def cmd_show(argv: list[str]) -> int:
    if not argv:
        print("usage: plugin show <name>", file=sys.stderr)
        return 2
    name = argv[0]
    pdir = _ziro_home() / "plugins" / name
    if not pdir.is_dir():
        print(f"plugin not found: {name}", file=sys.stderr)
        return 1
    zsh_files = list(pdir.rglob("*.zsh"))
    print(f"plugin: {name}")
    print(f"path: {pdir}")
    print(f"zsh files: {len(zsh_files)}")
    tag_file = _config_dir() / "tags" / "plugins" / f"{name}.toml"
    if tag_file.is_file():
        print(f"tags file: {tag_file}")
    return 0


def cmd_add(argv: list[str]) -> int:
    if not argv:
        print("usage: plugin add <source> [name] [@tags...]", file=sys.stderr)
        return 2
    dry_run = "--dry-run" in argv
    positional = [a for a in argv if not a.startswith("--")]
    tags = [a for a in argv if a.startswith("@")]
    source = positional[0] if positional else ""
    name = positional[1] if len(positional) > 1 and not positional[1].startswith("@") else ""

    if not source:
        print("usage: plugin add <source> [name] [@tags...]", file=sys.stderr)
        return 2

    # Normalize GitHub slug → URL
    if "/" in source and not source.startswith(("http://", "https://", "git@", "ssh://")):
        source = f"https://github.com/{source}.git"

    try:
        result = add_plugin(
            source,
            name=name,
            tags=tags,
            ziro_home=_ziro_home(),
            config_dir=_config_dir(),
            dry_run=dry_run,
        )
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    prefix = "[dry-run] " if result.dry_run else ""
    print(f"{prefix}plugin: {result.plugin}")
    print(f"{prefix}strategy: {result.strategy}")
    print(f"{prefix}path: {result.plugin_dir}")
    if result.skipped_clone:
        print("(already cloned — skipped)")
    if not result.dry_run:
        print(f"✅ regenerated: {result.generated}")
    return 0


def cmd_remove(argv: list[str]) -> int:
    if not argv:
        print("usage: plugin remove <name>", file=sys.stderr)
        return 2
    dry_run = "--dry-run" in argv
    positional = [a for a in argv if not a.startswith("--")]
    if not positional:
        print("usage: plugin remove <name>", file=sys.stderr)
        return 2
    name = positional[0]
    ok = remove_plugin(
        name,
        ziro_home=_ziro_home(),
        config_dir=_config_dir(),
        dry_run=dry_run,
    )
    if not ok:
        print(f"plugin not found: {name}", file=sys.stderr)
        return 1
    prefix = "[dry-run] " if dry_run else ""
    print(f"{prefix}removed: {name}")
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
