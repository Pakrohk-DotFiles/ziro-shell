"""Installer flow contracts: overwrite preflight, managed theme file, PATH.

Runs offline in a temp HOME; no shell, no network, no sudo.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ziro import installer, themes  # noqa: E402
from ziro.installer import Options, _detect_conflicts, _preflight  # noqa: E402


class TestConflictDetection(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="ziro-conflict-"))
        self._orig_home = installer._home
        installer._home = lambda: self.home

    def tearDown(self):
        installer._home = self._orig_home
        shutil.rmtree(self.home)

    def test_clean_home_has_no_conflicts(self):
        self.assertEqual(_detect_conflicts(), [])

    def test_regular_files_and_framework_detected(self):
        (self.home / ".zshrc").write_text("# mine\n")
        (self.home / ".zprofile").write_text("# mine\n")
        (self.home / ".oh-my-zsh").mkdir()
        conflicts = _detect_conflicts()
        self.assertIn(".zshrc", conflicts)
        self.assertIn(".zprofile", conflicts)
        self.assertIn(".oh-my-zsh/", conflicts)

    def test_our_own_symlink_is_not_a_conflict(self):
        repo = self.home / ".ziro"
        repo.mkdir()
        (repo / ".zshrc").write_text("# ziro\n")
        (self.home / ".zshrc").symlink_to(repo / ".zshrc")
        self.assertEqual(_detect_conflicts(), [])

    def test_foreign_symlink_is_a_conflict(self):
        other = self.home / "other.zsh"
        other.write_text("# x\n")
        (self.home / ".zshrc").symlink_to(other)
        self.assertEqual(_detect_conflicts(), [".zshrc (symlink)"])


class TestPreflightDecision(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="ziro-pre-"))
        self._orig_home = installer._home
        installer._home = lambda: self.home

    def tearDown(self):
        installer._home = self._orig_home
        shutil.rmtree(self.home)

    def test_clean_home_proceeds_silently(self):
        self.assertTrue(_preflight(Options()))

    def test_conflicts_with_overwrite_proceeds(self):
        (self.home / ".zshrc").write_text("x\n")
        self.assertTrue(_preflight(Options(overwrite=True)))

    def test_no_overwrite_aborts(self):
        (self.home / ".zshrc").write_text("x\n")
        self.assertFalse(_preflight(Options(overwrite=False)))
        self.assertTrue((self.home / ".zshrc").is_file())  # aborted = untouched

    def test_non_interactive_defaults_to_replace(self):
        (self.home / ".zshrc").write_text("x\n")
        self.assertTrue(_preflight(Options(non_interactive=True)))

    def test_force_implies_replace(self):
        (self.home / ".zshrc").write_text("x\n")
        opts = Options(force=True, non_interactive=True)
        self.assertTrue(_preflight(opts))

    def test_dry_run_ask_path_proceeds_without_changes(self):
        (self.home / ".zshrc").write_text("keep me\n")
        self.assertTrue(_preflight(Options(dry_run=True, non_interactive=False)))
        self.assertEqual((self.home / ".zshrc").read_text(), "keep me\n")


class TestBackup(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="ziro-backup-"))
        self._orig_home = installer._home
        installer._home = lambda: self.home

    def tearDown(self):
        installer._home = self._orig_home
        shutil.rmtree(self.home)

    def test_files_share_one_timestamp_suffix(self):
        (self.home / ".zshrc").write_text("a\n")
        (self.home / ".zprofile").write_text("b\n")
        installer._backup_existing(Options())
        backups = sorted(p.name for p in self.home.glob("*.bak.*"))
        self.assertEqual(len(backups), 2)
        stamps = {n.split(".bak.")[1] for n in backups}
        self.assertEqual(len(stamps), 1, "all backups must share one suffix")
        self.assertFalse((self.home / ".zshrc").exists())

    def test_dry_run_changes_nothing(self):
        (self.home / ".zshrc").write_text("a\n")
        installer._backup_existing(Options(dry_run=True))
        self.assertEqual((self.home / ".zshrc").read_text(), "a\n")
        self.assertEqual(list(self.home.glob("*.bak.*")), [])

    def test_foreign_symlink_removed_regular_kept(self):
        repo = self.home / ".ziro"
        repo.mkdir()
        (repo / ".zshrc").write_text("# ziro\n")
        (self.home / ".zshrc").symlink_to(repo / ".zshrc")
        (self.home / ".zprofile").write_text("x\n")
        installer._backup_existing(Options())
        self.assertTrue((self.home / ".zshrc").is_symlink())
        self.assertFalse((self.home / ".zprofile").exists())
        self.assertTrue(next(self.home.glob(".zprofile.bak.*")).is_file())


class TestPathHeal(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="ziro-path-"))
        self._orig_home = installer._home
        self._orig_resolve = installer.gitops.resolve_config_dir
        installer._home = lambda: self.home
        installer.gitops.resolve_config_dir = lambda home=None: self.home / ".ziro"
        (self.home / ".ziro").mkdir()

    def tearDown(self):
        installer._home = self._orig_home
        installer.gitops.resolve_config_dir = self._orig_resolve
        shutil.rmtree(self.home)

    def test_creates_zshenv_export(self):
        installer._ensure_local_bin_on_path(False)
        zshenv = (self.home / ".zshenv").read_text()
        self.assertIn('export PATH="$HOME/.local/bin:$PATH"', zshenv)

    def test_idempotent(self):
        installer._ensure_local_bin_on_path(False)
        installer._ensure_local_bin_on_path(False)
        text = (self.home / ".zshenv").read_text()
        self.assertEqual(text.count('export PATH="$HOME/.local/bin:$PATH"'), 1)

    def test_zshrc_local_gets_guarded_line(self):
        local = self.home / ".ziro" / ".zshrc.local"
        local.write_text("ZSH_ENV_TYPE='desktop'\n")
        installer._ensure_local_bin_on_path(False)
        text = local.read_text()
        self.assertIn("ZSH_ENV_TYPE", text)  # existing content preserved
        self.assertIn('[[ ":$PATH:" != *":$HOME/.local/bin:"* ]]', text)

    def test_existing_export_not_duplicated(self):
        zshenv = self.home / ".zshenv"
        zshenv.write_text('export PATH="$HOME/.local/bin:$PATH"\n')
        installer._ensure_local_bin_on_path(False)
        self.assertEqual(zshenv.read_text().count("local/bin"), 1)

    def test_dry_run_writes_nothing(self):
        installer._ensure_local_bin_on_path(True)
        self.assertFalse((self.home / ".zshenv").exists())


class TestThemeInstall(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="ziro-theme-"))
        self.repo = self.home / ".ziro"
        shutil.copytree(Path(__file__).resolve().parents[2] / "themes",
                        self.repo / "themes")
        (self.home / ".config").mkdir()
        self._orig_home = installer._home
        installer._home = lambda: self.home

    def tearDown(self):
        installer._home = self._orig_home
        shutil.rmtree(self.home)

    def test_fresh_install_places_default_theme(self):
        installer._install_starship_config(Options(), self.repo)
        conf = self.home / ".config" / "starship.toml"
        self.assertTrue(conf.is_file())
        self.assertEqual(conf.read_bytes(),
                         (self.repo / "themes" / "lambda" / "Starship.toml").read_bytes())

    def test_user_edits_survive_reinstall(self):
        conf = self.home / ".config" / "starship.toml"
        conf.write_text("# my custom config\n")
        installer._install_starship_config(Options(), self.repo)
        self.assertEqual(conf.read_text(), "# my custom config\n")

    def test_managed_copy_refreshed_on_upgrade(self):
        conf = self.home / ".config" / "starship.toml"
        installer._install_starship_config(Options(), self.repo)
        theme = self.repo / "themes" / "lambda" / "Starship.toml"
        theme.write_bytes(theme.read_bytes() + b"\n# upstream change\n")
        installer._install_starship_config(Options(), self.repo)
        self.assertEqual(conf.read_bytes(), theme.read_bytes())

    def test_switch_theme_with_flag(self):
        names = list(themes.list_themes(self.repo))
        other = next((n for n in names if n != themes.DEFAULT_THEME), None)
        if other is None:
            self.skipTest("only one bundled theme")
        conf = self.home / ".config" / "starship.toml"
        installer._install_starship_config(Options(), self.repo)
        installer._install_starship_config(Options(theme=other), self.repo)
        self.assertEqual(conf.read_bytes(),
                         (self.repo / "themes" / other / "Starship.toml").read_bytes())

    def test_symlinked_config_untouched(self):
        conf = self.home / ".config" / "starship.toml"
        real = self.home / "real.toml"
        real.write_text("keep\n")
        conf.symlink_to(real)
        installer._install_starship_config(Options(), self.repo)
        self.assertTrue(conf.is_symlink())
        self.assertEqual(real.read_text(), "keep\n")

    def test_unknown_theme_rejected(self):
        installer._install_starship_config(Options(theme="nope"), self.repo)
        self.assertFalse((self.home / ".config" / "starship.toml").exists())

    def test_dry_run_writes_nothing(self):
        installer._install_starship_config(Options(dry_run=True), self.repo)
        self.assertFalse((self.home / ".config" / "starship.toml").exists())


if __name__ == "__main__":
    unittest.main()
