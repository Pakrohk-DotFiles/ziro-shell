"""Tests for core.resolver."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".ziro"))

from core.models import (
    AnalysisResult, DetectedSignals, Recommendation, Strategy,
)
from core.resolver import resolve, ConflictError


def _analysis(plugin: str, strategy: Strategy = Strategy.LAZY) -> AnalysisResult:
    return AnalysisResult(
        plugin=plugin,
        source="test",
        detected=DetectedSignals(),
        recommended=Recommendation(strategy=strategy),
    )


def _fixture_config(tmp: str) -> Path:
    """Create temp config dir with builtin.toml copied in."""
    cfg = Path(tmp)
    (cfg / "tags" / "plugins").mkdir(parents=True)
    shutil.copy(
        Path.home() / ".config" / "ziro" / "tags" / "builtin.toml",
        cfg / "tags" / "builtin.toml",
    )
    return cfg


class TestResolve(unittest.TestCase):
    def test_no_tags_keeps_analysis(self):
        config = Path.home() / ".config" / "ziro"
        r = resolve(_analysis("no-tags-plugin"), config)
        self.assertEqual(r.strategy, Strategy.LAZY)
        self.assertEqual(r.applied_tags, ())

    def test_eager_tag_overrides(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _fixture_config(tmp)
            from core.tags import save_plugin_tags
            save_plugin_tags(cfg, "eager-plugin", ["@eager"])
            r = resolve(_analysis("eager-plugin"), cfg)
            self.assertEqual(r.strategy, Strategy.EAGER)
            self.assertIn("@eager", r.applied_tags)

    def test_conflict_raises_when_requested(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = _fixture_config(tmp)
            from core.tags import save_plugin_tags
            save_plugin_tags(cfg, "conflict-plugin", ["@eager", "@lazy"])
            with self.assertRaises(ConflictError):
                resolve(_analysis("conflict-plugin"), cfg, raise_on_conflict=True)


if __name__ == "__main__":
    unittest.main()
