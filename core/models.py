"""ziro-shell — data models for Layer 1 analyzer.

Layer: 3 (Python core, cold-path only)
Spec: 001
Schema: A (analysis output)

These dataclasses are the stable contract between the Layer 1 analyzer
(Python, cold-path) and the zsh runtime adapters. The frozen design makes
results hashable and safe to cache on disk as JSON (see AnalysisResult.to_dict).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Strategy(str, Enum):
    """Load strategy recommendation."""
    EAGER = "eager"
    AFTER_PROMPT = "after-prompt"
    AT_PROMPT = "at-prompt"
    LAZY = "lazy"


@dataclass(frozen=True)
class DetectedSignals:
    """Raw signals detected in plugin source."""
    hooks: tuple[str, ...] = ()  # precmd, preexec, chpwd
    zle_widgets: bool = False
    compdef: bool = False
    bindkey: bool = False
    eval_commands: tuple[str, ...] = ()
    modifies_path: bool = False
    is_prompt: bool = False

    def has_any(self) -> bool:
        return bool(
            self.hooks or self.zle_widgets or self.compdef
            or self.bindkey or self.eval_commands
            or self.modifies_path or self.is_prompt
        )


@dataclass(frozen=True)
class Recommendation:
    """Recommended load strategy."""
    strategy: Strategy = Strategy.EAGER
    wait: str = ""
    compile: bool = True
    eval_cache: bool = False
    adapter_options: tuple[str, ...] = ()
    pick: str = ""


@dataclass(frozen=True)
class AnalysisResult:
    """Schema A — output of Layer 1 analysis (frozen)."""
    plugin: str
    source: str
    detected: DetectedSignals
    recommended: Recommendation
    confidence: float = 0.0
    analyzed_at: str = ""
    analyzer_version: str = "0.1.0"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to Schema A JSON."""
        return {
            "plugin": self.plugin,
            "source": self.source,
            "detected": {
                "hooks": list(self.detected.hooks),
                "zle_widgets": self.detected.zle_widgets,
                "compdef": self.detected.compdef,
                "bindkey": self.detected.bindkey,
                "eval_commands": list(self.detected.eval_commands),
                "modifies_path": self.detected.modifies_path,
                "is_prompt": self.detected.is_prompt,
            },
            "recommended": {
                "strategy": self.recommended.strategy.value,
                "wait": self.recommended.wait,
                "compile": self.recommended.compile,
                "eval_cache": self.recommended.eval_cache,
                "adapter_options": list(self.recommended.adapter_options),
                "pick": self.recommended.pick,
            },
            "confidence": self.confidence,
            "analyzed_at": self.analyzed_at,
            "analyzer_version": self.analyzer_version,
        }

    @staticmethod
    def empty(plugin: str, source: str = "") -> "AnalysisResult":
        """Safe fallback — unknown plugin → eager."""
        return AnalysisResult(
            plugin=plugin,
            source=source,
            detected=DetectedSignals(),
            recommended=Recommendation(strategy=Strategy.EAGER),
            confidence=0.0,
            analyzed_at=datetime.now(timezone.utc).isoformat(),
        )
