"""Focused unit tests for IOP domain contracts."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from textwrap import dedent

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ziro.domain.config import (
    LANG_OPTIONS, SHELL_OPTIONS, SELECTION_BY_KEY, MANAGED_CONFIGS, MANAGED_FRAMEWORKS,
    extract_env_from_zshrc_local, render_zshrc_local, strip_legacy_lines,
    patch_zsh_config_dir, append_to_zshrc_local,
)
from ziro.domain.install import (
    InstallStrategy, InstallRequest, InstallResult, BackupScope,
    backup_manager_name, strategy_for_update,
)
from ziro.domain.migration import (
    MigrationStatus, compute_migration, legacy_dir_name, new_dir_name,
)
from ziro.domain.platform import Platform, is_server_mode
from ziro.domain.packages import packages_for
from ziro.domain.paths import (
    ZSH_COMPILE_TARGETS, ensure_local_bin_on_path_block, local_bin_path_marker,
    local_bin_guard_block, zshenv_path_block,
)
from ziro.domain.theme import (
    ThemePackage, ThemeValidationError, validate_theme, SEMVER_RE, REQUIRED_THEME_FIELDS,
    THEMES_DIR, DEFAULT_THEME, starship_config_path,
)
from ziro.domain.doctor import (
    Check, check_zsh, check_git, check_python3, check_fzf, check_starship,
    check_gh, check_config_dir, check_zshrc_symlink, check_default_shell,
    check_znap, check_plugins, check_remote_origin, check_zshrc_local,
    check_starship_toml,
)
from ziro.domain.packages import packages_for


# ── Config tests ─────────────────────────────────────────────────────────────

class TestSelectionTables(unittest.TestCase):
    def test_lang_count(self):
        self.assertEqual(len(LANG_OPTIONS), 4)

    def test_shell_count(self):
        self.assertEqual(len(SHELL_OPTIONS), 8)

    def test_by_key_complete(self):
        all_options = LANG_OPTIONS + SHELL_OPTIONS
        self.assertEqual(len(SELECTION_BY_KEY), len(all_options))
        for opt in all_options:
            self.assertIn(opt.env_key, SELECTION_BY_KEY)
            self.assertIs(SELECTION_BY_KEY[opt.env_key], opt)

    def test_managed_configs(self):
        self.assertIn("zshrc", MANAGED_CONFIGS)

    def test_managed_frameworks(self):
        self.assertIn(".oh-my-zsh", MANAGED_FRAMEWORKS)


class TestExtractEnv(unittest.TestCase):
    def test_basic_yes_no(self):
        text = "export ENABLE_RUST='yes'\nexport ENABLE_PYTHON='no'\n"
        result = extract_env_from_zshrc_local(text)
        self.assertTrue(result["ENABLE_RUST"])
        self.assertFalse(result["ENABLE_PYTHON"])

    def test_unknown_key_ignored(self):
        text = "export EDITOR=vim\nexport ENABLE_GO='true'\n"
        result = extract_env_from_zshrc_local(text)
        self.assertNotIn("EDITOR", result)
        self.assertTrue(result["ENABLE_GO"])

    def test_empty_text(self):
        self.assertEqual(extract_env_from_zshrc_local(""), {})


class TestRenderZshrcLocal(unittest.TestCase):
    def test_render_preserves_custom_lines(self):
        existing = "export FOO=bar\nexport ENABLE_RUST='yes'\n"
        result = render_zshrc_local(existing, {"ENABLE_RUST": "no", "ENABLE_PYTHON": "yes"})
        self.assertIn("FOO=bar", result)
        self.assertIn("ENABLE_PYTHON='yes'", result)

    def test_render_uses_existing_values(self):
        existing = "export ENABLE_GO='yes'\n"
        result = render_zshrc_local(existing, {"ENABLE_GO": "no"})
        self.assertIn("ENABLE_GO='yes'", result)


class TestStripLegacy(unittest.TestCase):
    def test_strips_legacy(self):
        text = "line1\nznap fpath _rustup 'rustup completions zsh'\nline2\n"
        result = strip_legacy_lines(text)
        self.assertNotIn("znap fpath", result)
        self.assertIn("line1", result)


class TestPatchZshConfigDir(unittest.TestCase):
    def test_patch(self):
        self.assertEqual(patch_zsh_config_dir("ZSH_CONFIG_DIR=~/.zsh_config", ".zsh_config", ".ziro"),
                         "ZSH_CONFIG_DIR=~/.ziro")


# ── Install tests ────────────────────────────────────────────────────────────

class TestInstallStrategy(unittest.TestCase):
    def test_update_strategy(self):
        self.assertEqual(strategy_for_update(), InstallStrategy.UPDATE)

    def test_backup_name_format(self):
        name = backup_manager_name()
        self.assertTrue(name.startswith(".bak."))
        self.assertEqual(len(".bak."), 5)

    def test_install_request_defaults(self):
        req = InstallRequest()
        self.assertEqual(req.strategy, InstallStrategy.FULL_OVERWRITE_WITH_BACKUP)
        self.assertIsNone(req.mode)
        self.assertFalse(req.skip_deps)

    def test_install_result(self):
        r = InstallResult(success=True)
        self.assertTrue(r.success)
        self.assertEqual(r.errors, [])


# ── Migration tests ──────────────────────────────────────────────────────────

class TestMigration(unittest.TestCase):
    def test_dir_names(self):
        self.assertEqual(legacy_dir_name(), ".zsh_config")
        self.assertEqual(new_dir_name(), ".ziro")

    def test_both_exist(self):
        result = compute_migration(
            Path("/tmp/test"),
            new_exists=lambda p: True,
            legacy_exists=lambda p: True,
            new_is_repo=lambda p: True,
            dry_run=False,
        )
        self.assertEqual(result.status, MigrationStatus.BOTH_EXIST)

    def test_not_needed(self):
        result = compute_migration(
            Path("/tmp/test"),
            new_exists=lambda p: False,
            legacy_exists=lambda p: False,
            new_is_repo=lambda p: False,
            dry_run=False,
        )
        self.assertEqual(result.status, MigrationStatus.NOT_NEEDED)

    def test_blocked(self):
        result = compute_migration(
            Path("/tmp/test"),
            new_exists=lambda p: True,
            legacy_exists=lambda p: True,
            new_is_repo=lambda p: False,
            dry_run=False,
        )
        self.assertEqual(result.status, MigrationStatus.BLOCKED)


# ── Platform tests ───────────────────────────────────────────────────────────

class TestPlatform(unittest.TestCase):
    def test_default(self):
        p = Platform()
        self.assertEqual(p.os_name, "Unknown")
        self.assertFalse(p.has_pkg_manager)

    def test_with_pkg_mgr(self):
        p = Platform(os_name="Arch", pkg_mgr="pacman", pkg_install=["pacman", "-Sy"])
        self.assertTrue(p.has_pkg_manager)

    def test_is_server_mode(self):
        self.assertTrue(is_server_mode(Platform(is_root=True)))
        self.assertFalse(is_server_mode(Platform(is_root=False)))


# ── Package tests ────────────────────────────────────────────────────────────

class TestPackages(unittest.TestCase):
    def test_arch_python_present(self):
        p = Platform(os_name="Arch", pkg_mgr="pacman")
        base, _ = packages_for(p, "Desktop", True, False, False, False)
        self.assertIn("python", base)
        self.assertNotIn("rustup", base)

    def test_arch_no_python_absent(self):
        p = Platform(os_name="Arch", pkg_mgr="pacman")
        base, _ = packages_for(p, "Desktop", False, False, False, False)
        self.assertNotIn("python", base)

    def test_arch_rust_present(self):
        p = Platform(os_name="Arch", pkg_mgr="pacman")
        base, _ = packages_for(p, "Desktop", False, True, False, False)
        self.assertIn("rustup", base)

    def test_core_packages_always(self):
        p = Platform(os_name="Arch", pkg_mgr="pacman")
        base, _ = packages_for(p, "Desktop", False, False, False, False)
        for pkg in ("zsh", "git", "curl", "fzf", "starship"):
            self.assertIn(pkg, base, f"{pkg} missing from base")

    def test_server_net_packages(self):
        p = Platform(os_name="Arch", pkg_mgr="pacman")
        base, _ = packages_for(p, "Server", False, False, False, False)
        self.assertIn("nmap", base)
        self.assertIn("iftop", base)

    def test_debian_python_packages(self):
        p = Platform(os_name="Debian/Ubuntu", pkg_mgr="apt")
        base, _ = packages_for(p, "Desktop", True, False, False, False)
        self.assertIn("python3", base)
        self.assertIn("python3-venv", base)


# ── Path tests ───────────────────────────────────────────────────────────────

class TestPaths(unittest.TestCase):
    def test_compile_targets(self):
        self.assertIn(".zshrc", ZSH_COMPILE_TARGETS)
        self.assertIn("znap", ZSH_COMPILE_TARGETS)

    def test_ensure_path_idempotent(self):
        existing = "some content\n"
        result1, added1 = ensure_local_bin_on_path_block(existing)
        self.assertTrue(added1)
        result2, added2 = ensure_local_bin_on_path_block(result1)
        self.assertFalse(added2)

    def test_marker_in_guard(self):
        marker = local_bin_path_marker()
        guard = local_bin_guard_block()
        self.assertIn("PATH", guard)
        self.assertTrue(marker.startswith("#"))


# ── Theme tests ──────────────────────────────────────────────────────────────

class TestTheme(unittest.TestCase):
    def test_valid_theme(self):
        data = {"theme": {"name": "test", "version": "1.0.0", "description": "A test",
                          "author": "me", "license": "MIT"}}
        pkg = validate_theme(data, Path("/tmp/test"))
        self.assertIsNotNone(pkg)
        self.assertEqual(pkg.name, "test")
        self.assertEqual(pkg.version, "1.0.0")

    def test_missing_section(self):
        self.assertIsNone(validate_theme({"name": "x"}, Path("/tmp")))

    def test_missing_field(self):
        data = {"theme": {"name": "x", "version": "1.0.0"}}
        self.assertIsNone(validate_theme(data, Path("/tmp")))

    def test_empty_name(self):
        data = {"theme": {"name": "", "version": "1.0.0", "description": "x",
                          "author": "x", "license": "MIT"}}
        self.assertIsNone(validate_theme(data, Path("/tmp")))

    def test_bad_version(self):
        data = {"theme": {"name": "x", "version": "latest", "description": "x",
                          "author": "x", "license": "MIT"}}
        self.assertIsNone(validate_theme(data, Path("/tmp")))

    def test_name_mismatch(self):
        data = {"theme": {"name": "alpha", "version": "1.0.0", "description": "x",
                          "author": "x", "license": "MIT"}}
        pkg = validate_theme(data, Path("/tmp/beta"))
        self.assertIsNone(pkg)

    def test_default_theme(self):
        self.assertEqual(DEFAULT_THEME, "lambda")

    def test_required_fields(self):
        self.assertEqual(REQUIRED_THEME_FIELDS, {"name", "version", "description", "author", "license"})


# ── Doctor tests ─────────────────────────────────────────────────────────────

class TestDoctor(unittest.TestCase):
    def test_zsh_present(self):
        c = check_zsh("/usr/bin/zsh")
        self.assertTrue(c.ok)
        self.assertEqual(c.detail, "/usr/bin/zsh")

    def test_zsh_missing(self):
        c = check_zsh(None)
        self.assertFalse(c.ok)

    def test_fzf_missing_warn(self):
        c = check_fzf(None)
        self.assertFalse(c.ok)
        self.assertTrue(c.warn)

    def test_gh_optional(self):
        c = check_gh(None)
        self.assertTrue(c.ok)

    def test_config_dir_legacy(self):
        c = check_config_dir(Path("/home/u/.zsh_config"), False, ".zsh_config")
        self.assertFalse(c.ok)

    def test_default_shell_zsh(self):
        c = check_default_shell("/usr/bin/zsh")
        self.assertTrue(c.ok)

    def test_plugins_present(self):
        c = check_plugins(Path("/tmp"), ["fast-syntax-highlighting", "zsh-autosuggestions", "zsh-completions"])
        self.assertTrue(c.ok)

    def test_plugins_missing_warn(self):
        c = check_plugins(Path("/tmp"), [])
        self.assertFalse(c.ok)
        self.assertTrue(c.warn)


if __name__ == "__main__":
    unittest.main()
