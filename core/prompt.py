"""ziro-shell — prompt layer (T1).

Layer: 3 (Python core, cold-path only)
Spec: 006
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SUPPORTED_PROMPTS = ("starship", "powerlevel10k", "pure", "none")
DEFAULT_PROMPT = "starship"


@dataclass(frozen=True)
class PromptConfig:
    name: str
    adapter_path: Path
    theme_supported: bool = False


def read_prompt_conf(config_dir: Path) -> str:
    """Read active prompt name from prompt.conf. Empty → 'none'."""
    conf = config_dir / "prompt.conf"
    if not conf.is_file():
        return DEFAULT_PROMPT
    try:
        line = conf.read_text().strip().splitlines()[0]
    except (OSError, IndexError):
        return DEFAULT_PROMPT
    name = line.strip().lower()
    if not name:
        return "none"
    if name not in SUPPORTED_PROMPTS:
        return DEFAULT_PROMPT
    return name


def write_prompt_conf(config_dir: Path, name: str) -> None:
    """Write prompt name to prompt.conf."""
    if name not in SUPPORTED_PROMPTS:
        raise ValueError(f"Unsupported prompt: {name}. Choose from {SUPPORTED_PROMPTS}")
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "prompt.conf").write_text(name + "\n")


def resolve_prompt(config_dir: Path, prompts_dir: Path) -> PromptConfig:
    """Resolve active prompt to adapter file path."""
    name = read_prompt_conf(config_dir)
    adapter = prompts_dir / f"{name}.zsh"
    theme_supported = name == "starship"
    return PromptConfig(
        name=name,
        adapter_path=adapter,
        theme_supported=theme_supported,
    )


def list_prompts(prompts_dir: Path) -> list[str]:
    """List available prompt adapters."""
    if not prompts_dir.is_dir():
        return []
    return sorted(p.stem for p in prompts_dir.glob("*.zsh"))


__all__ = [
    "PromptConfig",
    "SUPPORTED_PROMPTS",
    "DEFAULT_PROMPT",
    "read_prompt_conf",
    "write_prompt_conf",
    "resolve_prompt",
    "list_prompts",
]
