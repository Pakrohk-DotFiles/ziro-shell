"""ziro-shell — plugins.gen.zsh regeneration orchestrator.

Layer: 3 (znap Runtime)
Spec: 002 R5 (regeneration triggers)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.analyzer import analyze_with_cache
from core.generator import EmitOptions, default_output_path, generate
from core.resolver import resolve


TRIGGERS = [
    "plugin-add",
    "plugin-remove",
    "plugin-optimize",
    "tag-add",
    "tag-remove",
    "tag-define",
    "tag-reset",
    "suggest-set",
    "theme-apply",
]


@dataclass(frozen=True)
class RegenerateResult:
    output: Path
    plugin_count: int
    trigger: str


def regenerate(
    config_dir: Path,
    plugin_dirs: list[tuple[Path, str]],
    *,
    trigger: str = "manual",
) -> RegenerateResult:
    """Regenerate plugins.gen.zsh from plugin dirs + tags.

    plugin_dirs: list of (plugin_directory, plugin_name)
    """
    if trigger not in TRIGGERS and trigger != "manual":
        raise ValueError(f"Unknown trigger: {trigger}")

    configs = []
    for plugin_dir, plugin_name in plugin_dirs:
        analysis = analyze_with_cache(plugin_dir, plugin_name)
        resolved = resolve(analysis, config_dir)
        configs.append(resolved)

    output = default_output_path(config_dir)
    generate(configs, output, options=EmitOptions(enforce_order=True))

    return RegenerateResult(
        output=output,
        plugin_count=len(configs),
        trigger=trigger,
    )


__all__ = ["regenerate", "RegenerateResult", "TRIGGERS"]
