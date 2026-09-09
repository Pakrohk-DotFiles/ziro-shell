"""Platform detection: OS, distro, package manager, privileges, capabilities.

Everything is probed at runtime. No assumptions about username, HOME,
hostname, distro, or absolute tool paths.
"""

import os
import shutil
import sys
from dataclasses import dataclass, field


@dataclass
class Platform:
    os_name: str = "Unknown"          # macOS / Arch / Debian/Ubuntu / Fedora / Alpine / openSUSE / Windows-MSYS / Linux / Unknown
    pkg_mgr: str = ""                 # brew / pacman / apt / dnf / apk / zypper
    pkg_install: list[str] = field(default_factory=list)
    sudo: str | None = None
    is_root: bool = False
    non_interactive: bool = False
    distro_like: str = ""

    @property
    def has_pkg_manager(self) -> bool:
        return bool(self.pkg_mgr)


def _detect_os() -> tuple[str, str]:
    if sys.platform.startswith("darwin"):
        return "macOS", ""
    if sys.platform.startswith("win"):
        return "Windows-MSYS", ""
    # Linux (or WSL/MSYS reporting Linux)
    if os.path.isfile("/etc/arch-release"):
        return "Arch", ""
    if os.path.isfile("/etc/debian_version"):
        return "Debian/Ubuntu", ""
    if os.path.isfile("/etc/fedora-release"):
        return "Fedora", ""
    if os.path.isfile("/etc/alpine-release"):
        return "Alpine", ""
    if os.path.isfile("/etc/os-release"):
        fields: dict[str, str] = {}
        try:
            with open("/etc/os-release", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if "=" in line:
                        k, _, v = line.partition("=")
                        fields[k.strip()] = v.strip().strip('"')
        except OSError:
            pass
        distro_id = fields.get("ID", "")
        like = fields.get("ID_LIKE", "")
        if distro_id.startswith("opensuse") or "suse" in like:
            return "openSUSE", like
        if "debian" in like or distro_id in ("ubuntu", "mint", "pop"):
            return "Debian/Ubuntu", like
        if "fedora" in like or distro_id in ("rhel", "centos"):
            return "Fedora", like
        if "arch" in like:
            return "Arch", like
        if "alpine" in like:
            return "Alpine", like
        return "Linux", like
    return "Linux", ""


def _pkg_manager(os_name: str) -> tuple[str, list[str]]:
    """Detect the package manager by probing PATH (order matters)."""
    from shutil import which

    if which("brew"):
        return "brew", ["brew", "install"]
    if which("pacman"):
        return "pacman", ["pacman", "-Sy", "--needed", "--noconfirm"]
    if which("apt-get") or which("apt"):
        return "apt", ["apt-get", "install", "-y",
                       "-o", "Dpkg::Options::=--force-confdef",
                       "-o", "Dpkg::Options::=--force-confold"]
    if which("dnf"):
        return "dnf", ["dnf", "install", "-y"]
    if which("apk"):
        return "apk", ["apk", "add"]
    if which("zypper"):
        return "zypper", ["zypper", "--non-interactive", "install"]
    return "", []


def detect() -> Platform:
    p = Platform()
    p.os_name, p.distro_like = _detect_os()
    p.pkg_mgr, p.pkg_install = _pkg_manager(p.os_name)
    p.is_root = hasattr(os, "geteuid") and os.geteuid() == 0

    if not p.is_root and shutil.which("sudo"):
        p.sudo = "sudo"

    if os.path.isfile("/.dockerenv") or os.environ.get("CI") or not os.isatty(0):
        p.non_interactive = True
    return p


def find_tool(name: str) -> str | None:
    """Return absolute path of tool, or None."""
    return shutil.which(name)


def zsh_path() -> str | None:
    """Preferred zsh path for chsh."""
    if sys.platform.startswith("darwin") and os.path.isfile("/bin/zsh"):
        return "/bin/zsh"
    return find_tool("zsh")
