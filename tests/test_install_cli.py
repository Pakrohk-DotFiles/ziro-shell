"""Tests for core.install_cli."""
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".ziro"))
from core import install_cli


class TestInstallCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._old = os.environ.get("ZIRO_CONFIG")
        os.environ["ZIRO_CONFIG"] = self.tmp.name

    def tearDown(self):
        if self._old is not None:
            os.environ["ZIRO_CONFIG"] = self._old
        else:
            os.environ.pop("ZIRO_CONFIG", None)
        self.tmp.cleanup()

    def test_dry_run(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = install_cli.main(["--default", "--dry-run"])
        self.assertEqual(rc, 0)
        self.assertIn("dry-run", buf.getvalue())

    def test_default_writes_files(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = install_cli.main(["--default"])
        self.assertEqual(rc, 0)
        self.assertTrue((Path(self.tmp.name) / "defaults.toml").is_file())
        self.assertTrue((Path(self.tmp.name) / "tools.toml").is_file())

    def test_no_overwrite(self):
        cfg = Path(self.tmp.name)
        cfg.mkdir(parents=True, exist_ok=True)
        (cfg / "defaults.toml").write_text("# custom\n")
        install_cli.main(["--default"])
        self.assertEqual((cfg / "defaults.toml").read_text(), "# custom\n")


if __name__ == "__main__":
    unittest.main()
