"""Update flow: stash -> pull --ff-only -> pop -> recompile -> refresh
update-check state."""

import os
import subprocess
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
    gitops.heal_origin(config_dir)

    ui.info("Updating Ziro...")
    try:
        stashed = gitops.stash(config_dir)
        if stashed:
            ui.warn("Local changes detected. Stashing them temporarily...")

        ui.info("Pulling latest updates from repository...")
        if gitops.pull_ff_only(config_dir):
            ui.updated("Ziro repository")
            gitops.untrack_zshrc_local(config_dir)

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

        _ensure_plugins(config_dir)
        _recompile(config_dir)
        _heal_cli(config_dir)
        _ensure_path()
        _ensure_theme(config_dir)
        ok = _verify_after_update()
        _refresh_check_state(config_dir)
    except RunError as exc:
        report_failure(exc)
        if stashed:
            ui.warn("Restoring your stashed local changes...")
            gitops.stash_pop(config_dir)
        return 1

    if not ok:
        ui.error("Update completed but verification failed. Run 'ziro doctor'.")
        return 1
    ui.success("Update complete. Reload your shell with: exec zsh -l")
    return 0


def _recompile(config_dir: Path) -> None:
    ui.info("Compiling configurations for maximum speed...")
    from .installer import _final_compile, Options  # noqa: PLC0415
    opts = Options()
    _final_compile(opts, config_dir)


def _znap_plugin_dirs(config_dir: Path) -> list[Path]:
    """Git clones znap created inside the config dir (owner/repo layout)."""
    dirs: list[Path] = []
    for child in config_dir.iterdir():
        if not child.is_dir() or child.name.startswith((".", "_")) or child.name == "ziro":
            continue
        if (child / ".git").exists():
            dirs.append(child)
        else:
            for sub in child.iterdir():
                if sub.is_dir() and (sub / ".git").exists():
                    dirs.append(sub)
    return sorted(dirs)


def _plugin_up_to_date(plugin: Path) -> bool:
    proc = subprocess.run(["git", "pull", "--ff-only"], cwd=plugin,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc.returncode == 0


def _ensure_plugins(config_dir: Path) -> None:
    """Update znap-managed plugin clones; the repo pull only covers dotfiles."""
    ui.section("Updating plugins")
    updated, failed = 0, []
    for plugin in _znap_plugin_dirs(config_dir):
        if _plugin_up_to_date(plugin):
            updated += 1
        else:
            failed.append(plugin.relative_to(config_dir).as_posix())
    ui.success(f"{updated} plugin(s) up to date")
    for name in failed:
        ui.warn(f"could not update plugin '{name}' (local divergence? re-clone: rm -rf {config_dir / name} && exec zsh -l)")


def _heal_cli(config_dir: Path) -> None:
    """Point ~/.local/bin/ziro at the current repo (fixes stale legacy links)."""
    ui.section("CLI link")
    from .installer import Options, _install_cli  # noqa: PLC0415
    _install_cli(Options(), config_dir)


def _ensure_path() -> None:
    ui.section("PATH")
    from .installer import _ensure_local_bin_on_path  # noqa: PLC0415
    _ensure_local_bin_on_path(False)


def _ensure_theme(config_dir: Path) -> None:
    """Refresh an unmodified managed theme file; user edits are preserved."""
    ui.section("Prompt theme")
    from .installer import Options, _install_starship_config  # noqa: PLC0415
    _install_starship_config(Options(), config_dir)


def _verify_after_update() -> bool:
    """Focused post-update check: the user must be able to run `ziro`.

    Full health is `ziro doctor`'s job; here we only gate on the CLI being
    resolvable in a fresh interactive shell (the real-world breakage)."""
    ui.section("Verifying update")
    cli = Path(os.path.expanduser("~")) / ".local" / "bin" / "ziro"
    if cli.is_file() or cli.is_symlink():
        proc = subprocess.run([str(cli), "--version"], capture_output=True, text=True)
        if proc.returncode == 0:
            ui.success(f"ziro CLI works ({proc.stdout.strip()})")
        else:
            ui.warn("ziro CLI present but 'ziro --version' failed")
            return False
    else:
        ui.warn("ziro CLI missing at ~/.local/bin/ziro (re-run 'ziro install')")
        return False
    # interactive zsh paints its prompt on stdout; substring-match the resolved path
    shell = subprocess.run(["zsh", "-ic", "command -v ziro"],
                           capture_output=True, text=True)
    if ".local/bin/ziro" not in shell.stdout:
        ui.warn("`ziro` is not reachable in a fresh interactive shell; check PATH (~/.zshenv).")
        return False
    ui.success("Update verification passed")
    return True


def _refresh_check_state(config_dir: Path) -> None:
    """Write fresh timestamp so the background notifier's cooldown restarts
    after a real update."""
    stamp = config_dir / LAST_CHECK_FILE
    try:
        stamp.write_text(f"{int(time.time())}\n")
    except OSError:
        pass
