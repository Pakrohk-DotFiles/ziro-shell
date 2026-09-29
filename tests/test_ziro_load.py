"""Tests for core.ziro_load."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".ziro"))

from core.ziro_load import (
    LoadSpec,
    emit,
    emit_deferred,
    emit_eager,
    emit_raw,
    from_resolved,
)


class TestEmitEager(unittest.TestCase):
    def test_plain_eager(self):
        spec = LoadSpec("my-plugin", "eager")
        self.assertEqual(emit(spec), "znap source my-plugin")

    def test_eager_with_eval_cache(self):
        spec = LoadSpec("zoxide", "eager", eval_cache="zoxide init zsh")
        self.assertEqual(emit(spec), "znap eval zoxide 'zoxide init zsh'")

    def test_eager_with_pick(self):
        spec = LoadSpec("multi", "eager", pick="main.plugin.zsh")
        self.assertIn("--pick=main.plugin.zsh", emit(spec))


class TestEmitDeferred(unittest.TestCase):
    def test_plain_deferred(self):
        spec = LoadSpec("heavy", "after-prompt")
        self.assertEqual(emit(spec), "ziro-defer znap source heavy")

    def test_deferred_with_slot(self):
        spec = LoadSpec("heavy", "after-prompt", sub_slot="b")
        self.assertEqual(emit(spec), "ziro-defer --slot=b znap source heavy")

    def test_deferred_with_wait(self):
        spec = LoadSpec("delayed", "lazy", wait="2")
        self.assertIn('--wait="2"', emit(spec))


class TestEmitRaw(unittest.TestCase):
    def test_raw_verbatim(self):
        spec = LoadSpec("custom", "raw", raw='znap source custom --deep')
        self.assertEqual(emit(spec), "znap source custom --deep")


class TestFromResolved(unittest.TestCase):
    def test_maps_eager(self):
        spec = from_resolved("p1", "EAGER")
        self.assertEqual(spec.strategy, "eager")

    def test_maps_after_prompt(self):
        spec = from_resolved("p2", "AFTER_PROMPT", defer_slot="b")
        self.assertEqual(spec.strategy, "after-prompt")
        self.assertEqual(spec.sub_slot, "b")

    def test_maps_lazy(self):
        spec = from_resolved("p3", "LAZY", wait="2")
        self.assertEqual(spec.strategy, "lazy")
        self.assertEqual(spec.wait, "2")

    def test_unknown_strategy_fallback(self):
        spec = from_resolved("p4", "weird-strategy")
        self.assertEqual(spec.strategy, "eager")


if __name__ == "__main__":
    unittest.main()
