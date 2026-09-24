"""ziro-shell — Doctor: hash validation for plugins.gen.zsh.

Layer: 3 (znap Runtime)
Spec: 002 R5, FR-006d
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from core.generator import HEADER_LINE, default_output_path


@dataclass(frozen=True)
class DoctorResult:
    """Health check result."""

    healthy: bool
    issues: tuple[str, ...] = ()
    generated_path: Path | None = None


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def verify_generated(
    config_dir: Path,
    expected_configs_hash: str = "",
) -> DoctorResult:
    """Verify plugins.gen.zsh exists, has header, matches hash."""
    issues: list[str] = []
    path = default_output_path(config_dir)

    if not path.is_file():
        issues.append(f"plugins.gen.zsh missing at {path}")
        return DoctorResult(healthy=False, issues=tuple(issues))

    content = path.read_text()

    if not content.startswith(HEADER_LINE):
        issues.append("Missing AUTO-GENERATED header (possibly hand-edited)")

    if expected_configs_hash:
        actual = _file_hash(path)
        if actual != expected_configs_hash:
            issues.append(
                f"Hash mismatch: expected {expected_configs_hash[:12]}, "
                f"got {actual[:12]}"
            )

    return DoctorResult(
        healthy=not issues,
        issues=tuple(issues),
        generated_path=path,
    )


def compute_expected_hash(config_dir: Path, plugin_dirs: list[tuple[Path, str]]) -> str:
    """Compute hash of analysis+tags inputs (source-of-truth hash)."""
    from core.analyzer import analyze_with_cache
    from core.resolver import resolve

    h = hashlib.sha256()
    for plugin_dir, plugin_name in sorted(plugin_dirs, key=lambda x: x[1]):
        analysis = analyze_with_cache(plugin_dir, plugin_name)
        resolved = resolve(analysis, config_dir)
        h.update(f"{plugin_name}|{resolved.strategy.value}\n".encode())
    return h.hexdigest()


__all__ = ["DoctorResult", "verify_generated", "compute_expected_hash"]
