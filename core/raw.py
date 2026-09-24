"""ziro-shell — --raw escape hatch (Layer 3).

Layer: 3 (znap Runtime)
Spec: 002 R1

Allows power users to inject verbatim zsh syntax that
bypasses ziro_load normalization. Useful for znap
features not yet exposed by interface.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RawSpec:
    """Raw zsh to inject verbatim."""

    plugin: str
    raw: str
    comment: str = ""


def validate_raw(spec: RawSpec) -> tuple[bool, str]:
    """Basic validation — reject obviously dangerous patterns.

    Returns (ok, reason).
    """
    raw = spec.raw.strip()

    if not raw:
        return False, "empty raw string"

    if raw.startswith("#"):
        return False, "raw starts with comment only"

    # Forbidden patterns (safety)
    forbidden = (
        "rm -rf /",
        "curl ",
        "wget ",
        "eval $",
        "> /dev/sd",
        "dd if=",
    )
    for pattern in forbidden:
        if pattern in raw:
            return False, f"forbidden pattern: {pattern}"

    return True, "ok"


def emit_raw(spec: RawSpec) -> str:
    """Emit raw zsh with optional comment header."""
    ok, reason = validate_raw(spec)
    if not ok:
        return f"# ziro: rejected raw for {spec.plugin} ({reason})"

    if spec.comment:
        return f"# raw: {spec.comment}\n{spec.raw}"
    return spec.raw


__all__ = ["RawSpec", "validate_raw", "emit_raw"]
