"""Application workflow contracts. Interfaces only, no I/O."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from ..domain.doctor import Check
from ..domain.install import InstallRequest, InstallResult
from ..domain.theme import ThemePackage
from ..domain.update import UpdateResult


class InstallWorkflow(Protocol):
    def run(self, request: InstallRequest) -> InstallResult: ...


class UpdateWorkflow(Protocol):
    def run(self) -> UpdateResult: ...


class DoctorWorkflow(Protocol):
    def run(self) -> list[Check]: ...


class ThemeWorkflow(Protocol):
    def list_themes(self) -> list[ThemePackage]: ...

    def current_theme(self) -> str | None: ...

    def apply_theme(self, name: str, force: bool = False) -> int: ...
