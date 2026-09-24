"""ziro-shell — ziro_load: frozen interface (Layer 3).

Layer: 3 (znap Runtime)
Spec: 002 R1 (frozen contract)

This module produces the ZSH syntax that plugins.gen.zsh will emit.
It is pure-function emitter — no I/O, no side effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Strategy = Literal["eager", "after-prompt", "lazy", "raw"]


@dataclass(frozen=True)
class LoadSpec:
    """Frozen representation of single plugin load request.

    Mirrors ziro_load interface (Spec 002 R1).
    """
    plugin: str
    strategy: Strategy = "eager"
    wait: str = ""
    sub_slot: str = ""
    lazy_by_command: str = ""
    lazy_by_function: str = ""
    compile: bool = True
    pick: str = ""
    atinit: str = ""
    atload: str = ""
    notify: str = ""
    lucid: bool = False
    reset_prompt: bool = False
    eval_cache: str = ""
    raw: str = ""


def emit_eager(spec: LoadSpec) -> str:
    """Emit znap source line for eager plugins."""
    if spec.eval_cache:
        return f"znap eval {spec.plugin} '{spec.eval_cache}'"
    if spec.pick:
        return f"znap source {spec.plugin} --pick={spec.pick}"
    return f"znap source {spec.plugin}"


def emit_deferred(spec: LoadSpec) -> str:
    """Emit ziro-defer-wrapped znap source for deferred plugins."""
    prefix = "ziro-defer"
    args: list[str] = []

    if spec.wait:
        args.append(f'--wait="{spec.wait}"')
    if spec.sub_slot:
        args.append(f"--slot={spec.sub_slot}")
    if spec.lazy_by_command:
        args.append(f'--lazy-by-command="{spec.lazy_by_command}"')
    if spec.lazy_by_function:
        args.append(f'--lazy-by-function="{spec.lazy_by_function}"')
    if spec.atinit:
        args.append(f'--atinit="{spec.atinit}"')
    if spec.atload:
        args.append(f'--atload="{spec.atload}"')

    inner = f"znap source {spec.plugin}"
    if args:
        return f"{prefix} {' '.join(args)} {inner}"
    return f"{prefix} {inner}"


def emit_raw(spec: LoadSpec) -> str:
    """Emit raw syntax verbatim (escape hatch, Spec 002 R1)."""
    return spec.raw


def emit(spec: LoadSpec) -> str:
    """Emit zsh line for a LoadSpec — dispatches by strategy."""
    if spec.raw:
        return emit_raw(spec)
    if spec.strategy == "eager":
        return emit_eager(spec)
    if spec.strategy in ("after-prompt", "lazy"):
        return emit_deferred(spec)
    return emit_eager(spec)  # safe fallback


def from_resolved(
    plugin: str,
    strategy: str,
    *,
    compile_: bool = True,
    eval_cache: bool = False,
    pick: str = "",
    wait: str = "",
    defer_slot: str = "",
    raw: str = "",
) -> LoadSpec:
    """Build LoadSpec from ResolvedConfig fields.

    Maps ResolvedConfig.strategy to LoadSpec.strategy:
    EAGER -> eager
    AFTER_PROMPT -> after-prompt
    LAZY -> lazy
    """
    strategy_lower = strategy.lower().replace("_", "-")
    if strategy_lower not in ("eager", "after-prompt", "lazy"):
        strategy_lower = "eager"  # safe fallback

    return LoadSpec(
        plugin=plugin,
        strategy=strategy_lower,  # type: ignore[arg-type]
        wait=wait,
        sub_slot=defer_slot,
        compile=compile_,
        pick=pick,
        eval_cache=(f"{plugin} init" if eval_cache else ""),
        raw=raw,
    )


__all__ = [
    "LoadSpec",
    "emit",
    "emit_eager",
    "emit_deferred",
    "emit_raw",
    "from_resolved",
]
