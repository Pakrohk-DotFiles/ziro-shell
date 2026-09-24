"""Tests for core.tags."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".ziro"))

from core.tags import (
    Tag,
    load_builtin_tags,
    load_all_tags,
    load_plugin_tags,
    save_plugin_tags,
)


class TestTag(unittest.TestCase):
    def test_is_builtin(self):
        self.assertTrue(Tag("@eager", "eager").is_builtin())
        self.assertFalse(Tag("my-tag", "eager").is_builtin())


class TestBuiltinLoad(unittest.TestCase):
    def test_loads_seven_tags(self):
        config = Path.home() / ".config" / "ziro"
        tags = load_builtin_tags(config)
        self.assertEqual(len(tags), 7)
        self.assertIn("@eager", tags)
        self.assertIn("@compdef", tags)
        self.assertEqual(tags["@compdef"].priority, 15)
        self.assertEqual(tags["@eager"].priority, 10)


class TestPluginTags(unittest.TestCase):
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp)
            (cfg / "tags" / "plugins").mkdir(parents=True)
            save_plugin_tags(cfg, "myplugin", ["@eager", "@no-compile"])
            loaded = load_plugin_tags(cfg, "myplugin")
            self.assertEqual(set(loaded), {"@eager", "@no-compile"})


class TestAllTags(unittest.TestCase):
    def test_all_contains_builtins(self):
        config = Path.home() / ".config" / "ziro"
        all_tags = load_all_tags(config)
        for name in ("@eager", "@compdef", "@lazy", "@raw"):
            self.assertIn(name, all_tags)


if __name__ == "__main__":
    unittest.main()
