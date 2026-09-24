"""ziro-shell — Layer 1 plugin analyzer (core).

Layer: 3 (Python core, cold-path only)
Spec: 001
Patterns: compdef, zle_widgets, zsh_hooks, bindkey

Scans a plugin directory, detects load-relevant signals, and returns a
Schema A AnalysisResult recommending a load strategy.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from core.models import (
    AnalysisResult,
    DetectedSignals,
    Recommendation,
    Strategy,
)


ANALYZER_VERSION = "0.1.0"

# ─── Pattern definitions (compiled once) ───

_PATTERNS = {
    "compdef": re.compile(r"^\s*compdef\s+", re.MULTILINE),
    "zle_n": re.compile(r"^\s*zle\s+-N\s+", re.MULTILINE),
    "zle_hook": re.compile(r"add-zle-hook-widget\s+(\w+)"),
    "zsh_hook": re.compile(r"^\s*add-zsh-hook\s+([a-z_][a-z0-9_]*)\s", re.MULTILINE),
    "bindkey": re.compile(r"^\s*bindkey\s+", re.MULTILINE),
    "eval_subprocess": re.compile(r"eval\s+\"\$\(([^)]+)\)\""),
    "path_mod": re.compile(r"\bPATH\s*=\s*[\"']?[^\s\"']*\bPATH"),
    "prompt_var": re.compile(r"^\s*(PROMPT|PS1|RPROMPT|RPS1)\s*=", re.MULTILINE),
}


def _read_source_files(plugin_dir: Path) -> Iterable[Path]:
    """Yield all .zsh and .plugin.zsh files under plugin_dir."""
    for pattern in ("**/*.plugin.zsh", "**/*.zsh"):
        for path in plugin_dir.glob(pattern):
            if path.is_file():
                yield path


def _find_main_file(plugin_dir: Path, plugin_name: str) -> str:
    """Find main plugin file: *.plugin.zsh > <name>.zsh > *.zsh."""
    # Priority 1: name.plugin.zsh
    candidate = plugin_dir / f"{plugin_name}.plugin.zsh"
    if candidate.is_file():
        return candidate.name

    # Priority 2: any *.plugin.zsh
    for path in sorted(plugin_dir.glob("*.plugin.zsh")):
        return path.name

    # Priority 3: name.zsh
    candidate = plugin_dir / f"{plugin_name}.zsh"
    if candidate.is_file():
        return candidate.name

    # Priority 4: any top-level .zsh
    for path in sorted(plugin_dir.glob("*.zsh")):
        return path.name

    return ""


def _detect_signals(content: str) -> DetectedSignals:
    """Run all regex patterns over concatenated source."""
    hooks: set[str] = set()
    eval_cmds: list[str] = []

    for match in _PATTERNS["zsh_hook"].finditer(content):
        hooks.add(match.group(1))

    for match in _PATTERNS["eval_subprocess"].finditer(content):
        eval_cmds.append(match.group(1))

    return DetectedSignals(
        hooks=tuple(sorted(hooks)),
        zle_widgets=bool(_PATTERNS["zle_hook"].search(content)),
        compdef=bool(_PATTERNS["compdef"].search(content)),
        bindkey=bool(_PATTERNS["bindkey"].search(content)),
        eval_commands=tuple(eval_cmds),
        modifies_path=bool(_PATTERNS["path_mod"].search(content)),
        is_prompt=bool(_PATTERNS["prompt_var"].search(content)),
    )


def _recommend(signals: DetectedSignals) -> Recommendation:
    """Map signals to load strategy (per Spec 001 FR-002)."""
    # compdef must be eager (before compinit)
    if signals.compdef:
        return Recommendation(strategy=Strategy.EAGER)

    # PATH modification must be eager
    if signals.modifies_path:
        return Recommendation(strategy=Strategy.EAGER)

    # ZLE / bindkey / prompt → after-prompt
    if signals.zle_widgets or signals.bindkey or signals.is_prompt:
        return Recommendation(strategy=Strategy.AFTER_PROMPT, wait="0")

    # Hooks (precmd/preexec/chpwd) → after-prompt
    if signals.hooks:
        return Recommendation(strategy=Strategy.AFTER_PROMPT, wait="0")

    # eval-cache candidate
    if signals.eval_commands:
        return Recommendation(
            strategy=Strategy.EAGER,
            eval_cache=True,
            adapter_options=tuple(signals.eval_commands),
        )

    # No signals → lazy (safe fallback)
    return Recommendation(strategy=Strategy.LAZY, wait="2")


def _confidence(signals: DetectedSignals) -> float:
    """Confidence score 0.0-1.0 based on signal count."""
    if not signals.has_any():
        return 0.0
    count = (
        len(signals.hooks)
        + int(signals.zle_widgets)
        + int(signals.compdef)
        + int(signals.bindkey)
        + len(signals.eval_commands)
        + int(signals.modifies_path)
        + int(signals.is_prompt)
    )
    return min(1.0, count / 5.0)


def analyze_plugin(plugin_dir: Path, plugin_name: str = "") -> AnalysisResult:
    """Analyze single plugin directory synchronously.

    Returns AnalysisResult (Schema A) — never raises on bad input.
    """
    plugin_dir = Path(plugin_dir)
    plugin_name = plugin_name or plugin_dir.name

    if not plugin_dir.is_dir():
        return AnalysisResult.empty(plugin_name)

    # Concatenate all .zsh sources
    chunks: list[str] = []
    for src in _read_source_files(plugin_dir):
        try:
            chunks.append(src.read_text(errors="ignore"))
        except OSError:
            continue

    content = "\n".join(chunks)

    signals = _detect_signals(content)
    recommendation = _recommend(signals)
    confidence = _confidence(signals)

    main_file = _find_main_file(plugin_dir, plugin_name)
    if main_file:
        recommendation = Recommendation(
            strategy=recommendation.strategy,
            wait=recommendation.wait,
            compile=recommendation.compile,
            eval_cache=recommendation.eval_cache,
            adapter_options=recommendation.adapter_options,
            pick=main_file,
        )

    return AnalysisResult(
        plugin=plugin_name,
        source=str(plugin_dir),
        detected=signals,
        recommended=recommendation,
        confidence=confidence,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
        analyzer_version=ANALYZER_VERSION,
    )


__all__ = ["analyze_plugin", "ANALYZER_VERSION"]
