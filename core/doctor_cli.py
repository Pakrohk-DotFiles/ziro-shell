"""ziro-shell — doctor command (health check).

Layer: 3 (Python core, cold-path only)
Spec: 006 SC-1
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from core.doctor import verify_generated


def _config_dir() -> Path:
    base = os.environ.get("ZIRO_CONFIG")
    if base:
        return Path(base)
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "ziro"


def _ziro_home() -> Path:
    return Path(os.environ.get("ZIRO_HOME", Path.home() / ".ziro"))


def _check_python() -> tuple[bool, str]:
    ok = sys.version_info >= (3, 11)
    return ok, f"python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def _check_znap() -> tuple[bool, str]:
    home = _ziro_home()
    candidates = [
        home / "vendor" / "znap" / "znap.zsh",
        home / "znap" / "znap.zsh",
    ]
    for c in candidates:
        if c.is_file():
            return True, str(c)
    return False, "znap not found in vendor/ or znap/"


def _check_ziro_defer() -> tuple[bool, str]:
    home = _ziro_home()
    z = home / "vendor" / "ziro-defer" / "ziro-defer.plugin.zsh"
    u = home / "vendor" / "ziro-defer" / "zsh-defer.plugin.zsh"
    if z.is_file():
        return True, f"ziro-defer (fork): {z}"
    if u.is_file():
        return True, f"zsh-defer (upstream): {u} (fork pending Phase 5 follow-up)"
    return False, "ziro-defer/zsh-defer not found"


def _check_config_files() -> list[tuple[str, bool, str]]:
    cfg = _config_dir()
    results = []
    for name in ("defaults.toml", "tools.toml", "prompt.conf", ".theme.conf"):
        p = cfg / name
        results.append((name, p.is_file(), str(p)))
    return results


def _check_generated() -> tuple[bool, str]:
    r = verify_generated(_config_dir())
    if r.healthy:
        return True, str(r.generated_path)
    return False, "; ".join(r.issues) or "unknown"


def cmd_doctor(argv: list[str]) -> int:
    verbose = "--verbose" in argv or "-v" in argv
    print("ziro doctor")
    print("=" * 50)

    checks: list[tuple[str, bool, str]] = []

    ok, msg = _check_python()
    checks.append(("Python 3.11+", ok, msg))

    ok, msg = _check_znap()
    checks.append(("znap", ok, msg))

    ok, msg = _check_ziro_defer()
    checks.append(("ziro-defer", ok, msg))

    ok, msg = _check_generated()
    checks.append(("plugins.gen.zsh", ok, msg))

    for name, ok, msg in _check_config_files():
        checks.append((f"config/{name}", ok, msg))

    failed = 0
    for name, ok, msg in checks:
        icon = "✅" if ok else "❌"
        print(f" {icon} {name:25s} {msg if verbose else ''}")
        if not ok:
            failed += 1

    print()
    if failed == 0:
        print(f"✅ healthy ({len(checks)} checks passed)")
        return 0
    print(f"❌ {failed} issue(s) found ({len(checks) - failed} passed)")
    return 1


def main(argv: list[str]) -> int:
    return cmd_doctor(argv)


__all__ = ["main"]
