"""Thin compatibility adapter over the existing ziro.platform module."""

from __future__ import annotations

import os

from .. import platform as platform_mod


class ShellAdapter:
    def zsh_path(self) -> str | None:
        return platform_mod.zsh_path()

    def find_tool(self, name: str) -> str | None:
        return platform_mod.find_tool(name)

    def current_shell(self) -> str:
        return os.environ.get("SHELL", "")
