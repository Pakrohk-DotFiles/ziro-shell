"""Install flow: deps -> sync/migrate -> backup -> link -> .zshrc.local
-> chsh -> znap compile -> verify -> getting-started."""

import contextlib
import os
import shutil
import sys
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from . import gitops, packages, platform as platform_mod, themes, ui
from .runner import RunError, capture, quiet, report_failure, run, sudo_prefix

MANAGED_CONFIGS = ["zshrc", "zimrc", "zpreztorc", "zprofile", "zshenv"]
MANAGED_FRAMEWORKS = [".oh-my-zsh", ".zim", ".zprezto"]

ZSH_COMPILE_TARGETS = [
    ".zshrc", ".zsh_aliases", ".zsh_update.zsh", ".paru_fzf.zsh", ".prompt.local",
    "znap", "zsh-users", "zdharma-continuum", "mfaerevaag", "djui", "rupa",
    "ohmyzsh", "marlonrichert",
]


@dataclass
class Options:
    mode: str | None = None            # Desktop / Server (None = auto)
    skip_deps: bool = False
    skip_shell: bool = False
    force: bool = False
    dry_run: bool = False
    non_interactive: bool = False
    enable_python: bool | None = None  # None = ask interactively
    enable_rust: bool | None = None
    enable_go: bool | None = None
    enable_node: bool | None = None
    # Shell features
    enable_zcolors: bool | None = None
    enable_wd: bool | None = None
    enable_alias_tips: bool | None = None
    enable_z: bool | None = None
    enable_pf: bool | None = None
    enable_ssh_agent: bool | None = None
    enable_update_check: bool | None = None
    enable_nmap: bool | None = None


LANG_PROMPTS = [
    ("enable_python", "Python", "--with-python/--no-python", "ENABLE_PYTHON"),
    ("enable_rust", "Rust", "--with-rust/--no-rust", "ENABLE_RUST"),
    ("enable_go", "Go", "--with-go/--no-go", "ENABLE_GO"),
    ("enable_node", "Node.js", "--with-node/--no-node", "ENABLE_NODE"),
]

# (attr, label, env_key, desktop_default)
FEATURE_PROMPTS = [
    ("enable_zcolors", "zcolors (shell colors)", "ENABLE_ZCOLORS", True),
    ("enable_wd", "wd (directory bookmarks)", "ENABLE_WD", True),
    ("enable_alias_tips", "alias-tips (suggestions)", "ENABLE_ALIAS_TIPS", True),
    ("enable_z", "z (smart cd)", "ENABLE_Z", True),
    ("enable_pf", "pf (fzf package manager)", "ENABLE_PF", True),
    ("enable_ssh_agent", "SSH agent (auto-load keys)", "ENABLE_SSH_AGENT", True),
    ("enable_update_check", "Background update check", "ENABLE_UPDATE_CHECK", True),
    ("enable_nmap", "nmap completions (server)", "ENABLE_NMAP", False),
]


def _resolve_language_flags(opts: Options) -> dict[str, str]:
    """Ask about unset language tooling (None). Returns env values to persist.

    Default is OFF for every language; --non-interactive also turns them all
    off. Explicit flags and existing .zshrc.local values win over prompts.
    """
    values: dict[str, str] = {}

    ui.section("Language tooling")
    ui.info("Enable only what you use; easy to turn on later in .zshrc.local")
    for attr, label, flags, env_key in LANG_PROMPTS:
        val = getattr(opts, attr)
        if val is None and opts.non_interactive:
            val = False
        if val is None:
            val = ui.confirm(f"Use {label}?", default_yes=False)
            setattr(opts, attr, val)
        values[env_key] = "yes" if val else "no"

    for attr, label, flags, env_key in LANG_PROMPTS:
        val = getattr(opts, attr)
        note = "" if val else f" (enable later: {env_key}=yes in .zshrc.local)"
        ui.info(f"{label}: {'yes' if val else 'no'}{note}")
    return values


