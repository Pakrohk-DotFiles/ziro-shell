"""ziro-shell — plugin pipeline (clone + analyze + generate).

Layer: 3 (Python core, cold-path only)
Spec: 001 FR-001 + 002 R5 + 003
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from core.analyzer import analyze_with_cache
from core.generator import EmitOptions, default_output_path, generate
from core.resolver import ConflictError, resolve
from core.tags import save_plugin_tags


@dataclass(frozen=True)
class AddResult:
    plugin: str
    plugin_dir: Path
    strategy: str
    generated: Path
    dry_run: bool = False
    skipped_clone: bool = False


def _plugins_root(ziro_home: Path) -> Path:
    return ziro_home / "plugins"


def _clone_repo(source: str, dest: Path, dry_run: bool) -> bool:
    """Clone git repo. Returns True if cloned, False if existed."""
    if dest.is_dir():
        return False
    if dry_run:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["git", "clone", "--depth=1", source, str(dest)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git clone failed: {result.stderr.strip()}")
    return True


def add_plugin(
    source: str,
    *,
    name: str = "",
    tags: list[str] | None = None,
    ziro_home: Path | None = None,
    config_dir: Path | None = None,
    all_configs: list | None = None,
    dry_run: bool = False,
) -> AddResult:
    """Full pipeline: clone → analyze → resolve → regenerate."""
    ziro_home = ziro_home or Path.home() / ".ziro"
    config_dir = config_dir or Path.home() / ".config" / "ziro"
    tags = tags or []
    all_configs = all_configs or []

    plugin_name = name or source.rstrip("/").split("/")[-1].removesuffix(".git")
    dest = _plugins_root(ziro_home) / plugin_name

    # 1. Clone
    skipped = not _clone_repo(source, dest, dry_run)

    # 2. Save tags (if any)
    if tags and not dry_run:
        save_plugin_tags(config_dir, plugin_name, tags)

    # 3. Analyze
    if not dest.is_dir():
        # dry-run: no source to analyze → fake analysis
        from core.models import AnalysisResult, Recommendation, Strategy
        analysis = AnalysisResult.empty(plugin_name, source)
    else:
        analysis = analyze_with_cache(dest, plugin_name)

    # 4. Resolve
    try:
        resolved = resolve(analysis, config_dir)
    except ConflictError as e:
        raise RuntimeError(f"tag conflict: {e}") from e

    # 5. Regenerate plugins.gen.zsh
    generated = default_output_path(config_dir)
    configs = list(all_configs) + [resolved]
    if not dry_run:
        generate(configs, generated, options=EmitOptions(enforce_order=True))

    return AddResult(
        plugin=plugin_name,
        plugin_dir=dest,
        strategy=resolved.strategy.value if hasattr(resolved.strategy, "value") else str(resolved.strategy),
        generated=generated,
        dry_run=dry_run,
        skipped_clone=skipped,
    )


def remove_plugin(
    name: str,
    *,
    ziro_home: Path | None = None,
    config_dir: Path | None = None,
    all_configs: list | None = None,
    dry_run: bool = False,
) -> bool:
    """Remove plugin dir + tags + regenerate. Returns True if removed."""
    ziro_home = ziro_home or Path.home() / ".ziro"
    config_dir = config_dir or Path.home() / ".config" / "ziro"
    all_configs = all_configs or []

    dest = _plugins_root(ziro_home) / name
    if not dest.is_dir():
        return False
    if dry_run:
        return True

    # Remove plugin dir
    shutil.rmtree(dest, ignore_errors=True)

    # Remove tag file
    tag_file = config_dir / "tags" / "plugins" / f"{name}.toml"
    if tag_file.is_file():
        tag_file.unlink()

    # Regenerate without this plugin
    configs = [c for c in all_configs if c.plugin != name]
    if configs:
        generate(configs, default_output_path(config_dir), options=EmitOptions(enforce_order=True))

    return True


__all__ = ["AddResult", "add_plugin", "remove_plugin"]
