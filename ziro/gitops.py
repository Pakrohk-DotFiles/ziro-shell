"""Git/GitHub operations: clone, pull, migrate, remote checks.

Repo layout note: plugin directories (znap, zsh-users, ...) are
znap-managed clones listed in .gitignore - never touched by git ops here.
"""

import os
import shutil
import tempfile
import time
from pathlib import Path

from . import ui
from .runner import capture, quiet, run

REPO_URL = "https://github.com/Pakrohk-DotFiles/ziro-shell.git"
REMOTE_HINT = "Pakrohk-DotFiles/ziro-shell"
# Repos installed before the rename still point at these; accepted as Ziro,
# and healed (re-pointed) automatically on update.
LEGACY_REMOTE_HINTS = (
    "Pakrohk-DotFiles/zsh_config",      # pre-rename origin
    "Pakrohk-DotFiles/ziro",            # even older name
)
NEW_DIR = ".ziro"          # under HOME
LEGACY_DIR = ".zsh_config"  # under HOME


def git_available() -> bool:
    return shutil.which("git") is not None


def gh_available() -> bool:
    return shutil.which("gh") is not None


def is_repo(path: Path) -> bool:
    return (path / ".git").exists()


def remote_origin_url(path: Path) -> str | None:
    if not is_repo(path):
        return None
    return capture(["git", "-C", str(path), "remote", "get-url", "origin"], check=False) or None


def is_ziro_repo(path: Path) -> bool:
    return origin_kind(path) is not None


def origin_kind(path: Path) -> str | None:
    """Classify origin: 'current', 'legacy', or None (not a Ziro repo)."""
    url = remote_origin_url(path)
    if not url:
        return None
    if REMOTE_HINT in url:
        return "current"
    if any(hint in url for hint in LEGACY_REMOTE_HINTS):
        return "legacy"
    return None


def heal_origin(path: Path) -> bool:
    """Re-point a pre-rename origin at the current repo URL.

    True if the origin was healed (or already current).
    """
    if origin_kind(path) == "current":
        return True
    if origin_kind(path) != "legacy":
        return False
    run(["git", "-C", str(path), "remote", "set-url", "origin", REPO_URL])
    ui.configured("origin -> Pakrohk-DotFiles/ziro-shell (repo was renamed)")
    return True


def has_uncommitted_changes(path: Path) -> bool:
    return bool(capture(["git", "-C", str(path), "status", "--porcelain"], check=False))


def stash(path: Path) -> bool:
    """Stash local changes; True if a stash was created."""
    if not has_uncommitted_changes(path):
        return False
    run(["git", "-C", str(path), "stash", "-q", "-m",
         f"ziro auto-stash before update on {time.strftime('%Y-%m-%d %H:%M:%S')}"])
    return True


def stash_pop(path: Path) -> bool:
    """Pop latest stash; True on success."""
    return quiet(["git", "-C", str(path), "stash", "pop", "-q"])


def clone(url: str, dest: Path, depth: int | None = None) -> None:
    cmd = ["git", "clone"]
    if depth:
        cmd += ["--depth", str(depth)]
    cmd += [url, str(dest)]
    run(cmd)


def pull_ff_only(path: Path) -> bool:
    return quiet(["git", "-C", str(path), "pull", "--ff-only"])


def untrack_zshrc_local(path: Path) -> bool:
    """Stop tracking .zshrc.local if an old repo version still tracks it.

    The file is machine-local; it shipped tracked by mistake. Untracking
    keeps the user's on-disk copy intact. True if untracked now.
    """
    if not is_repo(path):
        return False
    tracked = quiet(["git", "-C", str(path), "ls-files", "--error", "--", ".zshrc.local"])
    if not tracked:
        return True
    run(["git", "-C", str(path), "rm", "--cached", "-q", "--", ".zshrc.local"])
    ui.configured(".zshrc.local untracked (machine-local file; your copy is untouched)")
    return True


def fetch(path: Path, ref: str = "origin main") -> bool:
    return quiet(["git", "-C", str(path), "fetch", "-q"] + ref.split())


def head_and_remote(path: Path) -> tuple[str, str]:
    head = capture(["git", "-C", str(path), "rev-parse", "HEAD"], check=False)
    remote = capture(["git", "-C", str(path), "rev-parse", "@{u}"], check=False)
    return head, remote


def ensure_znap(config_dir: Path, dry_run: bool = False) -> bool:
    """Bootstrap znap (shallow clone) if missing. True if present after call."""
    znap = config_dir / "znap" / "znap.zsh"
    if znap.is_file():
        return True
    if dry_run:
        ui.info(f"Would bootstrap znap into {config_dir / 'znap'}")
        return False
    ui.info("Bootstrapping znap...")
    target = config_dir / "znap"
    if target.exists():
        shutil.rmtree(target)
    clone("https://github.com/marlonrichert/zsh-snap.git", target, depth=1)
    return True


def migrate_legacy(home: Path, dry_run: bool = False) -> tuple[Path, bool]:
    """Move legacy ~/.zsh_config to ~/.ziro.

    Returns (config_dir_used, migrated).
    Handles: legacy exists + new missing -> mv;
             both exist -> keep new, leave legacy untouched;
             failure -> fall back to legacy path.
    Never blindly removes anything.
    """
    new = home / NEW_DIR
    legacy = home / LEGACY_DIR
    new_is_repo = is_repo(new)
    legacy_is_repo = is_repo(legacy)

    if legacy_is_repo and not new.exists():
        if dry_run:
            ui.info(f"Would migrate {legacy} -> {new}")
            return legacy, False
        ui.info(f"Found legacy install at {legacy}")
        try:
            os.rename(legacy, new)
            ui.success(f"Migrated {legacy} -> {new}")
            return new, True
        except OSError as exc:
            ui.failed(f"migration rename: {exc}")
            ui.warn("Continuing with legacy path")
            return legacy, False

    if legacy_is_repo and new_is_repo:
        ui.warn(f"Both {new} and {legacy} exist; using {new} and leaving legacy untouched")
        return new, False

    if new.exists() and not new_is_repo:
        ui.error(f"{new} already exists and is not a Ziro repository.")
        ui.warn("Move it away or inspect it manually; refusing to overwrite user data.")
        raise MigrationBlocked(str(new))

    return new, False


class MigrationBlocked(Exception):
    """Target location exists but is not a Ziro repository (user data)."""


def backup_path_for(name: str) -> Path:
    """Timestamped backup path (used for user config backups)."""
    suffix = time.strftime(".bak.%Y%m%d%H%M%S")
    return Path(tempfile.gettempdir()) / f"{name}{suffix}"
