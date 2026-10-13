"""ziro-shell — centralized help registry and command documentation.

Layer: 3 (Python core, cold-path only)
Spec: 008 R1, R2, R7, R10
"""

from __future__ import annotations

import difflib
import sys
from dataclasses import dataclass, field


@dataclass
class HelpEntry:
    name: str
    summary: str
    usage: str
    subcommands: dict[str, str] = field(default_factory=dict)
    flags: list[tuple[str, str]] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.subcommands, list):
            self.subcommands = {s: "" for s in self.subcommands}


HELP_REGISTRY: dict[str, HelpEntry] = {
    "install": HelpEntry(
        name="install",
        summary="Install ziro with defaults or custom profile",
        usage="ziro install [--default | --custom] [--dry-run]",
        flags=[
            ("--default", "Install with pre-configured defaults (Starship, recommended plugins)"),
            ("--custom", "Interactive prompt to choose components manually"),
            ("--dry-run", "Preview files that would be written without writing"),
        ],
        examples=[
            "ziro install",
            "ziro install --default",
            "ziro install --dry-run",
        ],
        related=["doctor", "config"],
    ),
    "plugin": HelpEntry(
        name="plugin",
        summary="Manage plugins (add, remove, list, show)",
        usage="ziro plugin <add|remove|list|show> [args...]",
        subcommands={
            "add": "Add and analyze a plugin from Git repository or GitHub slug",
            "remove": "Remove an installed plugin",
            "list": "List all installed plugins and their load strategies",
            "show": "Show detailed analysis and resolved strategy for a plugin",
        },
        flags=[
            ("--dry-run", "Simulate plugin addition or removal without disk changes"),
        ],
        examples=[
            "ziro plugin list",
            "ziro plugin add zsh-users/zsh-autosuggestions",
            "ziro plugin add romkatv/powerlevel10k @eager",
            "ziro plugin show zsh-autosuggestions",
            "ziro plugin remove zsh-autosuggestions",
        ],
        related=["tag"],
    ),
    "plugin add": HelpEntry(
        name="plugin add",
        summary="Add and analyze a plugin",
        usage="ziro plugin add <source> [name] [@tags...] [--dry-run]",
        flags=[
            ("--dry-run", "Preview plugin clone, analysis, and strategy without saving"),
        ],
        examples=[
            "ziro plugin add zsh-users/zsh-autosuggestions",
            "ziro plugin add https://github.com/zsh-users/zsh-syntax-highlighting.git",
            "ziro plugin add romkatv/powerlevel10k @eager",
        ],
        related=["plugin show", "tag add"],
    ),
    "plugin remove": HelpEntry(
        name="plugin remove",
        summary="Remove an installed plugin",
        usage="ziro plugin remove <name> [--dry-run]",
        flags=[
            ("--dry-run", "Preview plugin removal without deleting files"),
        ],
        examples=[
            "ziro plugin remove zsh-autosuggestions",
        ],
        related=["plugin list"],
    ),
    "plugin list": HelpEntry(
        name="plugin list",
        summary="List all installed plugins and their load strategies",
        usage="ziro plugin list",
        examples=[
            "ziro plugin list",
        ],
        related=["plugin show"],
    ),
    "plugin show": HelpEntry(
        name="plugin show",
        summary="Show detailed plugin analysis and tags",
        usage="ziro plugin show <name>",
        examples=[
            "ziro plugin show zsh-autosuggestions",
        ],
        related=["plugin list", "tag show"],
    ),
    "tag": HelpEntry(
        name="tag",
        summary="Manage plugin tags (list, show, add, remove, reset, define)",
        usage="ziro tag <list|show|add|remove|reset|define> [args...]",
        subcommands={
            "list": "List available builtin and user tags",
            "show": "Show tags applied to a specific plugin",
            "add": "Apply a tag to a plugin",
            "remove": "Remove a tag from a plugin",
            "reset": "Reset user tags for a plugin to defaults",
            "define": "Define a custom tag in user.toml",
        },
        examples=[
            "ziro tag list",
            "ziro tag show zsh-autosuggestions",
            "ziro tag add zsh-autosuggestions @eager",
            "ziro tag remove zsh-autosuggestions @eager",
        ],
        related=["plugin"],
    ),
    "tag list": HelpEntry(
        name="tag list",
        summary="List available builtin and user tags",
        usage="ziro tag list [--builtin | --user]",
        flags=[
            ("--builtin", "Display only built-in system tags"),
            ("--user", "Display only user-defined tags"),
        ],
        examples=[
            "ziro tag list",
            "ziro tag list --builtin",
        ],
        related=["tag show"],
    ),
    "tag show": HelpEntry(
        name="tag show",
        summary="Show tags applied to a specific plugin",
        usage="ziro tag show <plugin>",
        examples=[
            "ziro tag show zsh-autosuggestions",
        ],
        related=["tag list", "tag add"],
    ),
    "tag add": HelpEntry(
        name="tag add",
        summary="Apply a tag to a plugin",
        usage="ziro tag add <plugin> <@tag>",
        examples=[
            "ziro tag add zsh-autosuggestions @eager",
        ],
        related=["tag remove", "tag show"],
    ),
    "tag remove": HelpEntry(
        name="tag remove",
        summary="Remove a tag from a plugin",
        usage="ziro tag remove <plugin> <@tag>",
        examples=[
            "ziro tag remove zsh-autosuggestions @eager",
        ],
        related=["tag add", "tag show"],
    ),
    "tag reset": HelpEntry(
        name="tag reset",
        summary="Reset user tags for a plugin",
        usage="ziro tag reset <plugin>",
        examples=[
            "ziro tag reset zsh-autosuggestions",
        ],
        related=["tag show"],
    ),
    "tag define": HelpEntry(
        name="tag define",
        summary="Define a custom tag in user.toml",
        usage="ziro tag define <@name> --strategy=<eager|defer|raw> [--priority=<N>] [--description=<text>] [--force]",
        flags=[
            ("--strategy=<val>", "Load strategy: eager, defer, or raw"),
            ("--priority=<N>", "Priority integer 0-100 (default: 5)"),
            ("--description=<text>", "Short description of the tag"),
            ("--force", "Override existing builtin or user tag"),
        ],
        examples=[
            "ziro tag define @custom --strategy=eager --priority=7",
            "ziro tag define @slow --strategy=defer --priority=3 --description='Load late'",
        ],
        related=["tag list", "tag show"],
    ),
    "suggest": HelpEntry(
        name="suggest",
        summary="Manage auto-suggest component",
        usage="ziro suggest <list|set|disable> [args...]",
        subcommands={
            "list": "List available auto-suggest providers",
            "set": "Set active auto-suggest provider",
            "disable": "Disable auto-suggest component",
        },
        examples=[
            "ziro suggest list",
            "ziro suggest set zsh-autosuggestions",
            "ziro suggest disable",
        ],
        related=["theme"],
    ),
    "suggest list": HelpEntry(
        name="suggest list",
        summary="List available auto-suggest providers",
        usage="ziro suggest list",
        examples=[
            "ziro suggest list",
        ],
        related=["suggest set"],
    ),
    "suggest set": HelpEntry(
        name="suggest set",
        summary="Set active auto-suggest provider",
        usage="ziro suggest set <name>",
        examples=[
            "ziro suggest set zsh-autosuggestions",
            "ziro suggest set ziro-ghost",
        ],
        related=["suggest list", "suggest disable"],
    ),
    "suggest disable": HelpEntry(
        name="suggest disable",
        summary="Disable auto-suggest component",
        usage="ziro suggest disable",
        examples=[
            "ziro suggest disable",
        ],
        related=["suggest set"],
    ),
    "theme": HelpEntry(
        name="theme",
        summary="Manage shell themes and appearance",
        usage="ziro theme <list|current|apply|reset> [args...]",
        subcommands={
            "list": "List available theme components",
            "current": "Show currently active theme selection",
            "apply": "Apply a theme or component style",
            "reset": "Reset theme configuration to defaults",
        },
        flags=[
            ("--component <comp>", "Component to apply theme to (prompt, auto_suggest, colors, syntax_highlighting)"),
        ],
        examples=[
            "ziro theme current",
            "ziro theme list",
            "ziro theme apply default",
        ],
        related=["prompt", "suggest"],
    ),
    "theme list": HelpEntry(
        name="theme list",
        summary="List available theme presets and components",
        usage="ziro theme list",
        examples=[
            "ziro theme list",
        ],
        related=["theme current", "theme apply"],
    ),
    "theme current": HelpEntry(
        name="theme current",
        summary="Show currently active theme configuration",
        usage="ziro theme current",
        examples=[
            "ziro theme current",
        ],
        related=["theme apply"],
    ),
    "theme apply": HelpEntry(
        name="theme apply",
        summary="Apply a theme preset or component style",
        usage="ziro theme apply <name> [--component <comp>]",
        flags=[
            ("--component <comp>", "Component target: prompt, auto_suggest, colors, syntax_highlighting"),
        ],
        examples=[
            "ziro theme apply default",
            "ziro theme apply iris --component prompt",
        ],
        related=["theme current"],
    ),
    "theme reset": HelpEntry(
        name="theme reset",
        summary="Reset theme configuration to defaults",
        usage="ziro theme reset",
        examples=[
            "ziro theme reset",
        ],
        related=["theme current"],
    ),
    "prompt": HelpEntry(
        name="prompt",
        summary="Manage shell prompt engine",
        usage="ziro prompt <list|current|set> [args...]",
        subcommands={
            "list": "List supported prompt engines (starship, p10k, pure, none)",
            "current": "Display currently active prompt engine",
            "set": "Set active prompt engine",
        },
        examples=[
            "ziro prompt list",
            "ziro prompt current",
            "ziro prompt set starship",
            "ziro prompt set none",
        ],
        related=["theme"],
    ),
    "prompt list": HelpEntry(
        name="prompt list",
        summary="List supported prompt engines",
        usage="ziro prompt list",
        examples=[
            "ziro prompt list",
        ],
        related=["prompt set"],
    ),
    "prompt current": HelpEntry(
        name="prompt current",
        summary="Display currently active prompt engine",
        usage="ziro prompt current",
        examples=[
            "ziro prompt current",
        ],
        related=["prompt set"],
    ),
    "prompt set": HelpEntry(
        name="prompt set",
        summary="Set active prompt engine",
        usage="ziro prompt set <name>",
        examples=[
            "ziro prompt set starship",
            "ziro prompt set p10k",
            "ziro prompt set pure",
            "ziro prompt set none",
        ],
        related=["prompt current", "prompt list"],
    ),
    "config": HelpEntry(
        name="config",
        summary="Inspect and manage configuration files",
        usage="ziro config <show|edit|set> [args...]",
        subcommands={
            "show": "Print contents of defaults.toml or tools.toml",
            "edit": "Open defaults.toml or tools.toml in $EDITOR",
            "set": "Set configuration key in defaults.toml",
        },
        examples=[
            "ziro config show",
            "ziro config show tools",
            "ziro config edit defaults",
        ],
        related=["install", "doctor"],
    ),
    "config show": HelpEntry(
        name="config show",
        summary="Display configuration file contents",
        usage="ziro config show [defaults | tools]",
        examples=[
            "ziro config show",
            "ziro config show tools",
        ],
        related=["config edit"],
    ),
    "config edit": HelpEntry(
        name="config edit",
        summary="Edit configuration file in $EDITOR",
        usage="ziro config edit [defaults | tools]",
        examples=[
            "ziro config edit defaults",
            "ziro config edit tools",
        ],
        related=["config show"],
    ),
    "config set": HelpEntry(
        name="config set",
        summary="Set configuration option in defaults.toml",
        usage="ziro config set <category.key> <value>",
        examples=[
            "ziro config set prompt.default pure",
            "ziro config set auto_suggest.default zsh-autosuggestions",
            "ziro config set ui.rich false",
        ],
        related=["config show", "config edit"],
    ),
    "doctor": HelpEntry(
        name="doctor",
        summary="Diagnose installation health and configuration",
        usage="ziro doctor [--verbose|-v]",
        flags=[
            ("--verbose, -v", "Display detailed diagnostic messages"),
        ],
        examples=[
            "ziro doctor",
            "ziro doctor --verbose",
        ],
        related=["bench", "config"],
    ),
    "bench": HelpEntry(
        name="bench",
        summary="Benchmark startup and command performance",
        usage="ziro bench [--iters <n>]",
        flags=[
            ("--iters <n>", "Number of iterations for min-of-N benchmark (default: 11)"),
        ],
        examples=[
            "ziro bench",
            "ziro bench --iters 15",
        ],
        related=["doctor"],
    ),
    "help": HelpEntry(
        name="help",
        summary="Show help information for ziro commands",
        usage="ziro help [command [subcommand]]",
        examples=[
            "ziro help",
            "ziro help install",
            "ziro help plugin",
            "ziro help plugin add",
        ],
        related=[],
    ),
}


