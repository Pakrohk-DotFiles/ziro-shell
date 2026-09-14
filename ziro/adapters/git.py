"""Thin compatibility adapter over the existing ziro.gitops module.

Delegates 1:1; no behavior lives here. Git workflows in later phases depend
on the GitPort protocol instead of importing gitops directly.
"""

from __future__ import annotations

from pathlib import Path

from .. import gitops


class GitOpsAdapter:
    def available(self) -> bool:
        return gitops.git_available()

    def is_repo(self, path: Path) -> bool:
        return gitops.is_repo(path)

    def is_ziro_repo(self, path: Path) -> bool:
        return gitops.is_ziro_repo(path)

    def origin_kind(self, path: Path) -> str | None:
        return gitops.origin_kind(path)

    def heal_origin(self, path: Path) -> bool:
        return gitops.heal_origin(path)

    def clone(self, url: str, dest: Path, depth: int | None = None) -> None:
        gitops.clone(url, dest, depth)

    def pull_ff_only(self, path: Path) -> bool:
        return gitops.pull_ff_only(path)

    def has_uncommitted_changes(self, path: Path) -> bool:
        return gitops.has_uncommitted_changes(path)

    def stash(self, path: Path) -> bool:
        return gitops.stash(path)

    def stash_pop(self, path: Path) -> bool:
        return gitops.stash_pop(path)

    def migrate_legacy(self, home: Path, dry_run: bool = False) -> tuple[Path, bool]:
        return gitops.migrate_legacy(home, dry_run=dry_run)
