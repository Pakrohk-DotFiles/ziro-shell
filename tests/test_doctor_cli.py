"""Tests for core.doctor_cli."""
import io, os, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".ziro"))
from core import doctor_cli


class TestDoctorCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._cfg = os.environ.get("ZIRO_CONFIG")
        self._home = os.environ.get("ZIRO_HOME")
        os.environ["ZIRO_CONFIG"] = self.tmp.name
        os.environ["ZIRO_HOME"] = self.tmp.name

    def tearDown(self):
        for k, v in (("ZIRO_CONFIG", self._cfg), ("ZIRO_HOME", self._home)):
            if v is not None:
                os.environ[k] = v
            else:
                os.environ.pop(k, None)
        self.tmp.cleanup()

    def test_runs(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = doctor_cli.main([])
        self.assertIn(rc, (0, 1))
        self.assertIn("ziro doctor", buf.getvalue())

    def test_verbose(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            doctor_cli.main(["--verbose"])
        self.assertIn("Python", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
