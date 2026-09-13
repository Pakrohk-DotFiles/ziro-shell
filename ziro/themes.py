"""Theme packages: discover and apply external starship.toml themes.

A theme package is a directory under themes/<name>/ containing:
  Theme.toml     - metadata: [theme] section with name, version, description,
                   author, license (all required)
  Starship.toml  - the prompt config

`ziro theme list` shows available packages; `ziro theme apply <name>`
copies its Starship.toml to ~/.config/starship.toml. Apply never
overwrites a user-owned config unless the user confirms via --force
or the existing file is identical to the theme being applied.
"""

import os
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from . import ui

THEMES_DIR = "themes"
DEFAULT_THEME = "lambda"
CONFIG_PATH = Path.home() / ".config" / "starship.toml"


@dataclass(frozen=True)
class ThemePackage:
    """Validated theme package metadata from Theme.toml."""
    name: str
    version: str
    description: str
    author: str
    license: str
    path: Path
    starship: Path


REQUIRED_THEME_FIELDS = {"name", "version", "description", "author", "license"}

_SEMVER_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$')


def themes_root(config_dir: Path) -> Path:
    return config_dir / THEMES_DIR


def _validate_theme(data: dict, pkg_dir: Path) -> ThemePackage | None:
    """Validate a Theme.toml [theme] section. Returns ThemePackage or None."""
    if not isinstance(data.get("theme"), dict):
        return None
    t = data["theme"]
    if not REQUIRED_THEME_FIELDS.issubset(t.keys()):
        return None
    for field in ("name", "version", "description", "author", "license"):
        if not isinstance(t.get(field), str) or not t[field]:
            return None
    if not _SEMVER_RE.match(t["version"]):
        return None
    return ThemePackage(
        name=t["name"],
        version=t["version"],
        description=t["description"],
        author=t["author"],
        license=t["license"],
        path=pkg_dir,
        starship=pkg_dir / "Starship.toml",
    )


def list_themes(config_dir: Path) -> dict[str, ThemePackage]:
    """Return {name: ThemePackage} for every valid theme package.

    A valid package must have both Theme.toml and Starship.toml.
    Theme.toml must contain a [theme] section with required fields:
    name, version, description, author, license. Packages missing any
    of these are skipped.
    """
    root = themes_root(config_dir)
    if not root.is_dir():
        return {}
    found: dict[str, ThemePackage] = {}
    for pkg in sorted(root.iterdir()):
        if not pkg.is_dir():
            continue
        meta = pkg / "Theme.toml"
        starship = pkg / "Starship.toml"
        if not meta.is_file() or not starship.is_file():
            continue
        try:
            data = tomllib.loads(meta.read_text(encoding="utf-8"))
            parsed = _validate_theme(data, pkg)
            if parsed is None:
                continue
            if parsed.name != pkg.name:
                continue
            # Validate Starship.toml is parseable TOML and non-empty
            starship_data = tomllib.loads(starship.read_text(encoding="utf-8"))
            if not starship_data:
                continue
            found[parsed.name] = parsed
        except (OSError, tomllib.TOMLDecodeError):
            pass
    return found


def theme_file(config_dir: Path, name: str) -> Path | None:
    """Starship.toml path from a validated theme package, or None."""
    pkg = list_themes(config_dir).get(name)
    return pkg.starship if pkg else None


def _atomic_write(dest: Path, data: bytes) -> None:
    """Write bytes to dest atomically: temp file in same dir, fsync, os.replace."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(f".{dest.name}.ziro.tmp")
    try:
        with open(tmp, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, dest)
    finally:
        tmp.unlink(missing_ok=True)


def apply(config_dir: Path, name: str, force: bool = False) -> int:
    """Apply a validated theme package to ~/.config/starship.toml."""
    themes = list_themes(config_dir)
    if name not in themes:
        ui.error(f"unknown theme '{name}'. Available: {', '.join(themes) or 'none'}")
        return 2
    src = themes[name].starship
    if CONFIG_PATH.is_symlink():
        ui.error(f"{CONFIG_PATH} is a symlink; refusing to follow it.")
        ui.info("Remove the symlink first, then run: ziro theme apply " + name)
        return 1
    if CONFIG_PATH.exists() and not force:
        if CONFIG_PATH.read_bytes() == src.read_bytes():
            ui.present(f"~/.config/starship.toml already uses theme '{name}'")
            return 0
        ui.error(f"{CONFIG_PATH} exists and differs from theme '{name}'.")
        ui.info("Remove it or run: ziro theme apply " + name + " --force")
        return 1
    _atomic_write(CONFIG_PATH, src.read_bytes())
    ui.configured(f"~/.config/starship.toml -> theme '{name}'")
    ui.info("restart your terminal or run: source ~/.zshrc")
    return 0


def run(config_dir: Path, command: str | None, name: str | None,
        force: bool = False) -> int:
    """Entry for `ziro theme <list|current|apply>`."""
    if command == "list":
        themes = list_themes(config_dir)
        if not themes:
            ui.info(f"no theme packages in {themes_root(config_dir)}")
            return 0
        for tname, meta in themes.items():
            marker = " (default)" if tname == DEFAULT_THEME else ""
            label = f"{tname}{marker} v{meta.version}"
            ui.info(f"{label}: {meta.description}" if meta.description else label)
        return 0

    if command == "current":
        if not CONFIG_PATH.is_file():
            ui.info("no Starship.toml installed")
            return 1
        current = CONFIG_PATH.read_bytes()
        for tname, pkg in list_themes(config_dir).items():
            if current == pkg.starship.read_bytes():
                ui.info(f"theme '{tname}'")
                return 0
        ui.info("custom (no exact theme match)")
        return 0

    if command == "apply":
        if not name:
            themes = list_themes(config_dir)
            ui.error(f"usage: ziro theme apply <name>. Available: {', '.join(themes) or 'none'}")
            return 2
        return apply(config_dir, name, force)

    ui.error("unknown theme command: " + (command or ""))
    return 2
