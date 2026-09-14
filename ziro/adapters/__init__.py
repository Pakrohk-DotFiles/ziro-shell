"""Adapters: concrete implementations of ports. Also compatibility shims."""

from .git import GitOpsAdapter
from .platform import ShellAdapter
from .process import SubprocessRunner

__all__ = ["GitOpsAdapter", "ShellAdapter", "SubprocessRunner"]
