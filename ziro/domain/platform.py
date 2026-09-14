"""Platform detection models. Pure data, no I/O (detection in adapters)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Platform:
    os_name: str = "Unknown"
    pkg_mgr: str = ""
    pkg_install: list[str] = field(default_factory=list)
    sudo: str | None = None
    is_root: bool = False
    non_interactive: bool = False
    distro_like: str = ""

    @property
    def has_pkg_manager(self) -> bool:
        return bool(self.pkg_mgr)


def is_server_mode(platform: Platform) -> bool:
    return platform.is_root


def zsh_path_for(platform: Platform) -> str | None:
    import sys
    import shutil
    if sys.platform.startswith("darwin") and __import__("os").path.isfile("/bin/zsh"):
        return "/bin/zsh"
    return shutil.which("zsh")
