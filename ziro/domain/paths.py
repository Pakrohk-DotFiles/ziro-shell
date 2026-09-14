"""Path constants and path helpers. Pure logic, no I/O."""

from __future__ import annotations

ZSH_COMPILE_TARGETS = (
    ".zshrc", ".zsh_aliases", ".zsh_update.zsh", ".paru_fzf.zsh", ".prompt.local",
    "znap", "zsh-users", "zdharma-continuum", "mfaerevaag", "djui", "rupa",
    "ohmyzsh", "marlonrichert",
)

LOCAL_BIN_PATH_MARKER = "# Add ~/.local/bin to PATH (set by ziro install)"
LOCAL_BIN_GUARD = '[[ ":$PATH:" != *":$HOME/.local/bin:"* ]] && export PATH="$HOME/.local/bin:$PATH"'

ZSHENV_BLOCK = """
# Add ~/.local/bin to PATH (set by ziro install)
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  export PATH="$HOME/.local/bin:$PATH"
fi
""".lstrip()


def ensure_local_bin_on_path_block(existing_text: str) -> tuple[str, bool]:
    if LOCAL_BIN_PATH_MARKER in existing_text or 'export PATH="$HOME/.local/bin' in existing_text:
        return existing_text, False
    block = f"\n{LOCAL_BIN_PATH_MARKER}\n{LOCAL_BIN_GUARD}\n"
    return existing_text + block, True


def local_bin_guard_block() -> str:
    return LOCAL_BIN_GUARD


def local_bin_path_marker() -> str:
    return LOCAL_BIN_PATH_MARKER


def zshenv_path_block() -> str:
    return ZSHENV_BLOCK
