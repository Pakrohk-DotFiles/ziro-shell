"""Legacy migration logic. Pure decisions, no I/O."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


LEGACY_DIR = ".zsh_config"
NEW_DIR = ".ziro"


class MigrationStatus(str, Enum):
    NOT_NEEDED = "not-needed"
    MIGRATED = "migrated"
    DRY_RUN = "dry-run"
    BOTH_EXIST = "both-exist"
    MIGRATION_FAILED = "migration-failed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class MigrationResult:
    status: MigrationStatus
    config_dir: Path
    message: str = ""


def compute_migration(
    home: Path,
    *,
    new_exists: callable,
    legacy_exists: callable,
    new_is_repo: callable,
    dry_run: bool,
) -> MigrationResult:
    new = home / NEW_DIR
    legacy = home / LEGACY_DIR

    new_exists_flag = new_exists(new)
    legacy_exists_flag = legacy_exists(legacy)

    if legacy_exists_flag and not new_exists_flag:
        if dry_run:
            return MigrationResult(MigrationStatus.DRY_RUN, legacy, f"Would migrate {legacy} -> {new}")
        return MigrationResult(MigrationStatus.MIGRATED, new, f"Migrated {legacy} -> {new}")

    if legacy_exists_flag and new_exists_flag and new_is_repo(new):
        return MigrationResult(MigrationStatus.BOTH_EXIST, new, f"Both {new} and {legacy} exist")

    if new_exists_flag and not new_is_repo(new):
        return MigrationResult(MigrationStatus.BLOCKED, new, f"{new} exists and is not a Ziro repo")

    return MigrationResult(MigrationStatus.NOT_NEEDED, new)


def legacy_dir_name() -> str:
    return LEGACY_DIR


def new_dir_name() -> str:
    return NEW_DIR