def _resolve_feature_flags(opts: Options) -> dict[str, str]:
    """Ask about shell features (ssh-agent, zcolors, etc.).

    Default is the desktop_default column; Server mode flips all to no.
    --non-interactive uses the mode-aware default.
    """
    values: dict[str, str] = {}

    ui.section("Shell features")
    ui.info("Enable features you want; easy to toggle later in .zshrc.local")
    for attr, label, env_key, desktop_default in FEATURE_PROMPTS:
        val = getattr(opts, attr)
        if val is None:
            default = desktop_default if opts.mode != "Server" else False
            if opts.non_interactive:
                val = default
            else:
                val = ui.confirm(f"  {label}?", default_yes=default)
            setattr(opts, attr, val)
        values[env_key] = "yes" if val else "no"

    for attr, label, env_key, desktop_default in FEATURE_PROMPTS:
        val = getattr(opts, attr)
        note = "" if val else f" (enable later: {env_key}=yes in .zshrc.local)"
        ui.info(f"  {label}: {'yes' if val else 'no'}{note}")
    return values


def _persist_language_flags(config_dir: Path, values: dict[str, str]) -> None:
    """Merge ENABLE_* values into the user's .zshrc.local, preserving everything else.

    Also strips legacy unguarded ``znap fpath`` rustup/cargo lines that
    were shipped in older .zshrc.local files — they cause
    ``command not found: rustup`` on every shell start when Rust is disabled.
    """
    local = config_dir / ".zshrc.local"
    _ALL_ENABLE_KEYS = {
        "ENABLE_PYTHON", "ENABLE_RUST", "ENABLE_GO", "ENABLE_NODE",
        "ENABLE_ZCOLORS", "ENABLE_WD", "ENABLE_ALIAS_TIPS", "ENABLE_Z",
        "ENABLE_PF", "ENABLE_SSH_AGENT", "ENABLE_UPDATE_CHECK", "ENABLE_NMAP",
    }
    _LEGACY_STRIP = (
        "znap fpath _rustup 'rustup completions zsh'",
        "znap fpath _cargo 'rustup completions zsh cargo'",
    )
    lines = []
    if local.is_file():
        for line in local.read_text(encoding="utf-8", errors="replace").splitlines():
            key = line.strip().removeprefix("export ").split("=")[0].strip()
            if key in _ALL_ENABLE_KEYS:
                continue
            if line.strip() in _LEGACY_STRIP:
                continue
            lines.append(line)
    lines += [
        "# Language tooling (set by ziro install; edit freely)",
        f"export ENABLE_PYTHON='{values.get('ENABLE_PYTHON', 'no')}'",
        f"export ENABLE_RUST='{values.get('ENABLE_RUST', 'no')}'",
        f"export ENABLE_GO='{values.get('ENABLE_GO', 'no')}'",
        f"export ENABLE_NODE='{values.get('ENABLE_NODE', 'no')}'",
        "",
        "# Shell features (set by ziro install; edit freely)",
        f"export ENABLE_ZCOLORS='{values.get('ENABLE_ZCOLORS', 'no')}'",
        f"export ENABLE_WD='{values.get('ENABLE_WD', 'no')}'",
        f"export ENABLE_ALIAS_TIPS='{values.get('ENABLE_ALIAS_TIPS', 'no')}'",
        f"export ENABLE_Z='{values.get('ENABLE_Z', 'no')}'",
        f"export ENABLE_PF='{values.get('ENABLE_PF', 'no')}'",
        f"export ENABLE_SSH_AGENT='{values.get('ENABLE_SSH_AGENT', 'no')}'",
        f"export ENABLE_UPDATE_CHECK='{values.get('ENABLE_UPDATE_CHECK', 'no')}'",
        f"export ENABLE_NMAP='{values.get('ENABLE_NMAP', 'no')}'",
    ]
    local.write_text("\n".join(lines) + "\n")


def _home() -> Path:
    return Path(os.path.expanduser("~"))


