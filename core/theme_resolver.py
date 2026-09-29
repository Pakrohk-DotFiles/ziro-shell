"""ziro-shell — theme resolution (T3).

Layer: 3 (Python core, cold-path only)
Spec: 006 R6

Axes: nerd_font, truecolor, platform, env_type, component.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EnvContext:
    """Environment snapshot for resolution."""
    platform: str = "linux"  # linux|macos|wsl|termux
    env_type: str = "desktop"  # server|desktop
    has_nerd_font: bool = False
    has_truecolor: bool = False


def resolve_prompt_theme(ctx: EnvContext) -> str:
    """Resolve best prompt theme for environment."""
    # Server / no rich terminal → minimal
    if ctx.env_type == "server":
        return "minimal"

    # No Nerd Font → minimal (avoid broken glyphs)
    if not ctx.has_nerd_font:
        return "minimal"

    # Truecolor + Nerd Font + Desktop → rich theme
    if ctx.has_truecolor:
        return "powerline"

    # 256 color fallback
    return "standard"


def resolve_auto_suggest_theme(ctx: EnvContext) -> str:
    """Auto-suggest theme (mostly fixed)."""
    if ctx.env_type == "server":
        return "minimal"
    return "default"


def resolve_colors_theme(ctx: EnvContext) -> str:
    if ctx.env_type == "server":
        return "minimal"
    return "default"


def resolve_syntax_theme(ctx: EnvContext) -> str:
    if ctx.env_type == "server":
        return "minimal"
    return "default"


def resolve_all(ctx: EnvContext) -> dict[str, str]:
    """Resolve every component."""
    return {
        "prompt": resolve_prompt_theme(ctx),
        "auto_suggest": resolve_auto_suggest_theme(ctx),
        "colors": resolve_colors_theme(ctx),
        "syntax_highlighting": resolve_syntax_theme(ctx),
    }


__all__ = [
    "EnvContext",
    "resolve_prompt_theme",
    "resolve_auto_suggest_theme",
    "resolve_colors_theme",
    "resolve_syntax_theme",
    "resolve_all",
]
