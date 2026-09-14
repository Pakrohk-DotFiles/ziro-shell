"""Package manager port. Protocol only, no implementation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from ..domain.platform import Platform


class PackageManager(Protocol):
    def detect(self) -> Platform: ...

    def install(self, platform: Platform, packages: Sequence[str], *, dry_run: bool = False) -> bool: ...
