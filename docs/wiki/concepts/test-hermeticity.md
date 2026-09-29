---
title: Test Hermeticity
tags: [tests, ci, hermeticity, gotcha]
sourceRefs: [tests/test_resolver.py, tests/test_tags.py, .github/workflows/test.yml]
lastReviewed: 2026-09-25
---

# Test Hermeticity

Ziro's test suite must not depend on state created by `ziro install`.

## The trap

`$HOME/.config/ziro/tags/builtin.toml` is **created at install time**, is
**gitignored**, and therefore **does not exist on a fresh CI runner**. Two test
files used to read it:

- `tests/test_tags.py` — `TestBuiltinLoad`, `TestPluginTags`, `TestAllTags`
- `tests/test_resolver.py` — all three `TestResolve` cases (via
  `_fixture_config`, which copied the home `builtin.toml` into a temp dir)

Result: green locally (where `~/.config/ziro` exists), red or silently
wrong in CI.

## The fix

Both now seed an **inline minimal `builtin.toml`** into a temp config dir, so
each test is self-contained:

```python
_MIN_BUILTIN_TOML = (
    '[[tags]]\nname = "@eager"\nstrategy = "eager"\npriority = 10\n'
    '[[tags]]\nname = "@lazy"\nstrategy = "defer"\npriority = 5\n'
)

def _fixture_config(tmp: str) -> Path:
    cfg = Path(tmp)
    (cfg / "tags" / "plugins").mkdir(parents=True, exist_ok=True)
    (cfg / "tags" / "builtin.toml").write_text(_MIN_BUILTIN_TOML)
    return cfg
```

## PYTHONPATH in CI

28 test modules begin with:

```python
sys.path.insert(0, str(Path.home() / ".ziro"))
```

`~/.ziro` does not exist on a CI runner. The tests still pass because the
suite is invoked from the repo root, where `core/` and `tests/` are already
importable — but the `sys.path.insert` line is dead weight in CI and can mask
import errors. `.github/workflows/test.yml` sets `PYTHONPATH` to the workspace
explicitly:

```yaml
- name: Run tests
  env:
    PYTHONPATH: ${{ github.workspace }}
  run: python -m unittest discover -s tests -v
```

## Verifying hermeticity locally

Simulate a bare CI checkout — fresh worktree, empty HOME:

```bash
WORK=$(mktemp -d)
git archive HEAD | tar -x -C "$WORK"
HOME_SIM=$(mktemp -d)
cd "$WORK"
python3 -m unittest discover -s tests   # → Ran 129 tests ... OK
```

If this passes, the suite is hermetic. See [[entities/tag-system]] for what
`builtin.toml` actually contains and [[entities/ziro]] for the layout.

## Related

- [[concepts/xdg-path-layout]] — where the config dirs live at runtime
- [[entities/tag-system]] — the tag definitions being loaded