def install(opts: Options) -> int:
    plat = platform_mod.detect()

    # mode default: root -> Server, else Desktop
    if opts.mode is None:
        opts.mode = "Server" if plat.is_root else "Desktop"
    if plat.non_interactive:
        opts.non_interactive = True

    ui.banner()
    ui.info(f"OS detected: {plat.os_name}"
            + (f" ({plat.pkg_mgr})" if plat.pkg_mgr else " (no known package manager)"))
    ui.info(f"Mode: {opts.mode} | Non-interactive: {opts.non_interactive}"
            + (" | DRY RUN" if opts.dry_run else ""))

    if plat.is_root and sys.platform.startswith("darwin"):
        ui.error("Do not run this installer as root on macOS.")
        return 1

    if not opts.non_interactive and not opts.force and not opts.dry_run:
        if not ui.confirm("Proceed with installation?"):
            ui.info("Cancelled")
            return 0

    try:
        lang_values = _resolve_language_flags(opts)
        feature_values = _resolve_feature_flags(opts)
        all_values = {**lang_values, **feature_values}
        if not _install_deps(opts, plat):
            return 1
        try:
            config_dir = _sync_config(opts)
        except gitops.MigrationBlocked as exc:
            ui.error(f"Cannot install into {exc}; resolve it manually.")
            return 1
        if config_dir is None:
            return 1
        _backup_existing(opts)
        if not _link_zshrc(opts, config_dir):
            return 1
        _install_cli(opts, config_dir)
        if not opts.dry_run:
            _persist_language_flags(config_dir, all_values)
        _install_starship_config(opts, config_dir)
        _create_local_config(opts, config_dir)
        _change_shell(opts, plat)
        _final_compile(opts, config_dir)
        _verify_install(opts, config_dir)
    except RunError as exc:
        report_failure(exc)
        ui.error("Installation aborted.")
        return 1
    except KeyboardInterrupt:
        ui.error("Interrupted.")
        return 130

    print(f"\n{ui.GREEN}=========================================={ui.RESET}")
    print(f"{ui.GREEN}   Installation Completed Successfully!   {ui.RESET}")
    print(f"{ui.GREEN}=========================================={ui.RESET}")
    ui.info("Restart your terminal or run: source ~/.zshrc")
    ui.getting_started(getting_started_lines())
    return 0


# ── dependencies ─────────────────────────────────────────────────────────────

def _install_deps(opts: Options, plat: platform_mod.Platform) -> bool:
    if opts.skip_deps:
        ui.skipped("dependency installation (--skip-deps)")
        return True
    if not plat.has_pkg_manager:
        ui.skipped(f"no package manager detected for {plat.os_name}; install deps manually")
        return True

    base, extra = packages.packages_for(
        plat, opts.mode, opts.enable_python, opts.enable_rust, opts.enable_go, opts.enable_node)
    missing = _missing_packages(plat, base)
    missing_extra = _missing_packages(plat, extra)

    if opts.dry_run:
        if missing or missing_extra:
            ui.info(f"Would install: {' '.join(missing + missing_extra)}")
        else:
            ui.info("All packages already present")
        return True

    if plat.os_name == "macOS" and not shutil.which("brew"):
        ui.info("Installing Homebrew (official installer)...")
        # Unavoidable bootstrap: Homebrew's official installer script
        # (piped to bash; the only remote-execution in this project).
        run(["/bin/bash", "-c",
             "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"])
        plat.pkg_mgr, plat.pkg_install = platform_mod._pkg_manager(plat.os_name)  # noqa: SLF001
        if not shutil.which("brew"):
            ui.failed("Homebrew installation")
            return False

    if missing:
        ui.info(f"Installing base packages: {' '.join(missing)}")
        run(sudo_prefix(plat.sudo) + plat.pkg_install + missing)
        ui.installed(f"{len(missing)} base package(s)")
    else:
        ui.present("all base packages")

    if opts.mode == "Desktop" and missing_extra:
        ui.info(f"Installing desktop extras: {' '.join(missing_extra)}")
        run(sudo_prefix(plat.sudo) + plat.pkg_install + missing_extra)
        ui.installed(f"{len(missing_extra)} extra package(s)")

    # Arch Desktop: paru (AUR helper) if missing - build in a private temp dir
    if (plat.os_name == "Arch" and opts.mode == "Desktop"
            and not plat.is_root and not shutil.which("paru")):
        ui.info("Installing paru (AUR helper)...")
        with _temp_dir() as build:
            run(["git", "clone", "https://aur.archlinux.org/paru.git", str(build)])
            run(["makepkg", "-si", "--noconfirm"], cwd=str(build))
        ui.installed("paru")

    ui.success("Dependencies ready")
    return True


