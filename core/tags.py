"""ziro-shell — Tag system (Layer 2).

Layer: 3 (Python core, cold-path only)
Spec: 003

Tag registry: reads builtin.toml + user.toml, plus per-plugin tag files.
Builtin tags are shipped immutable; user tags/overrides win on collision.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Tag:
    """single tag definition."""
    name: str
    strategy: str
    priority: int = 0
    description: str = ""
    eager_order: str = ""
    defer_slot: str = ""
    compile: bool = True
    eval_cache: bool = False

    def is_builtin(self) -> bool:
        return self.name.startswith("@")


def _parse_tag(entry: dict) -> Tag | None:
    name = entry.get("name", "")
    if not name:
        return None
    return Tag(
        name=name,
        strategy=entry.get("strategy", "eager"),
        priority=int(entry.get("priority", 0)),
        description=entry.get("description", ""),
        eager_order=entry.get("eager_order", ""),
        defer_slot=entry.get("defer_slot", ""),
        compile=bool(entry.get("compile", True)),
        eval_cache=bool(entry.get("eval_cache", False)),
    )


def _load_toml_tags(path: Path) -> dict[str, Tag]:
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError):
        return {}
    out: dict[str, Tag] = {}
    for entry in data.get("tags", []):
        tag = _parse_tag(entry)
        if tag:
            out[tag.name] = tag
    return out


def load_builtin_tags(config_dir: Path) -> dict[str, Tag]:
    return _load_toml_tags(config_dir / "tags" / "builtin.toml")


def load_user_tags(config_dir: Path) -> dict[str, Tag]:
    return _load_toml_tags(config_dir / "tags" / "user.toml")


def load_all_tags(config_dir: Path) -> dict[str, Tag]:
    """Builtin + user tags. User wins on collision."""
    tags = load_builtin_tags(config_dir)
    tags.update(load_user_tags(config_dir))
    return tags


def load_plugin_tags(config_dir: Path, plugin_name: str) -> list[str]:
    """Load applied tags for specific plugin."""
    path = config_dir / "tags" / "plugins" / f"{plugin_name}.toml"
    if not path.is_file():
        return []
    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError):
        return []
    return list(data.get("user", {}).get("tags", []))


def save_plugin_tags(
    config_dir: Path,
    plugin_name: str,
    tags: list[str],
) -> None:
    """Write plugin tags file (minimal hand-rolled TOML writer)."""
    path = config_dir / "tags" / "plugins" / f"{plugin_name}.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# ziro-shell — plugin tags",
        f"# Plugin: {plugin_name}",
        "# Spec: 003",
        "",
        "[plugin]",
        f"name = \"{plugin_name}\"",
        "",
        "[user]",
        f"tags = [{', '.join(repr(t) for t in tags)}]",
        "",
    ]
    path.write_text("\n".join(lines))


__all__ = [
    "Tag",
    "load_builtin_tags",
    "load_user_tags",
    "load_all_tags",
    "load_plugin_tags",
    "save_plugin_tags",
]
