"""Per-distro package maps (ported verbatim from install.sh)."""

from .platform import Platform


def packages_for(
    platform_: Platform,
    mode: str,
    enable_python: bool,
    enable_rust: bool,
    enable_go: bool,
    enable_node: bool,
) -> tuple[list[str], list[str]]:
    """Return (base_pkgs, extra_pkgs) without sudo/install-command."""
    os_name = platform_.os_name
    base: list[str] = ["zsh", "git", "curl", "fzf"]
    extra: list[str] = []
    lang: list[str] = []

    # --- language packages ---
    # Starship always (except MSYS where native package may not exist)
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

    elif os_name == "Alpine":
        extra = ["p7zip", "unzip"]

    elif os_name == "openSUSE":
        extra = ["p7zip", "unzip"]

    elif os_name == "Windows-MSYS":
        extra = ["unzip", "p7zip"]

    base += lang

    # --- server-mode extras ---
    if mode == "Server":
        server_net = ["nload", "iftop", "nmap", "iperf3", "tcpdump", "mtr", "duf"]
        if os_name == "Debian/Ubuntu":
            server_net = ["nload", "iftop", "nmap", "iperf3", "tcpdump", "mtr-tiny", "duf"]
        base += server_net

    return base, extra
