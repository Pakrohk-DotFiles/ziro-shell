"""Theme package validation and discovery models. Pure logic, no I/O."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


REQUIRED_THEME_FIELDS = frozenset({"name", "version", "description", "author", "license"})
SEMVER_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$')

THEMES_DIR = "themes"
DEFAULT_THEME = "lambda"


@dataclass(frozen=True)
class ThemePackage:
    name: str
    version: str
    description: str
    author: str
    license: str
    path: Path
    starship: Path


class ThemeValidationError(Exception):
    pass


def validate_theme(data: dict, pkg_dir: Path) -> ThemePackage | None:
    """Validate Theme.toml payload against the package directory.

    Returns None when the [theme] section is malformed, a required field is
    missing/empty, the version is not semver, or the declared name does not
    match the directory name (packages are addressed by directory name).
    """
    if not isinstance(data.get("theme"), dict):
        return None
    t = data["theme"]
    if not REQUIRED_THEME_FIELDS.issubset(t.keys()):
        return None
    for field_name in REQUIRED_THEME_FIELDS:
        if not isinstance(t.get(field_name), str) or not t[field_name]:
            return None
    if not SEMVER_RE.match(t["version"]):
        return None
    if t["name"] != pkg_dir.name:
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


def discover_themes(config_dir: Path) -> dict[str, ThemePackage]:
    import tomllib
    root = config_dir / THEMES_DIR
    if not root.is_dir():
        return {}
    found: dict[str, ThemePackage] = {}
    for pkg_dir in sorted(root.iterdir()):
        if not pkg_dir.is_dir():
            continue
        meta = pkg_dir / "Theme.toml"
        starship = pkg_dir / "Starship.toml"
        if not meta.is_file() or not starship.is_file():
            continue
        try:
            data = tomllib.loads(meta.read_text(encoding="utf-8"))
            parsed = validate_theme(data, pkg_dir)
            if parsed is None or parsed.name != pkg_dir.name:
                continue
            starship_data = tomllib.loads(starship.read_text(encoding="utf-8"))
            if not starship_data:
                continue
            found[parsed.name] = parsed
        except (OSError, Exception):
            pass
    return found


def get_default_theme(config_dir: Path) -> ThemePackage | None:
    return discover_themes(config_dir).get(DEFAULT_THEME)


def starship_config_path() -> Path:
    return Path.home() / ".config" / "starship.toml"


def starship_files_identical(path_a: Path, path_b: Path) -> bool:
    return path_a.read_bytes() == path_b.read_bytes()


def parse_theme_meta(data: dict, pkg_dir: Path) -> ThemePackage | None:
    return validate_theme(data, pkg_dir)
