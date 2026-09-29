"""ziro-shell — Tag resolver (Layer 2).

Merges Layer 1 analysis with user tags → final config.
Layer: 3 (Python core, cold-path only)
Spec: 003
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.models import AnalysisResult, Recommendation, Strategy
from core.tags import Tag, load_all_tags, load_plugin_tags


class ConflictError(Exception):
    """Raised when tags conflict irreconcilably."""


@dataclass(frozen=True)
class ResolvedConfig:
    plugin: str
    strategy: Strategy
    compile: bool = True
    eval_cache: bool = False
    pick: str = ""
    wait: str = ""
    defer_slot: str = ""
    raw: str = ""
    applied_tags: tuple[str, ...] = ()


def _apply_tag(rec: Recommendation, tag: Tag) -> Recommendation:
    if tag.name == "@eager" or tag.name == "@compdef":
        return Recommendation(
            strategy=Strategy.EAGER,
            compile=rec.compile,
            eval_cache=rec.eval_cache,
            pick=rec.pick,
            adapter_options=rec.adapter_options,
        )
    if tag.name in ("@lazy", "@after-prompt"):
        wait = tag.defer_slot or "0"
        return Recommendation(
            strategy=Strategy.AFTER_PROMPT,
            wait=wait,
            compile=rec.compile,
            eval_cache=rec.eval_cache,
            pick=rec.pick,
            adapter_options=rec.adapter_options,
        )
    if tag.name == "@no-compile":
        return Recommendation(
            strategy=rec.strategy,
            wait=rec.wait,
            compile=False,
            eval_cache=rec.eval_cache,
            pick=rec.pick,
            adapter_options=rec.adapter_options,
        )
    if tag.name == "@eval-cache":
        return Recommendation(
            strategy=rec.strategy,
            wait=rec.wait,
            compile=rec.compile,
            eval_cache=True,
            pick=rec.pick,
            adapter_options=rec.adapter_options,
        )
    return rec


def resolve(
    analysis: AnalysisResult,
    config_dir: Path,
    *,
    raise_on_conflict: bool = False,
) -> ResolvedConfig:
    """Merge analysis + tags → ResolvedConfig.

    Args:
        analysis: Layer 1 output
        config_dir: ~/.config/ziro/
        raise_on_conflict: if True, raise ConflictError; else, last tag wins
    """
    all_tags = load_all_tags(config_dir)
    plugin_tags = load_plugin_tags(config_dir, analysis.plugin)

    # Conflict detection (Spec 003 R4)
    names_set = set(plugin_tags)
    if "@eager" in names_set and "@lazy" in names_set:
        if raise_on_conflict:
            raise ConflictError(
                f"Plugin {analysis.plugin!r}: @eager and @lazy conflict"
            )
    if "@compdef" in names_set and "@lazy" in names_set:
        if raise_on_conflict:
            raise ConflictError(
                f"Plugin {analysis.plugin!r}: @compdef cannot be @lazy"
            )

    # Sort by priority (higher first)
    def prio(name: str) -> int:
        t = all_tags.get(name)
        return t.priority if t else -1

    sorted_tags = sorted(plugin_tags, key=prio, reverse=True)

    rec = analysis.recommended
    for name in sorted_tags:
        tag = all_tags.get(name)
        if tag is not None:
            rec = _apply_tag(rec, tag)

    return ResolvedConfig(
        plugin=analysis.plugin,
        strategy=rec.strategy,
        compile=rec.compile,
        eval_cache=rec.eval_cache,
        pick=rec.pick,
        wait=rec.wait,
        defer_slot=rec.wait,
        applied_tags=tuple(sorted_tags),
    )


__all__ = ["resolve", "ResolvedConfig", "ConflictError"]
