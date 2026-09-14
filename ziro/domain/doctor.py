"""Doctor check models. Pure logic, no I/O."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str
    warn: bool = False


def check_zsh(which_zsh: str | None) -> Check:
    if which_zsh:
        return Check("zsh", True, which_zsh)
    return Check("zsh", False, "not found in PATH")


def check_git(which_git: str | None) -> Check:
    if which_git:
        return Check("git", True, which_git)
    return Check("git", False, "not found in PATH")


def check_python3(which_python3: str | None, version: str = "") -> Check:
    if which_python3:
        return Check("python3", True, version or which_python3)
    return Check("python3", False, "not found in PATH")


def check_fzf(which_fzf: str | None) -> Check:
    if which_fzf:
        return Check("fzf", True, "installed")
    return Check("fzf", False, "not found (pf/cdf unavailable)", warn=True)


def check_starship(which_starship: str | None) -> Check:
    if which_starship:
        return Check("starship", True, "installed")
    return Check("starship", False, "not found (prompt unavailable)", warn=True)


def check_gh(which_gh: str | None) -> Check:
    if which_gh:
        return Check("gh", True, "installed (GitHub integration available)")
    return Check("gh", True, "not installed (optional)")


def check_config_dir(config_dir: Path, is_repo: bool, legacy_dir: str) -> Check:
    if config_dir.name == legacy_dir:
        return Check("config dir", False, f"{config_dir} (legacy path; re-run 'ziro install' to migrate)")
    if is_repo:
        return Check("config dir", True, str(config_dir))
    return Check("config dir", False, f"{config_dir} (not a valid Ziro repository)")


def check_zshrc_symlink(zshrc: Path, config_dir: Path, is_symlink: bool, readlink_target: str | None) -> Check:
    expected = str(config_dir / ".zshrc")
    if is_symlink and readlink_target == expected:
        return Check("~/.zshrc symlink", True, "correct")
    if zshrc.exists():
        return Check("~/.zshrc symlink", False, f"{zshrc} is not a symlink to the Ziro config")
    return Check("~/.zshrc symlink", False, "~/.zshrc does not exist")


def check_default_shell(current_shell: str) -> Check:
    import os
    if os.path.basename(current_shell) == "zsh":
        return Check("default shell", True, "zsh")
    return Check("default shell", False, f"{current_shell or 'unknown'} (expected zsh)")


def check_znap(config_dir: Path, has_znap: bool) -> Check:
    znap = config_dir / "znap" / "znap.zsh"
    if has_znap:
        return Check("znap", True, str(znap))
    return Check("znap", False, "znap not found")


def check_plugins(config_dir: Path, existing: list[str] | None = None) -> Check:
    expected_names = ["fast-syntax-highlighting", "zsh-autosuggestions", "zsh-completions"]
    if existing is None:
        existing = expected_names
    missing = [n for n in expected_names if n not in existing]
    if missing:
        return Check("plugins", False, f"missing: {', '.join(missing)} (run 'znap pull' to fetch)", warn=True)
    return Check("plugins", True, "all core plugins present")


def check_remote_origin(origin_url: str | None, origin_kind: str | None, remote_hint: str) -> Check:
    if origin_kind == "current":
        return Check("remote origin", True, origin_url or "")
    if origin_kind == "legacy":
        return Check("remote origin", True, f"{origin_url} (repo renamed; will auto-heal on next update)")
    return Check("remote origin", False, f"{origin_url or 'unknown'} (expected origin containing {remote_hint})")


def check_zshrc_local(config_dir: Path, has_local: bool) -> Check:
    if has_local:
        return Check(".zshrc.local", True, "present (user-owned; preserved)")
    return Check(".zshrc.local", True, "not present (optional)", warn=True)


def check_starship_toml(has_starship: bool) -> Check:
    if has_starship:
        return Check("starship.toml", True, "present (user-owned; preserved)")
    return Check("starship.toml", True, "not present (will be created on first install)", warn=True)