@contextlib.contextmanager
def _temp_dir():
    d = Path(tempfile.mkdtemp(prefix="ziro-"))
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _pkg_query_cmd(plat: platform_mod.Platform) -> list[str] | None:
    """Command template that succeeds if a package is installed."""
    return {
        "pacman": ["pacman", "-Qi"],
        "apt": ["dpkg", "-s"],
        "apk": ["apk", "info", "-e"],
        "zypper": ["rpm", "-q"],
    }.get(plat.pkg_mgr)


def _missing_packages(plat: platform_mod.Platform, pkgs: list[str]) -> list[str]:
    if not pkgs:
        return []
    if plat.pkg_mgr == "brew":
        installed_names: set[str] = set()
        for args in (["--formula"], ["--cask"]):
            out = capture(["brew", "list"] + args, check=False)
            installed_names.update(out.split())
        return [p for p in pkgs if p not in installed_names]
    query = _pkg_query_cmd(plat)
    if query is None:
        return pkgs
    missing = []
    for pkg in pkgs:
        if not quiet(query + [pkg]):
            missing.append(pkg)
    return missing


# ── configuration sync ───────────────────────────────────────────────────────

def _sync_config(opts: Options) -> Path | None:
    ui.section("Syncing configuration")
    home = _home()
    config_dir, migrated = gitops.migrate_legacy(home, dry_run=opts.dry_run)

    if gitops.is_repo(config_dir):
        if opts.dry_run:
            ui.info(f"Would pull latest into {config_dir}")
        elif gitops.pull_ff_only(config_dir):
            ui.updated("configuration repository")
            gitops.untrack_zshrc_local(config_dir)
        else:
            ui.warn("git pull failed; using existing copy")
    else:
        if opts.dry_run:
            ui.info(f"Would clone {gitops.REPO_URL} -> {config_dir}")
        else:
            ui.info("Cloning Ziro...")
            gitops.clone(gitops.REPO_URL, config_dir)
            ui.installed(f"Ziro repository at {config_dir}")

    if gitops.ensure_znap(config_dir, dry_run=opts.dry_run):
        ui.present("znap")
    elif not opts.dry_run:
        ui.failed("znap bootstrap")
        return None

    if migrated and not opts.dry_run:
        _relink_after_migration(config_dir)
    return config_dir


def _relink_after_migration(config_dir: Path) -> None:
    """After migration, clean up leftover state and fix runtime paths."""
    home = _home()
    zshrc = home / ".zshrc"
    if zshrc.is_symlink():
        target = os.readlink(zshrc)
        if gitops.LEGACY_DIR in target:
            zshrc.unlink()
            zshrc.symlink_to(config_dir / ".zshrc")
            ui.configured(f"~/.zshrc -> {config_dir / '.zshrc'}")

    # Patch ZSH_CONFIG_DIR in the migrated .zshrc so znap clones into ~/.ziro,
    # not the stale legacy path embedded in the original repo HEAD.
    zshrc_local = config_dir / ".zshrc"
    if zshrc_local.is_file():
        content = zshrc_local.read_text(encoding="utf-8", errors="replace")
        if "ZSH_CONFIG_DIR=~/.zsh_config" in content or "ZSH_CONFIG_DIR=$HOME/.zsh_config" in content:
            content = content.replace("ZSH_CONFIG_DIR=~/.zsh_config", "ZSH_CONFIG_DIR=~/.ziro")
            content = content.replace("ZSH_CONFIG_DIR=$HOME/.zsh_config", "ZSH_CONFIG_DIR=$HOME/.ziro")
            zshrc_local.write_text(content, encoding="utf-8")
            ui.configured(f"ZSH_CONFIG_DIR → ~/.ziro in {zshrc_local}")


# ── backup / link / local config ─────────────────────────────────────────────

