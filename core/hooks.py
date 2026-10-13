"""ziro-shell — Hook re-registration for deferred plugins.

Layer: 3 (znap Runtime)
Spec: 002 R4

After ziro-defer defers plugin, some plugins lose their
hooks (chpwd, preexec, precmd). This module emits compensating
zsh code to re-register those hooks.

Verified facts (Spec 002 R4):
 - wd: registers chpwd → needs re-registration
 - alias-tips: registers preexec → needs re-registration
 - colored-man-pages: NO hooks → skip
 - z: NO hooks → skip
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HookSpec:
    """Re-registration spec for one plugin."""

    plugin: str
    hook_type: str  # chpwd, preexec, precmd
    handler: str  # function name to register
    auto_detect: bool = True


# Registry of verified hooks (Spec 002 R4)
KNOWN_HOOKS: dict[str, HookSpec] = {
    "wd": HookSpec("wd", "chpwd", "_wd_chpwd"),
    "mfaerevaag/wd": HookSpec("wd", "chpwd", "_wd_chpwd"),
    "alias-tips": HookSpec("alias-tips", "preexec", "_alias_tips_preexec"),
    "djui/alias-tips": HookSpec("alias-tips", "preexec", "_alias_tips_preexec"),
}


def emit_re_registration(plugin: str) -> str:
    """Emit zsh re-registration snippet, or empty string if none needed."""
    spec = KNOWN_HOOKS.get(plugin)
    if spec is None:
        return ""

    return (
        f"# Re-register {spec.hook_type} hook for {plugin}\n"
        f"add-zsh-hook {spec.hook_type} {spec.handler} 2>/dev/null || true"
    )


def needs_re_registration(plugin: str) -> bool:
    return plugin in KNOWN_HOOKS


def list_known_hooks() -> dict[str, HookSpec]:
    return dict(KNOWN_HOOKS)


__all__ = [
    "HookSpec",
    "KNOWN_HOOKS",
    "emit_re_registration",
    "needs_re_registration",
    "list_known_hooks",
]
