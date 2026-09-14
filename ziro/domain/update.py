"""Update flow models. Pure data, no I/O.

Maps the branches of the existing updater.update() flow onto a typed result
so the CLI (and later application layer) can decide exit codes without
re-reading git internals.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class UpdateStatus(str, Enum):
    UPDATED = "updated"
    UP_TO_DATE = "up-to-date"
    NO_REPO = "no-repo"
    FOREIGN_ORIGIN = "foreign-origin"
    PULL_FAILED = "pull-failed"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class UpdateResult:
    status: UpdateStatus
    config_dir: Path | None = None
    message: str = ""

    @property
    def ok(self) -> bool:
        return self.status in (UpdateStatus.UPDATED, UpdateStatus.UP_TO_DATE)

    @property
    def exit_code(self) -> int:
        return 0 if self.ok else 1