def _backup_existing(opts: Options) -> None:
    ui.section("Backing up existing configuration")
    home = _home()
    suffix = f".bak.{time.strftime('%Y%m%d%H%M%S')}"
    backed_up = 0

    for name in MANAGED_CONFIGS:
        conf = home / f".{name}"
        if conf.is_symlink():
            ui.info(f"Removing symlink .{name}")
            if not opts.dry_run:
                conf.unlink()
        elif conf.is_file():
            ui.info(f"Backing up .{name} -> .{name}{suffix}")
            if not opts.dry_run:
                conf.rename(f"{conf}{suffix}")
            backed_up += 1

    for fw in MANAGED_FRAMEWORKS:
        fw_dir = home / fw
        if fw_dir.is_dir() and not fw_dir.is_symlink():
            ui.info(f"Backing up framework {fw}")
            if not opts.dry_run:
                fw_dir.rename(f"{fw_dir}{suffix}")
            backed_up += 1

    if backed_up:
        ui.success("Backup complete")
    else:
        ui.present("no conflicting config found")


def _link_zshrc(opts: Options, config_dir: Path) -> bool:
    ui.section("Linking .zshrc")
    src = config_dir / ".zshrc"
    dst = _home() / ".zshrc"
    if opts.dry_run:
        ui.info(f"Would symlink ~/.zshrc -> {src}")
        return True
    if not src.is_file():
        ui.failed(f"{src} not found")
        return False
    if dst.is_symlink() and os.readlink(dst) == str(src):
        ui.present("~/.zshrc link")
        return True
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    dst.symlink_to(src)
    ui.configured(f"~/.zshrc -> {src}")
    return True


def _install_cli(opts: Options, config_dir: Path) -> None:
    """Symlink `ziro-cli` to ~/.local/bin/ziro so the `ziro` command is on PATH."""
    ui.section("Installing CLI")
    bin_dir = _home() / ".local" / "bin"
    src = config_dir / "ziro-cli"
    dst = bin_dir / "ziro"

    if opts.dry_run:
        ui.info(f"Would symlink {dst} -> {src}")
        return

    if not src.is_file():
        ui.warn(f"{src} not found; skipping CLI installation")
        return

    if not bin_dir.is_dir():
        bin_dir.mkdir(parents=True, exist_ok=True)
        ui.info(f"Created {bin_dir}")

    if dst.is_symlink() and os.readlink(dst) == str(src):
        ui.present("~/.local/bin/ziro link")
        return

    if dst.exists() or dst.is_symlink():
        dst.unlink()
    dst.symlink_to(src)
    ui.configured(f"~/.local/bin/ziro -> {src}")


def _install_starship_config(opts: Options, config_dir: Path) -> None:
    """Copy the default theme's starship.toml into ~/.config if not already present.

    Never overwrites an existing file — user edits survive installs and
    updates. `ziro doctor` reports a missing config as a warning.
    Default theme package: themes/lambda (see `ziro theme apply <name>`).
    """
    ui.section("Prompt config")
    conf = _home() / ".config" / "starship.toml"
    if conf.exists():
        ui.present("~/.config/starship.toml (preserved, user-owned)")
        return
    if opts.dry_run:
        ui.info(f"Would copy default theme (themes/{themes.DEFAULT_THEME}) -> {conf}")
        return
    src = themes.theme_file(config_dir, themes.DEFAULT_THEME)
    if src is None or themes.DEFAULT_THEME not in themes.list_themes(config_dir):
        ui.skipped(f"no valid default theme package (themes/{themes.DEFAULT_THEME}); skipping")
        return
    conf.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, conf)
    ui.installed("~/.config/starship.toml (edit freely; ziro never overwrites)")


def _create_local_config(opts: Options, config_dir: Path) -> None:
    ui.section("Creating .zshrc.local")
    local = config_dir / ".zshrc.local"
    if local.is_file() and not opts.force:
        ui.present(".zshrc.local (preserved, user-owned)")
        return
    if opts.dry_run:
        ui.info("Would create .zshrc.local")
        return
    if not local.is_file():
        example = config_dir / ".zshrc.local.example"
        if example.is_file():
            shutil.copyfile(example, local)
            ui.installed(".zshrc.local (from .zshrc.local.example)")
            return
    env_type = "server" if opts.mode == "Server" else "desktop"
    editor = "vim" if env_type == "server" else "nvim"
    content = (
        f"# Machine-specific settings for {opts.mode}\n"
        f"# Generated by ziro install on {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"export EDITOR='{editor}'\n"
        "export BROWSER='echo'\n"
        "export TERMINAL='xterm'\n"
        f"export ZSH_ENV_TYPE='{env_type}'\n"
    )
    local.write_text(content)
    ui.installed(".zshrc.local")


