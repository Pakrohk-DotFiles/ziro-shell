"""Doctor: verify Ziro installation health."""

import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from . import gitops, ui


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    warn: bool = False


def doctor() -> int:
    home = Path(os.path.expanduser("~"))
    config_dir = _resolve_config_dir(home)
    checks: list[Check] = []

    checks.append(_check_zsh())
    checks.append(_check_git())
    checks.append(_check_python3())
    checks.append(_check_fzf())
    checks.append(_check_starship())
    checks.append(_check_gh())
    checks.append(_check_config_dir(config_dir))
    checks.append(_check_zshrc_symlink(config_dir))
    checks.append(_check_default_shell())
    checks.append(_check_znap(config_dir))
    checks.append(_check_plugins(config_dir))
    checks.append(_check_remote_origin(config_dir))
    checks.append(_check_zshrc_local(config_dir))
    checks.append(_check_starship_toml())

    ui.section("Doctor results")
    failures = 0
    warnings = 0
    for c in checks:
        if c.ok:
            ui.success(f"{c.name}: {c.detail}")
        elif c.warn:
            ui.warn(f"{c.name}: {c.detail}")
            warnings += 1
        else:
            ui.failed(f"{c.name}: {c.detail}")
            failures += 1

    if failures == 0 and warnings == 0:
        ui.info("All checks passed.")
    else:
        parts = []
        if failures:
            parts.append(f"{failures} failure(s)")
        if warnings:
            parts.append(f"{warnings} warning(s)")
        ui.warn(f"{' and '.join(parts)}")

    return 1 if failures else 0


def _resolve_config_dir(home: Path) -> Path:
    """The Ziro config dir is the repository itself.

    Prefer the user's installed locations (~/.ziro, ~/.zsh_config), then
    the directory this engine lives in (covers running from a checkout).
    """
    new = home / gitops.NEW_DIR
    if gitops.is_repo(new):
        return new
    legacy = home / gitops.LEGACY_DIR
    if gitops.is_repo(legacy):
        return legacy
    repo_root = Path(__file__).resolve().parent.parent
    if gitops.is_repo(repo_root):
        return repo_root
    return new


# ── checks ───────────────────────────────────────────────────────────────────

def _check_zsh() -> Check:
    p = shutil.which("zsh")
    if not p:
        return Check("zsh", False, "not found in PATH")
    return Check("zsh", True, f"{p}")


def _check_git() -> Check:
    p = shutil.which("git")
    if not p:
        return Check("git", False, "not found in PATH")
    return Check("git", True, f"{p}")


def _check_python3() -> Check:
    p = shutil.which("python3")
    if not p:
        return Check("python3", False, "not found in PATH")
    return Check("python3", True, f"{sys.version.split()[0]}")


def _check_fzf() -> Check:
    p = shutil.which("fzf")
    if p:
        return Check("fzf", True, "installed")
    return Check("fzf", False, "not found (pf/cdf unavailable)", warn=True)


def _check_starship() -> Check:
    p = shutil.which("starship")
    if p:
        return Check("starship", True, "installed")
    return Check("starship", False, "not found (prompt unavailable)", warn=True)


def _check_gh() -> Check:
    p = shutil.which("gh")
    if p:
        return Check("gh", True, "installed (GitHub integration available)")
    return Check("gh", True, "not installed (optional)")


def _check_config_dir(config_dir: Path) -> Check:
    if config_dir.name == gitops.LEGACY_DIR:
        return Check("config dir", False,
                      f"{config_dir} (legacy path; re-run 'ziro install' to migrate)")
    if gitops.is_repo(config_dir):
        return Check("config dir", True, str(config_dir))
    return Check("config dir", False, f"{config_dir} (not a valid Ziro repository)")


def _check_zshrc_symlink(config_dir: Path) -> Check:
    zshrc = Path(os.path.expanduser("~")) / ".zshrc"
    if zshrc.is_symlink() and os.readlink(zshrc) == str(config_dir / ".zshrc"):
        return Check("~/.zshrc symlink", True, "correct")
    if zshrc.exists():
        return Check("~/.zshrc symlink", False,
                      f"{zshrc} is not a symlink to the Ziro config")
    return Check("~/.zshrc symlink", False, "~/.zshrc does not exist")


def _check_default_shell() -> Check:
    current = os.environ.get("SHELL", "")
    if os.path.basename(current) == "zsh":
        return Check("default shell", True, "zsh")
    return Check("default shell", False,
                 f"{current or 'unknown'} (expected zsh)")


def _check_znap(config_dir: Path) -> Check:
    znap = config_dir / "znap" / "znap.zsh"
    if znap.is_file():
        return Check("znap", True, f"{znap}")
    return Check("znap", False, "znap not found")


def _check_plugins(config_dir: Path) -> Check:
    expected = {
        "fast-syntax-highlighting": config_dir / "zdharma-continuum" / "fast-syntax-highlighting",
        "zsh-autosuggestions": config_dir / "zsh-users" / "zsh-autosuggestions",
        "zsh-completions": config_dir / "zsh-users" / "zsh-completions",
    }
    missing = [name for name, path in expected.items() if not path.is_dir()]
    if missing:
        return Check("plugins", False,
                      f"missing: {', '.join(missing)} (run 'znap pull' to fetch)", warn=True)
    return Check("plugins", True, "all core plugins present")


def _check_remote_origin(config_dir: Path) -> Check:
    url = gitops.remote_origin_url(config_dir)
    kind = gitops.origin_kind(config_dir)
    if kind == "current":
        return Check("remote origin", True, url)
    if kind == "legacy":
        return Check("remote origin", True,
                     f"{url} (repo renamed; will auto-heal on next update)")
    return Check("remote origin", False,
                 f"{url or 'unknown'} (expected origin containing {gitops.REMOTE_HINT})")


def _check_zshrc_local(config_dir: Path) -> Check:
    local = config_dir / ".zshrc.local"
    if local.is_file():
        return Check(".zshrc.local", True, "present (user-owned; preserved)")
    return Check(".zshrc.local", True, "not present (optional)", warn=True)


def _check_starship_toml() -> Check:
    from . import theme  # noqa: PLC0415
    conf = Path(os.path.expanduser("~")) / ".config" / "starship.toml"
    if conf.is_file():
        if theme.is_managed(conf):
            return Check("starship.toml", True, "managed by ziro theme system")
        return Check("starship.toml", True, "present (user-owned)")
    return Check("starship.toml", True, "not present (will be created on first run)", warn=True)
