"""ziro-shell — update command.

Layer: 3 (Python core, cold-path only)
Spec: 008
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path


def _repo_dir() -> Path:
    env = os.environ.get("ZIRO_HOME")
    if env:
        return Path(env)
    return Path.home() / ".ziro"


def _cache_dir() -> Path:
    env = os.environ.get("ZIRO_CACHE")
    if env:
        return Path(env)
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg) / "ziro"
    return Path.home() / ".cache" / "ziro"


def _config_dir() -> Path:
    env = os.environ.get("ZIRO_CONFIG")
    if env:
        return Path(env)
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "ziro"
    return Path.home() / ".config" / "ziro"


def is_opted_out(config_dir: Path | None = None) -> bool:
    """Return True if user explicitly opted out of update checks in defaults.toml."""
    cfg = config_dir or _config_dir()
    defaults_file = cfg / "defaults.toml"
    if not defaults_file.is_file():
        return False
    try:
        content = defaults_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("check_for_updates") or line.startswith("enabled"):
                parts = line.split("=", 1)
                if len(parts) == 2 and parts[1].strip().lower() in ("false", "0", '"false"'):
                    return True
    except OSError:
        return False
    return False


def is_cache_fresh(cache_file: Path, ttl: int = 86400, now: float | None = None) -> bool:
    """Check if cache file exists and was checked within ttl seconds."""
    if not cache_file.is_file():
        return False
    current_time = now if now is not None else time.time()
    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        checked_at = data.get("checked_at")
        if checked_at and isinstance(checked_at, (int, float)):
            return (current_time - checked_at) < ttl
        mtime = cache_file.stat().st_mtime
        return (current_time - mtime) < ttl
    except (OSError, json.JSONDecodeError, ValueError):
        return False


def read_cache(cache_file: Path) -> dict | None:
    """Read cached update info if valid JSON."""
    if not cache_file.is_file():
        return None
    try:
        return json.loads(cache_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def write_cache(cache_file: Path, data: dict) -> None:
    """Persist update status to cache file atomically."""
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    tmp = cache_file.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(cache_file)
    except OSError:
        pass


def check_update(
    repo_dir: Path | None = None,
    cache_dir: Path | None = None,
    fetch: bool = True,
) -> dict:
    """Check repository against origin/main for available updates."""
    repo = repo_dir or _repo_dir()
    cache_d = cache_dir or _cache_dir()
    cache_file = cache_d / "update-check.json"

    result = {
        "available": False,
        "local": "",
        "remote": "",
        "behind": 0,
        "checked_at": int(time.time()),
        "error": None,
    }

    git_dir = repo / ".git"
    if not git_dir.exists():
        result["error"] = "not a git repository"
        return result

    try:
        local_hash_res = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        local_hash = local_hash_res.stdout.strip()
        result["local"] = local_hash
    except (subprocess.SubprocessError, OSError) as e:
        result["error"] = f"git rev-parse failed: {e}"
        return result

    if fetch:
        try:
            subprocess.run(
                ["git", "-C", str(repo), "fetch", "-q", "origin", "main"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
        except (subprocess.SubprocessError, OSError) as e:
            result["error"] = f"git fetch failed: {e}"
            # Still proceed to check existing origin/main if available

    try:
        remote_hash_res = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "origin/main"],
            capture_output=True,
            text=True,
            check=True,
        )
        remote_hash = remote_hash_res.stdout.strip()
        result["remote"] = remote_hash

        if remote_hash and local_hash:
            rev_count = subprocess.run(
                ["git", "-C", str(repo), "rev-list", "--count", "HEAD..origin/main"],
                capture_output=True,
                text=True,
                check=True,
            )
            behind = int(rev_count.stdout.strip() or "0")
            result["behind"] = behind
            result["available"] = behind > 0
    except (subprocess.SubprocessError, OSError, ValueError) as e:
        if not result["error"]:
            result["error"] = f"git rev-list failed: {e}"

    write_cache(cache_file, result)
    return result


def perform_update(
    repo_dir: Path | None = None,
    force: bool = False,
) -> tuple[int, str]:
    """Execute update by pulling latest origin/main into repository."""
    repo = repo_dir or _repo_dir()
    git_dir = repo / ".git"
    if not git_dir.exists():
        return 1, f"ziro: {repo} is not a git repository"

    # Check for uncommitted changes in tracked files
    status_res = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain", "-uno"],
        capture_output=True,
        text=True,
    )
    if status_res.stdout.strip() and not force:
        return 1, "ziro: working directory has uncommitted tracked changes. Stash or commit before updating (or pass --force)."

    try:
        # Fetch
        subprocess.run(
            ["git", "-C", str(repo), "fetch", "-q", "origin", "main"],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )
        # Pull ff-only
        pull_res = subprocess.run(
            ["git", "-C", str(repo), "pull", "--ff-only", "origin", "main"],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )

        # Update cache to indicate no pending updates
        cache_d = _cache_dir()
        cache_file = cache_d / "update-check.json"
        notify_flag = cache_d / ".update_notified"
        try:
            notify_flag.unlink(missing_ok=True)
        except OSError:
            pass

        new_hash_res = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
        )
        new_hash = new_hash_res.stdout.strip() or "HEAD"

        write_cache(
            cache_file,
            {
                "available": False,
                "local": new_hash,
                "remote": new_hash,
                "behind": 0,
                "checked_at": int(time.time()),
                "error": None,
            },
        )
        msg = f"Ziro Shell updated successfully to {new_hash}.\n{pull_res.stdout.strip()}"
        return 0, msg
    except subprocess.CalledProcessError as e:
        err = e.stderr.strip() if e.stderr else str(e)
        return 1, f"ziro: update failed: {err}"
    except (subprocess.SubprocessError, OSError) as e:
        return 1, f"ziro: update error: {e}"


def cmd_update(argv: list[str]) -> int:
    from core.help_cli import handle_help_if_requested
    ret = handle_help_if_requested(argv, "update")
    if ret is not None:
        return ret

    check_only = False
    force = False
    quiet = False

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--check", "-c"):
            check_only = True
        elif arg in ("--force", "-f"):
            force = True
        elif arg in ("--quiet", "-q"):
            quiet = True
        elif arg in ("--help", "-h"):
            from core.help_cli import handle_help_if_requested
            return handle_help_if_requested(["--help"], "update") or 0
        else:
            print(f"ziro update: unrecognized option '{arg}'", file=sys.stderr)
            return 2
        i += 1

    repo = _repo_dir()

    if check_only:
        res = check_update(repo, fetch=True)
        if res.get("error"):
            print(f"ziro update check: {res['error']}", file=sys.stderr)
            return 1
        if res.get("available"):
            behind = res.get("behind", 1)
            print(f"Update available: {behind} commit(s) behind origin/main. Run 'ziro update' to apply.")
            return 0
        short_local = (res.get("local") or "current")[:7]
        print(f"Ziro Shell is up to date ({short_local}).")
        return 0

    code, msg = perform_update(repo, force=force)
    if code == 0:
        if not quiet:
            print(f"✅ {msg}")
    else:
        print(msg, file=sys.stderr)
    return code


def main(argv: list[str] | None = None) -> int:
    return cmd_update(argv or sys.argv[1:])
