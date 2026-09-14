"""Ports: side-effect interfaces. Protocols and ABCs only, no implementations."""

from .filesystem import FileSystem
from .git import GitPort
from .pkg import PackageManager
from .process import ProcessRunner, RunError
from .shell import ShellPort
from .ui import ConsoleUI

__all__ = [
    "ConsoleUI", "FileSystem", "GitPort", "PackageManager",
    "ProcessRunner", "RunError", "ShellPort",
]