def get_entry(name: str) -> HelpEntry | None:
    """Retrieve help entry by command name or composite subcommand."""
    normalized = " ".join(name.strip().split())
    if not normalized:
        return None
    if normalized in HELP_REGISTRY:
        return HELP_REGISTRY[normalized]

    parts = normalized.split()
    if len(parts) > 1 and parts[0] in HELP_REGISTRY:
        parent = HELP_REGISTRY[parts[0]]
        sub = parts[1]
        if sub in parent.subcommands:
            return HelpEntry(
                name=f"{parent.name} {sub}",
                summary=parent.subcommands[sub],
                usage=f"ziro {parent.name} {sub} [args...]",
                related=[parent.name],
            )
    return None


def suggest_similar(name: str) -> str | None:
    """Fuzzy match unknown command to registered commands or subcommands."""
    normalized = " ".join(name.strip().split()).lower()
    if not normalized:
        return None

    # Check if this matches a subcommand of a top-level command
    for parent_name, entry in HELP_REGISTRY.items():
        if " " not in parent_name and normalized in entry.subcommands:
            return f"{parent_name} {normalized}"

    # Fuzzy match against top-level command names
    top_cmds = [k for k in HELP_REGISTRY if " " not in k]
    matches = difflib.get_close_matches(normalized, top_cmds, n=1, cutoff=0.5)
    if matches:
        return matches[0]

    # Fuzzy match against all registered keys
    all_keys = list(HELP_REGISTRY.keys())
    matches = difflib.get_close_matches(normalized, all_keys, n=1, cutoff=0.5)
    return matches[0] if matches else None


