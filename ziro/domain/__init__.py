"""Domain models and policies. Pure logic, no I/O, no UI."""

from .config import (
    LANG_OPTIONS,
    MANAGED_CONFIGS,
    MANAGED_FRAMEWORKS,
    SHELL_OPTIONS,
    SELECTION_BY_ATTR,
    SELECTION_BY_KEY,
    append_to_zshrc_local,
    extract_env_from_zshrc_local,
    patch_zsh_config_dir,
    render_zshrc_local,
    strip_legacy_lines,
)
from .install import (
    BackupScope,
    InstallRequest,
    InstallResult,
    InstallStrategy,
    backup_manager_configs,
    backup_manager_frameworks,
    backup_manager_name,
    default_backup_scope,
    strategy_for_update,
)
from .migration import (
    MigrationResult,
    MigrationStatus,
    compute_migration,
    legacy_dir_name,
    new_dir_name,
)
from .platform import (
    Platform,
    is_server_mode,
    zsh_path_for,
)
from .packages import (
    packages_for,
)
from .paths import (
    ZSH_COMPILE_TARGETS,
    ensure_local_bin_on_path_block,
    local_bin_guard_block,
    local_bin_path_marker,
    zshenv_path_block,
)
from .theme import (
    REQUIRED_THEME_FIELDS,
    ThemePackage,
    ThemeValidationError,
    discover_themes,
    get_default_theme,
    parse_theme_meta,
    starship_config_path,
    starship_files_identical,
    validate_theme,
)
from .doctor import (
    Check,
    check_config_dir,
    check_default_shell,
    check_fzf,
    check_git,
    check_gh,
    check_plugins,
    check_python3,
    check_remote_origin,
    check_starship,
    check_starship_toml,
    check_znap,
    check_zsh,
    check_zshrc_local,
    check_zshrc_symlink,
)
from .update import UpdateResult, UpdateStatus

__all__ = [
    "BackupScope", "Check", "InstallRequest", "InstallResult", "InstallStrategy",
    "LANG_OPTIONS", "MANAGED_CONFIGS", "MANAGED_FRAMEWORKS", "MigrationResult",
    "MigrationStatus", "Platform", "REQUIRED_THEME_FIELDS", "SELECTION_BY_ATTR",
    "SELECTION_BY_KEY", "SHELL_OPTIONS", "ThemePackage", "ThemeValidationError",
    "UpdateResult", "UpdateStatus",
    "ZSH_COMPILE_TARGETS", "append_to_zshrc_local", "backup_manager_configs",
    "backup_manager_frameworks", "backup_manager_name", "check_config_dir",
    "check_default_shell", "check_fzf", "check_gh", "check_git", "check_plugins",
    "check_python3", "check_remote_origin", "check_starship", "check_starship_toml",
    "check_znap", "check_zsh", "check_zshrc_local", "check_zshrc_symlink",
    "compute_migration", "default_backup_scope", "discover_themes",
    "ensure_local_bin_on_path_block", "extract_env_from_zshrc_local",
    "get_default_theme", "is_server_mode", "legacy_dir_name",
    "local_bin_guard_block", "local_bin_path_marker", "new_dir_name",
    "packages_for", "parse_theme_meta", "patch_zsh_config_dir",
    "render_zshrc_local", "starship_config_path", "starship_files_identical",
    "strategy_for_update", "strip_legacy_lines", "validate_theme",
    "zsh_path_for", "zshenv_path_block",
]
