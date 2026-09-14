"""Focused unit tests for new IOP contracts: update models, ports, adapters."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ziro.domain.update import UpdateResult, UpdateStatus
from ziro.ports import (
    ConsoleUI, FileSystem, GitPort, PackageManager, ProcessRunner, RunError,
    ShellPort,
)
from ziro.adapters import GitOpsAdapter, ShellAdapter, SubprocessRunner


class TestUpdateResult(unittest.TestCase):
    def test_updated_ok(self):
        r = UpdateResult(UpdateStatus.UPDATED, Path("/home/u/.ziro"))
        self.assertTrue(r.ok)
        self.assertEqual(r.exit_code, 0)

    def test_up_to_date_ok(self):
        r = UpdateResult(UpdateStatus.UP_TO_DATE)
        self.assertTrue(r.ok)
        self.assertEqual(r.exit_code, 0)

    def test_failure_codes(self):
        for status in (UpdateStatus.NO_REPO, UpdateStatus.FOREIGN_ORIGIN,
                       UpdateStatus.PULL_FAILED, UpdateStatus.CONFLICT):
            r = UpdateResult(status)
            self.assertFalse(r.ok, status)
            self.assertEqual(r.exit_code, 1, status)

    def test_immutable(self):
        r = UpdateResult(UpdateStatus.UPDATED)
        with self.assertRaises(Exception):
            r.status = UpdateStatus.NO_REPO


class TestPortProtocols(unittest.TestCase):
    def test_runtime_checkable_negative(self):
        # Protocols are not @runtime_checkable by design here: existence is
        # structural, verified by instantiating the adapters instead.
        self.assertTrue(callable(SubprocessRunner.run))
        self.assertTrue(callable(GitOpsAdapter.pull_ff_only))
        self.assertTrue(callable(ShellAdapter.zsh_path))

    def test_protocols_are_protocols(self):
        import typing
        for proto in (ConsoleUI, FileSystem, GitPort, PackageManager,
                      ProcessRunner, ShellPort):
            self.assertTrue(
                getattr(proto, "_is_protocol", False),
                f"{proto.__name__} must stay a Protocol (no implementations in ports/)",
            )


class TestProcessAdapter(unittest.TestCase):
    def setUp(self):
        self.runner = SubprocessRunner()

    def test_run_success(self):
        proc = self.runner.run(["true"], check=False)
        self.assertEqual(proc.returncode, 0)

    def test_run_check_raises_runerror(self):
        with self.assertRaises(RunError) as ctx:
            self.runner.run(["false"])
        self.assertEqual(ctx.exception.returncode, 1)
        self.assertEqual(ctx.exception.cmd, ["false"])

    def test_missing_executable_127(self):
        with self.assertRaises(RunError) as ctx:
            self.runner.run(["definitely-not-a-real-binary-xyz"])
        self.assertEqual(ctx.exception.returncode, 127)

    def test_capture_strips(self):
        out = self.runner.capture(["printf", "hi\n"])
        self.assertEqual(out, "hi")

    def test_quiet_returns_bool(self):
        self.assertTrue(self.runner.quiet(["true"]))
        self.assertFalse(self.runner.quiet(["false"]))

    def test_sudo_prefix(self):
        self.assertEqual(self.runner.sudo_prefix("sudo"), ["sudo"])
        self.assertEqual(self.runner.sudo_prefix(None), [])


class TestRunErrorModel(unittest.TestCase):
    def test_message_contains_cmd_and_code(self):
        err = RunError(["git", "pull"], 1, "boom")
        self.assertIn("git pull", str(err))
        self.assertIn("1", str(err))
        self.assertEqual(err.stderr, "boom")


if __name__ == "__main__":
    unittest.main()