def render_entry(entry: HelpEntry, level: str = "top") -> str:
    """Render a HelpEntry into structured, aligned terminal text."""
    lines: list[str] = []
    lines.append(f"ziro {entry.name} — {entry.summary}")
    lines.append("")
    lines.append("Usage:")
    lines.append(f"  {entry.usage}")

    if entry.subcommands:
        lines.append("")
        lines.append("Subcommands:")
        max_sub = max(len(s) for s in entry.subcommands)
        pad = max(max_sub + 2, 10)
        for sub, desc in entry.subcommands.items():
            lines.append(f"  {sub.ljust(pad)} {desc}")

    if entry.flags:
        lines.append("")
        lines.append("Flags:")
        max_flag = max(len(f[0]) for f in entry.flags)
        pad = max(max_flag + 2, 12)
        for flag, desc in entry.flags:
            lines.append(f"  {flag.ljust(pad)} {desc}")

    if entry.examples:
        lines.append("")
        lines.append("Examples:")
        for ex in entry.examples:
            lines.append(f"  {ex}")

    if entry.related:
        lines.append("")
        lines.append(f"Related: {', '.join(entry.related)}")

    return "\n".join(lines)


def list_all() -> str:
    """Render top-level command summary."""
    lines = [
        "ziro — fast, layered Zsh runtime customization",
        "",
        "Usage:",
        "  ziro <command> [args...]",
        "  ziro [flags]",
        "",
        "Flags:",
        "  -h, --help     Show help information",
        "  -v, --version  Show version",
        "",
        "Commands:",
    ]
    top_entries = [
        ("install", "Install ziro with defaults or custom profile"),
        ("plugin", "Manage plugins (add, remove, list, show)"),
        ("tag", "Manage plugin tags (list, show, add, remove, reset, define)"),
        ("suggest", "Manage auto-suggest component"),
        ("theme", "Manage shell themes and appearance"),
        ("prompt", "Manage shell prompt engine"),
        ("config", "Inspect and manage configuration files"),
        ("doctor", "Diagnose installation health and configuration"),
        ("bench", "Benchmark startup and command performance"),
        ("help", "Show help information for ziro commands"),
    ]
    for cmd, summary in top_entries:
        lines.append(f"  {cmd.ljust(11)} {summary}")

    lines.append("")
    lines.append("Run 'ziro help <command>' or 'ziro <command> --help' for details on a command.")
    lines.append("For more: https://github.com/Pakrohk-DotFiles/ziro-shell")
    return "\n".join(lines)


