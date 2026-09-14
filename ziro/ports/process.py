"""Process execution port. Protocol only, no implementation."""

from __future__ import annotations

from collections.abc import Sequence
from subprocess import CompletedProcess
from typing import Protocol


class RunError(Exception):
    def __init__(self, cmd: Sequence[str], returncode: int, stderr: str) -> None:
        self.cmd = list(cmd)
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"command failed ({returncode}): {' '.join(self.cmd)}")


class ProcessRunner(Protocol):
    def run(self, cmd: Sequence[str], check: bool = True, **kwargs) -> CompletedProcess: ...

    def capture(self, cmd: Sequence[str], check: bool = True) -> str: ...

    def quiet(self, cmd: Sequence[str]) -> bool: ...

    def sudo_prefix(self, sudo: str | None) -> list[str]: ...

    def report_failure(self, exc: RunError) -> None: ...
