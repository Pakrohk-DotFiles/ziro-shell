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
    load_builtin_tags,
    load_user_tags,
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
    from core.help_cli import handle_help_if_requested
    ret = handle_help_if_requested(argv, "tag", subcommand="list")
    if ret is not None:
        return ret
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
    from core.help_cli import handle_help_if_requested
    ret = handle_help_if_requested(argv, "tag", subcommand="show")
    if ret is not None:
        return ret
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
    from core.help_cli import handle_help_if_requested
    ret = handle_help_if_requested(argv, "tag", subcommand="add")
    if ret is not None:
        return ret
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
    from core.help_cli import handle_help_if_requested
    ret = handle_help_if_requested(argv, "tag", subcommand="remove")
    if ret is not None:
        return ret
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
    from core.help_cli import handle_help_if_requested
    ret = handle_help_if_requested(argv, "tag", subcommand="reset")
    if ret is not None:
        return ret
    if not argv:
        print("usage: tag reset <plugin>", file=sys.stderr)
        return 2
    plugin = argv[0]
    cfg = _config_dir()
    save_plugin_tags(cfg, plugin, [])
    print(f"reset tags for {plugin}")
    return 0


def cmd_define(argv: list[str]) -> int:
    from core.help_cli import handle_help_if_requested
    ret = handle_help_if_requested(argv, "tag", subcommand="define")
    if ret is not None:
        return ret

    if not argv:
        print("usage: tag define <@name> --strategy=<eager|defer|raw> [--priority=<N>] [--description=<text>] [--force]", file=sys.stderr)
        return 2

    name = ""
    strategy = "eager"
    priority = 5
    description = ""
    force = False

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--force":
            force = True
        elif arg.startswith("--strategy="):
            strategy = arg.split("=", 1)[1]
        elif arg == "--strategy" and i + 1 < len(argv):
            i += 1
            strategy = argv[i]
        elif arg.startswith("--priority="):
            try:
                priority = int(arg.split("=", 1)[1])
            except ValueError:
                print(f"error: invalid priority '{arg}' (must be integer)", file=sys.stderr)
                return 2
        elif arg == "--priority" and i + 1 < len(argv):
            i += 1
            try:
                priority = int(argv[i])
            except ValueError:
                print(f"error: invalid priority '{argv[i]}' (must be integer)", file=sys.stderr)
                return 2
        elif arg.startswith("--description="):
            description = arg.split("=", 1)[1]
        elif arg == "--description" and i + 1 < len(argv):
            i += 1
            description = argv[i]
        elif not arg.startswith("-") and not name:
            name = arg
        i += 1

    if not name:
        print("usage: tag define <@name> --strategy=<eager|defer|raw> [--priority=<N>] [--description=<text>] [--force]", file=sys.stderr)
        return 2

    if not name.startswith("@"):
        name = "@" + name

    if len(name) < 2 or not name[1:].replace("-", "").replace("_", "").isalnum():
        print(f"error: invalid tag name '{name}' (must start with @ and contain alphanumeric/hyphen characters)", file=sys.stderr)
        return 2

    if strategy not in ("eager", "defer", "raw"):
        print(f"error: invalid strategy '{strategy}' (must be eager, defer, or raw)", file=sys.stderr)
        return 2

    if priority < 0 or priority > 100:
        print("error: priority must be integer between 0 and 100", file=sys.stderr)
        return 2

    cfg = _config_dir()
    builtins = load_builtin_tags(cfg)
    if name in builtins and not force:
        print(f"error: '{name}' collides with built-in tag (use --force to override)", file=sys.stderr)
        return 1

    user_tags = load_user_tags(cfg)
    if name in user_tags and not force:
        print(f"error: tag '{name}' already defined in user.toml (use --force to override)", file=sys.stderr)
        return 1

    user_file = cfg / "tags" / "user.toml"
    user_file.parent.mkdir(parents=True, exist_ok=True)

    existing_list = []
    found = False
    for t_name, t in user_tags.items():
        if t_name == name:
            existing_list.append({
                "name": name,
                "strategy": strategy,
                "priority": priority,
                "description": description or t.description,
            })
            found = True
        else:
            existing_list.append({
                "name": t.name,
                "strategy": t.strategy,
                "priority": t.priority,
                "description": t.description,
            })
    if not found:
        existing_list.append({
            "name": name,
            "strategy": strategy,
            "priority": priority,
            "description": description,
        })

    lines = [
        "# ziro-shell — user-defined tags",
        "# Spec: 003",
        "",
        "[meta]",
        'schema = "0.1.0"',
        f"count = {len(existing_list)}",
        "",
    ]
    for item in existing_list:
        lines.append("[[tags]]")
        lines.append(f"name = \"{item['name']}\"")
        lines.append(f"strategy = \"{item['strategy']}\"")
        lines.append(f"priority = {item['priority']}")
        if item.get("description"):
            lines.append(f"description = \"{item['description']}\"")
        lines.append("")

    user_file.write_text("\n".join(lines))
    print(f"✅ defined tag {name} in {user_file}")
    return 0


def main(argv: list[str]) -> int:
    from core.help_cli import handle_help_if_requested
    ret = handle_help_if_requested(argv, "tag")
    if ret is not None:
        return ret
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
