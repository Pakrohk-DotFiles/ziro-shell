"""ziro-shell — prompt CLI subcommands.

Layer: 3 (Python core, cold-path only)
Spec: 006 R4
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from core.prompt import (
    SUPPORTED_PROMPTS,
    list_prompts, read_prompt_conf, write_prompt_conf,
)


def _config_dir() -> Path:
    base = os.environ.get("ZIRO_CONFIG")
    if base:
        return Path(base)
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "ziro"


def _prompts_dir() -> Path:
    home = os.environ.get("ZIRO_HOME", Path.home() / ".ziro")
    return Path(home) / "prompts"


def cmd_list(argv: list[str]) -> int:
    available = list_prompts(_prompts_dir())
    if not available:
        print("(no prompt adapters found)")
        return 0
    current = read_prompt_conf(_config_dir())
    for name in available:
        marker = "*" if name == current else " "
        print(f" {marker} {name}")
    return 0


def cmd_current(argv: list[str]) -> int:
    print(read_prompt_conf(_config_dir()))
    return 0


def cmd_set(argv: list[str]) -> int:
    if not argv:
        print("usage: prompt set <name>", file=sys.stderr)
        print(f"available: {', '.join(SUPPORTED_PROMPTS)}", file=sys.stderr)
        return 2
    name = argv[0].lower()
    if name not in SUPPORTED_PROMPTS:
        print(f"unsupported prompt: {name}", file=sys.stderr)
        print(f"choose from: {', '.join(SUPPORTED_PROMPTS)}", file=sys.stderr)
        return 2
    write_prompt_conf(_config_dir(), name)
    print(f"prompt set to: {name}")
    print("(restart shell or run `exec zsh` to see changes)")
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: prompt <list|current|set>", file=sys.stderr)
        return 2
    sub, rest = argv[0], argv[1:]
    handlers = {
        "list": cmd_list,
        "current": cmd_current,
        "set": cmd_set,
    }
    handler = handlers.get(sub)
    if handler is None:
        print(f"unknown prompt subcommand: {sub}", file=sys.stderr)
        return 2
    return handler(rest)


__all__ = ["main"]
