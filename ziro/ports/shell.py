"""Shell environment port. Protocol only, no implementation."""

from __future__ import annotations

from typing import Protocol


class ShellPort(Protocol):
    def zsh_path(self) -> str | None: ...

    def find_tool(self, name: str) -> str | None: ...

    def current_shell(self) -> str: ...
