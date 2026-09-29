"""Tests for core.plugin_pipeline."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".ziro"))

from core.plugin_pipeline import add_plugin, remove_plugin


class TestAddPlugin(unittest.TestCase):
    def test_dry_run_no_clone(self):
        with tempfile.TemporaryDirectory() as tmp:
            zhome = Path(tmp) / "z"
            zcfg = Path(tmp) / "c"
            zhome.mkdir()
            zcfg.mkdir()
            r = add_plugin(
                "fake/repo",
                name="fake",
                ziro_home=zhome,
                config_dir=zcfg,
                dry_run=True,
            )
            self.assertEqual(r.plugin, "fake")
            self.assertTrue(r.dry_run)
            self.assertFalse((zhome / "plugins" / "fake").is_dir())

    def test_add_with_tags(self):
        with tempfile.TemporaryDirectory() as tmp:
            zhome = Path(tmp) / "z"
            zcfg = Path(tmp) / "c"
            zhome.mkdir()
            zcfg.mkdir()
            r = add_plugin(
                "fake/repo",
                name="t",
                tags=["@eager"],
                ziro_home=zhome,
                config_dir=zcfg,
                dry_run=True,
            )
            self.assertEqual(r.plugin, "t")


class TestRemovePlugin(unittest.TestCase):
    def test_remove_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            zhome = Path(tmp) / "z"
            zcfg = Path(tmp) / "c"
            zhome.mkdir()
            zcfg.mkdir()
            ok = remove_plugin("nope", ziro_home=zhome, config_dir=zcfg)
            self.assertFalse(ok)

    def test_remove_existing_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            zhome = Path(tmp) / "z"
            zcfg = Path(tmp) / "c"
            (zhome / "plugins" / "p1").mkdir(parents=True)
            zcfg.mkdir()
            ok = remove_plugin("p1", ziro_home=zhome, config_dir=zcfg, dry_run=True)
            self.assertTrue(ok)
            self.assertTrue((zhome / "plugins" / "p1").is_dir())  # not removed


if __name__ == "__main__":
    unittest.main()
