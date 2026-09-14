"""Package selection policy. Pure logic, no I/O."""

from __future__ import annotations

from .platform import Platform


def packages_for(
    platform: Platform,
    mode: str,
    enable_python: bool | None,
    enable_rust: bool | None,
    enable_go: bool | None,
    enable_node: bool | None,
) -> tuple[list[str], list[str]]:
    os_name = platform.os_name
    base: list[str] = ["zsh", "git", "curl", "fzf"]
    extra: list[str] = []
    lang: list[str] = []

    if os_name != "Windows-MSYS":
        lang.append("starship")

    if os_name == "macOS":
        extra = ["p7zip", "unzip"]
        if enable_python:
            lang.append("python")

    elif os_name == "Arch":
        extra = ["base-devel", "reflector", "p7zip", "unzip"]
        if enable_python:
            lang.append("python")
        if enable_rust:
            lang.append("rustup")
        if enable_go:
            lang.append("go")
        if enable_node:
            lang += ["nodejs", "npm"]

    elif os_name == "Debian/Ubuntu":
        extra = ["p7zip-full", "unzip"]
        if enable_python:
            lang += ["python3", "python3-venv", "virtualenvwrapper"]
        if enable_node:
            lang += ["nodejs", "npm"]
        if enable_go:
            lang.append("golang-go")

    elif os_name == "Fedora":
        extra = ["p7zip", "unzip"]
        if enable_python:
            lang += ["python3", "python3-virtualenvwrapper"]
        if enable_node:
            lang += ["nodejs", "npm"]

    elif os_name in ("Alpine", "openSUSE", "Windows-MSYS"):
        extra = ["p7zip", "unzip"]

    base += lang

    if mode == "Server":
        server_net = ["nload", "iftop", "nmap", "iperf3", "tcpdump", "mtr", "duf"]
        if os_name == "Debian/Ubuntu":
            server_net = ["nload", "iftop", "nmap", "iperf3", "tcpdump", "mtr-tiny", "duf"]
        base += server_net

    return base, extra