# ── shell / compile / verify ─────────────────────────────────────────────────

def _change_shell(opts: Options, plat: platform_mod.Platform) -> None:
    if opts.skip_shell:
        ui.skipped("default shell change (--skip-shell)")
        return
    current = os.environ.get("SHELL", "")
    if current and os.path.basename(current) == "zsh":
        ui.present("default shell (zsh)")
        return
    zsh = platform_mod.zsh_path()
    if not zsh:
        ui.skipped("zsh not found in PATH; change default shell manually")
        return
    ui.section("Changing default shell to zsh")
    if opts.dry_run:
        ui.info(f"Would run: chsh -s {zsh}")
        return
    if not quiet(["grep", "-qx", zsh, "/etc/shells"]):
        ui.info(f"Adding {zsh} to /etc/shells")
        if plat.sudo:
            run(["sh", "-c", f"echo {zsh} | {plat.sudo} tee -a /etc/shells >/dev/null"])
        else:
            ui.warn("Could not update /etc/shells (no sudo); chsh may fail")
    if shutil.which("chsh"):
        proc = run(["chsh", "-s", zsh], check=False)
        if proc.returncode == 0:
            ui.configured("default shell -> zsh")
        else:
            ui.warn(f"Could not change shell automatically. Run: chsh -s {zsh}")
    else:
        ui.warn(f"chsh not available. Change shell manually: chsh -s {zsh}")


def _final_compile(opts: Options, config_dir: Path) -> None:
    ui.section("Final compilation (speedup)")
    if opts.dry_run:
        ui.info("Would compile znap plugins")
        return
    znap = config_dir / "znap" / "znap.zsh"
    if not znap.is_file():
        ui.skipped("znap missing; cannot compile")
        return
    existing = [str(config_dir / t) for t in ZSH_COMPILE_TARGETS if (config_dir / t).exists()]
    if not existing:
        ui.skipped("nothing to compile")
        return
    # Pass targets via environment to avoid quoting issues
    env = dict(os.environ)
    env["ZIRO_COMPILE_TARGETS"] = " ".join(existing)
    proc = run(["zsh", "-c",
                "source \"$1\" && znap compile ${=ZIRO_COMPILE_TARGETS}",
                "zsh", str(znap)],
               check=False, env=env,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if proc.returncode != 0:
        ui.warn("znap compile reported errors (continuing)")
    ui.success("Compilation done")


def _verify_install(opts: Options, config_dir: Path) -> None:
    ui.section("Verifying installation")
    if opts.dry_run:
        ui.info("Would verify zsh startup")
        return
    if quiet(["zsh", "-ic", "echo ZSH_OK"]):
        ui.success("Zsh loads without errors")
    else:
        ui.warn("Zsh startup reported issues (check plugins/dependencies)")

    plugins = {
        "fast-syntax-highlighting": config_dir / "zdharma-continuum" / "fast-syntax-highlighting",
        "zsh-autosuggestions": config_dir / "zsh-users" / "zsh-autosuggestions",
        "zsh-completions": config_dir / "zsh-users" / "zsh-completions",
    }
    missing = [name for name, path in plugins.items() if not path.is_dir()]
    if missing:
        ui.warn(f"Missing plugins: {', '.join(missing)}")
        ui.warn(f"Run 'znap pull' or re-run 'ziro install' in {config_dir}")
    ui.success("Verification complete")


def getting_started_lines() -> list[str]:
    lines = []
    if shutil.which("starship"):
        lines.append("Starship prompt active (config: ~/.config/starship.toml)")
    if shutil.which("fzf"):
        lines.append("pf          - interactive package manager (fzf)")
    lines += [
        "zsh_update  - update Ziro",
        "softar      - remove orphaned packages",
        "extract <f> - extract any archive",
        "mkcd <dir>  - create and enter a directory",
        "cdf / up N  - fuzzy cd / go up N dirs",
        "cheat <cmd> <term> - search man pages",
        "ziro doctor - check installation health",
    ]
    return lines
