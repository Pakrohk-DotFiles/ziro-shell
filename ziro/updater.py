"""Update flow: stash -> pull --ff-only -> pop -> recompile -> refresh
update-check state."""

import os
import time
from pathlib import Path

from . import gitops, ui
from .runner import RunError, report_failure

LAST_CHECK_FILE = ".last_update_check"


def update() -> int:
    home = Path(os.path.expanduser("~"))
    # Prefer the user's installed locations; fall back to the repo this
    # engine lives in (covers running from a checkout).
    if gitops.is_repo(home / gitops.NEW_DIR):
        config_dir = home / gitops.NEW_DIR
    elif gitops.is_repo(home / gitops.LEGACY_DIR):
        config_dir = home / gitops.LEGACY_DIR
    else:
        repo_root = Path(__file__).resolve().parent.parent
        if gitops.is_repo(repo_root) and gitops.is_ziro_repo(repo_root):
            config_dir = repo_root
        else:
            ui.error("No Ziro repository found. Run 'ziro install' first.")
            return 1

    if not gitops.is_ziro_repo(config_dir):
        ui.warn(f"Origin of {config_dir} is not the Ziro repository; refusing to update.")
        return 1

    ui.info("Updating Ziro...")
    try:
        stashed = gitops.stash(config_dir)
        if stashed:
            ui.warn("Local changes detected. Stashing them temporarily...")

        ui.info("Pulling latest updates from repository...")
        if gitops.pull_ff_only(config_dir):
            ui.updated("Ziro repository")

            if stashed:
                ui.info("Re-applying your local changes...")
                if gitops.stash_pop(config_dir):
                    ui.success("Local changes restored")
                else:
                    ui.error("Merge conflict when applying your local changes.")
                    ui.warn(f"Please review and resolve conflicts in: {config_dir}")
        else:
            ui.error("Failed to pull Ziro. Check your internet connection.")
            if stashed:
                ui.info("Restoring your local changes...")
                gitops.stash_pop(config_dir)
            return 1

        _recompile(config_dir)
        _refresh_check_state(config_dir)
    except RunError as exc:
        report_failure(exc)
        if stashed:
            ui.warn("Restoring your stashed local changes...")
            gitops.stash_pop(config_dir)
        return 1

    ui.success("Update complete. Please reload your shell with: source ~/.zshrc")
    return 0


def _recompile(config_dir: Path) -> None:
    ui.info("Compiling configurations for maximum speed...")
    from .installer import ZSH_COMPILE_TARGETS, _final_compile, Options  # noqa: PLC0415
    opts = Options()
    _final_compile(opts, config_dir)


def _refresh_check_state(config_dir: Path) -> None:
    """Write fresh timestamp so the background notifier's cooldown restarts
    after a real update."""
    stamp = config_dir / LAST_CHECK_FILE
    try:
        stamp.write_text(f"{int(time.time())}\n")
    except OSError:
        pass
