"""Install strategies and request/result models. Pure data, no I/O."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class InstallStrategy(str, Enum):
    FULL_OVERWRITE = "full-overwrite"
    FULL_OVERWRITE_WITH_BACKUP = "full-overwrite-with-backup"
    UPDATE = "update"


@dataclass
class InstallRequest:
    strategy: InstallStrategy = InstallStrategy.FULL_OVERWRITE_WITH_BACKUP
    mode: str | None = None
    skip_deps: bool = False
    skip_shell: bool = False
    force: bool = False
    dry_run: bool = False
    non_interactive: bool = False
    theme: str | None = None
    enabled_features: dict[str, bool | None] = field(default_factory=dict)


@dataclass
class InstallResult:
    success: bool
    config_dir: str | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class BackupScope:
    managed: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)


def default_backup_scope(managed_configs: tuple[str, ...], managed_frameworks: tuple[str, ...]) -> BackupScope:
    return BackupScope(
        managed=list(managed_configs),
        frameworks=list(managed_frameworks),
    )


def backup_manager_configs(home_exists: callable, managed_configs: tuple[str, ...]) -> list[str]:
    return [c for c in managed_configs if home_exists(f".{c}")]


def backup_manager_frameworks(home_exists: callable, managed_frameworks: tuple[str, ...]) -> list[str]:
    return [f for f in managed_frameworks if home_exists(f)]


def backup_manager_name() -> str:
    from time import strftime
    return f".bak.{strftime('%Y%m%d%H%M%S')}"


def strategy_for_update() -> InstallStrategy:
    return InstallStrategy.UPDATE
