"""Tests for core.plugin_cli."""
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".ziro"))
from core import plugin_cli


class TestPluginCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._old = os.environ.get("ZIRO_HOME")
        os.environ["ZIRO_HOME"] = self.tmp.name

    def tearDown(self):
        if self._old is not None:
            os.environ["ZIRO_HOME"] = self._old
        else:
            os.environ.pop("ZIRO_HOME", None)
        self.tmp.cleanup()

    def test_list_empty(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = plugin_cli.main(["list"])
        self.assertEqual(rc, 0)

    def test_add_skeleton(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = plugin_cli.main(["add", "test-plugin"])
        self.assertEqual(rc, 0)
        self.assertIn("test-plugin", buf.getvalue())

    def test_show_missing(self):
        rc = plugin_cli.main(["show", "nope"])
        self.assertEqual(rc, 1)

    def test_unknown_sub(self):
        rc = plugin_cli.main(["bogus"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
