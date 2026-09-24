"""ziro-shell — Python CLI dispatcher.

Layer: 3 (Python core, cold-path only)
Spec: 006 R4

Usage: python3 -m core <subcommand> [args...]
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    args = list(argv or sys.argv[1:])
    if not args:
        print("usage: python3 -m core <subcommand> [args...]", file=sys.stderr)
        print("subcommands: theme, prompt, install, plugin", file=sys.stderr)
        return 2

    sub = args[0]
    rest = args[1:]

    if sub == "theme":
        from core import theme_cli
        return theme_cli.main(rest)
    if sub == "prompt":
        from core import prompt_cli
        return prompt_cli.main(rest)
    if sub == "install":
        from core import install_cli
        return install_cli.main(rest)
    if sub == "plugin":
        from core import plugin_cli
        return plugin_cli.main(rest)

    print(f"unknown subcommand: {sub}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
