"""Tests for core.generator."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".ziro"))

from core.generator import generate, HEADER_LINE, default_output_path, EmitOptions
from core.models import Strategy
from core.resolver import ResolvedConfig


class TestGenerate(unittest.TestCase):
    def test_header_and_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "plugins.gen.zsh"
            configs = [
                ResolvedConfig("p1", Strategy.EAGER),
                ResolvedConfig("p2", Strategy.AFTER_PROMPT, defer_slot="b"),
                ResolvedConfig("p3", Strategy.LAZY, defer_slot="2"),
            ]
            opts = EmitOptions(generated_at="2026-01-01T00:00:00Z")
            generate(configs, out, options=opts)
            content = out.read_text()
            self.assertTrue(content.startswith(HEADER_LINE))
            self.assertIn("znap source p1", content)
            self.assertIn("ziro-defer --slot=b znap source p2", content)
            self.assertIn("ziro-defer --slot=2 znap source p3", content)

    def test_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            out1 = Path(tmp) / "a.zsh"
            out2 = Path(tmp) / "b.zsh"
            configs = [ResolvedConfig("p1", Strategy.EAGER)]
            ts = "2026-01-01T00:00:00Z"
            opts = EmitOptions(generated_at=ts)
            generate(configs, out1, options=opts)
            generate(configs, out2, options=opts)
            self.assertEqual(out1.read_text(), out2.read_text())

    def test_default_output_path(self):
        p = default_output_path(Path("/home/x/.config/ziro"))
        self.assertEqual(str(p), "/home/x/.config/ziro/derived/plugins.gen.zsh")


if __name__ == "__main__":
    unittest.main()
