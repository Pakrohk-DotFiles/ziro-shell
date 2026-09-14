"""Subprocess process runner adapter. Wraps existing runner.py logic."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from subprocess import CompletedProcess

from ..ports.process import RunError


class SubprocessRunner:
    def run(self, cmd: Sequence[str], check: bool = True, **kwargs) -> CompletedProcess:
        cmd = [str(c) for c in cmd]
        kwargs.setdefault("text", True)
        try:
            proc = subprocess.run(cmd, **kwargs)
        except FileNotFoundError:
            if check:
                raise RunError(cmd, 127, f"executable not found: {cmd[0]}")
            return CompletedProcess(cmd, 127)
        if check and proc.returncode != 0:
            stderr = (proc.stderr or "") if isinstance(proc.stderr, str) else ""
            raise RunError(cmd, proc.returncode, stderr.strip())
        return proc

    def capture(self, cmd: Sequence[str], check: bool = True) -> str:
        return self.run(
            cmd, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).stdout.strip()

    def quiet(self, cmd: Sequence[str]) -> bool:
        return self.run(
            cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ).returncode == 0

    def sudo_prefix(self, sudo: str | None) -> list[str]:
        return [sudo] if sudo else []

    def report_failure(self, exc: RunError) -> None:
        from ..ui import get_ui
        ui = get_ui()
        ui.failed(f"`{' '.join(exc.cmd)}` exited {exc.returncode}")
        if exc.stderr:
            for line in exc.stderr.splitlines()[:5]:
                ui.error(f"  {line}")