def cmd_help(argv: list[str] | None = None) -> int:
    """Entry point for `ziro help [cmd]`."""
    args = [a for a in (argv or []) if a not in ("--help", "-h")]
    if not args:
        print(list_all())
        return 0

    target = " ".join(args).strip()
    entry = get_entry(target)
    if entry is not None:
        print(render_entry(entry))
        return 0

    # If composite command, check if parent exists (fallback)
    parts = target.split()
    if len(parts) > 1 and parts[0] in HELP_REGISTRY:
        parent_entry = HELP_REGISTRY[parts[0]]
        print(render_entry(parent_entry))
        return 0

    suggestion = suggest_similar(target)
    print(f"ziro: unknown command or topic '{target}'", file=sys.stderr)
    if suggestion:
        print(f"Did you mean: ziro {suggestion}?", file=sys.stderr)
    print("Run 'ziro help' to view all available commands.", file=sys.stderr)
    return 1


def handle_help_if_requested(
    argv: list[str] | None,
    command_name: str,
    subcommand: str | None = None,
) -> int | None:
    """Helper for core/*_cli.py modules to intercept --help and -h flags."""
    args = argv or []
    if "--help" not in args and "-h" not in args:
        return None

    if subcommand:
        target = f"{command_name} {subcommand}"
    else:
        rest = [a for a in args if a not in ("--help", "-h") and not a.startswith("-")]
        if rest:
            target = f"{command_name} {' '.join(rest)}"
        else:
            target = command_name

    if get_entry(target) is None and get_entry(command_name) is not None:
        target = command_name

    return cmd_help([target])


__all__ = [
    "HelpEntry",
    "HELP_REGISTRY",
    "get_entry",
    "suggest_similar",
    "render_entry",
    "list_all",
    "cmd_help",
    "handle_help_if_requested",
]
