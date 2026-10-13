"""ziro-shell — tag command.

Layer: 3 (Python core, cold-path only)
Spec: 003 R6
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from core.tags import (
    load_all_tags,
    load_plugin_tags,
    save_plugin_tags,
)


def _config_dir() -> Path:
    base = os.environ.get("ZIRO_CONFIG")
    if base:
        return Path(base)
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "ziro"


def cmd_list(argv: list[str]) -> int:
    """List all built-in + user tags."""
    cfg = _config_dir()
    all_tags = load_all_tags(cfg)
    if not all_tags:
        print("(no tags defined)")
        return 0
    for name in sorted(all_tags):
        tag = all_tags[name]
        print(f"{name:20s} priority={tag.priority:2d} {tag.description}")
    return 0


def cmd_show(argv: list[str]) -> int:
    """Show tags for one plugin."""
    if not argv:
        print("usage: tag show <plugin>", file=sys.stderr)
        return 2
    name = argv[0]
    applied = load_plugin_tags(_config_dir(), name)
    if not applied:
        print(f"(no tags for plugin: {name})")
        return 0
    for t in applied:
        print(t)
    return 0


def cmd_add(argv: list[str]) -> int:
    """Add tag to plugin."""
    if len(argv) < 2:
        print("usage: tag add <plugin> <@tag>", file=sys.stderr)
        return 2
    plugin, tag = argv[0], argv[1]
    if not tag.startswith("@"):
        tag = "@" + tag
    cfg = _config_dir()
    all_tags = load_all_tags(cfg)
    if tag not in all_tags:
        print(f"unknown tag: {tag}", file=sys.stderr)
        print(f"available: {', '.join(sorted(all_tags))}", file=sys.stderr)
        return 2
    current = list(load_plugin_tags(cfg, plugin))
    if tag in current:
        print(f"already applied: {tag} on {plugin}")
        return 0
    current.append(tag)
    save_plugin_tags(cfg, plugin, current)
    print(f"added {tag} to {plugin}")
    return 0


def cmd_remove(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: tag remove <plugin> <@tag>", file=sys.stderr)
        return 2
    plugin, tag = argv[0], argv[1]
    if not tag.startswith("@"):
        tag = "@" + tag
    cfg = _config_dir()
    current = list(load_plugin_tags(cfg, plugin))
    if tag not in current:
        print(f"not applied: {tag} on {plugin}")
        return 0
    current.remove(tag)
    save_plugin_tags(cfg, plugin, current)
    print(f"removed {tag} from {plugin}")
    return 0


def cmd_reset(argv: list[str]) -> int:
    if not argv:
        print("usage: tag reset <plugin>", file=sys.stderr)
        return 2
    plugin = argv[0]
    cfg = _config_dir()
    save_plugin_tags(cfg, plugin, [])
    print(f"reset tags for {plugin}")
    return 0


def cmd_define(argv: list[str]) -> int:
    print("NOTE: tag define is not yet implemented.", file=sys.stderr)
    print(" Will be added in a follow-up phase.", file=sys.stderr)
    return 1


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: tag <list|show|add|remove|reset|define>", file=sys.stderr)
        return 2
    sub, rest = argv[0], argv[1:]
    handlers = {
        "list": cmd_list,
        "show": cmd_show,
        "add": cmd_add,
        "remove": cmd_remove,
        "reset": cmd_reset,
        "define": cmd_define,
    }
    handler = handlers.get(sub)
    if handler is None:
        print(f"unknown tag subcommand: {sub}", file=sys.stderr)
        return 2
    return handler(rest)


__all__ = ["main"]
