"""Subprocess execution: argument arrays only, never shell=True."""

import subprocess
from collections.abc import Sequence

from . import ui


class RunError(Exception):
    def __init__(self, cmd: Sequence[str], returncode: int, stderr: str) -> None:
        self.cmd = list(cmd)
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"command failed ({returncode}): {' '.join(self.cmd)}")


def run(cmd: Sequence[str], check: bool = True, **kwargs) -> subprocess.CompletedProcess:
    """Run cmd; on check=True raise RunError with captured stderr."""
    cmd = [str(c) for c in cmd]
    kwargs.setdefault("text", True)
    try:
        proc = subprocess.run(cmd, **kwargs)
    except FileNotFoundError:
        if check:
            raise RunError(cmd, 127, f"executable not found: {cmd[0]}")
        return subprocess.CompletedProcess(cmd, 127)
    if check and proc.returncode != 0:
        stderr = (proc.stderr or "") if isinstance(proc.stderr, str) else ""
        raise RunError(cmd, proc.returncode, stderr.strip())
    return proc


def capture(cmd: Sequence[str], check: bool = True) -> str:
    """Run cmd and return stripped stdout."""
    return run(cmd, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.strip()


def quiet(cmd: Sequence[str], timeout: float | None = None) -> bool:
    """Run cmd, return True on exit code 0 or timeout (all output discarded).

    Interactive zsh can hang without `exit 0` in its command string (it grabs
    the tty after the -c code), and first-run plugin clones hit the network,
    so callers probing a user shell should pass a timeout.
    """
    try:
        proc = run(cmd, check=False, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False
    return proc.returncode == 0


def sudo_prefix(sudo: str | None) -> list[str]:
    return [sudo] if sudo else []


def report_failure(exc: RunError) -> None:
    ui.failed(f"`{' '.join(exc.cmd)}` exited {exc.returncode}")
    if exc.stderr:
        for line in exc.stderr.splitlines()[:5]:
            ui.error(f"  {line}")
