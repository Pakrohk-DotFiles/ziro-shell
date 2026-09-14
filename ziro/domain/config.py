"""Language/feature selections and .zshrc.local handling. Pure logic, no I/O."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Selection:
    attr: str
    label: str
    env_key: str
    default_desktop: bool
    is_language: bool


LANG_OPTIONS = (
    Selection("enable_python", "Python", "ENABLE_PYTHON", False, True),
    Selection("enable_rust", "Rust", "ENABLE_RUST", False, True),
    Selection("enable_go", "Go", "ENABLE_GO", False, True),
    Selection("enable_node", "Node.js", "ENABLE_NODE", False, True),
)

SHELL_OPTIONS = (
    Selection("enable_zcolors", "zcolors (shell colors)", "ENABLE_ZCOLORS", True, False),
    Selection("enable_wd", "wd (directory bookmarks)", "ENABLE_WD", True, False),
    Selection("enable_alias_tips", "alias-tips (suggestions)", "ENABLE_ALIAS_TIPS", True, False),
    Selection("enable_z", "z (smart cd)", "ENABLE_Z", True, False),
    Selection("enable_pf", "pf (fzf package manager)", "ENABLE_PF", True, False),
    Selection("enable_ssh_agent", "SSH agent (auto-load keys)", "ENABLE_SSH_AGENT", True, False),
    Selection("enable_update_check", "Background update check", "ENABLE_UPDATE_CHECK", True, False),
    Selection("enable_nmap", "nmap completions (server)", "ENABLE_NMAP", False, False),
)

MANAGED_CONFIGS = ("zshrc", "zimrc", "zpreztorc", "zprofile", "zshenv")
MANAGED_FRAMEWORKS = (".oh-my-zsh", ".zim", ".zprezto")

SELECTION_BY_ATTR: dict[str, Selection] = {s.attr: s for s in LANG_OPTIONS + SHELL_OPTIONS}
SELECTION_BY_KEY: dict[str, Selection] = {s.env_key: s for s in LANG_OPTIONS + SHELL_OPTIONS}

_ALL_ENV_KEYS = frozenset(SELECTION_BY_KEY)

_LEGACY_LINES = (
    "znap fpath _rustup 'rustup completions zsh'",
    "znap fpath _cargo 'rustup completions zsh cargo'",
)

_ENV_LINE_RE = re.compile(
    r"""^\s*(?:export\s+)?(ENABLE_[A-Z_]+)\s*=\s*['"]?(yes|no|true|false|1|0)['"]?\s*$""",
    re.I,
)


def _to_bool(value: str) -> bool:
    return value.lower() in ("yes", "true", "1")


def _to_str(value: bool) -> str:
    return "yes" if value else "no"


def strip_legacy_lines(text: str) -> str:
    lines = text.splitlines()
    kept = [line for line in lines if line.strip() not in _LEGACY_LINES]
    return "\n".join(kept) + ("\n" if text.endswith("\n") else "")


def extract_env_from_zshrc_local(text: str) -> dict[str, bool]:
    result: dict[str, bool] = {}
    for line in text.splitlines():
        m = _ENV_LINE_RE.match(line)
        if m and m.group(1) in _ALL_ENV_KEYS:
            result[m.group(1)] = _to_bool(m.group(2))
    return result


def _filter_non_managed_lines(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        key = stripped.removeprefix("export ").split("=")[0].strip()
        if key in _ALL_ENV_KEYS:
            continue
        if stripped in _LEGACY_LINES:
            continue
        lines.append(line)
    return lines


def render_zshrc_local(existing_text: str, selections: dict[str, str]) -> str:
    """Merge ENABLE_* values into .zshrc.local text, preserving everything else.

    Values already present in the user's file win over new selections, so a
    manually edited .zshrc.local is never clobbered by a reinstall.
    """
    kept = _filter_non_managed_lines(existing_text)
    existing = extract_env_from_zshrc_local(existing_text)
    merged = {
        key: ("yes" if val else "no") for key, val in existing.items()
    }
    merged.update(
        {k: v for k, v in selections.items() if k not in existing}
    )

    def line_for(s: Selection) -> str:
        return f"export {s.env_key}='{merged.get(s.env_key, 'no')}'"

    lines = [
        *kept,
        "# Language tooling (set by ziro install; edit freely)",
        *[line_for(s) for s in LANG_OPTIONS],
        "",
        "# Shell features (set by ziro install; edit freely)",
        *[line_for(s) for s in SHELL_OPTIONS],
    ]
    return "\n".join(lines) + "\n"


def append_to_zshrc_local(text: str, block: str) -> str:
    base = text.rstrip("\n") + "\n" if text else ""
    return base + block


def patch_zsh_config_dir(text: str, old: str = ".zsh_config", new: str = ".ziro") -> str:
    return (
        text.replace(f"ZSH_CONFIG_DIR=~/{old}", f"ZSH_CONFIG_DIR=~/{new}")
        .replace(f"ZSH_CONFIG_DIR=$HOME/{old}", f"ZSH_CONFIG_DIR=$HOME/{new}")
    )
