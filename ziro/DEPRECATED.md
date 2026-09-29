# DEPRECATED — legacy DDD package

**Status**: DEPRECATED as of v1.0.0 (2026-09-24)

This directory contains early DDD hexagonal architecture
(domain/, ports/, adapters/, application/) that is **no longer used**.

## Why it's here

initial design (pre-ADR-003) used full hexagonal architecture.
ADR-003 (Two-Layer Architecture) simplified this to:
- **Python core** → `~/.ziro/core/` (flat modules)
- **Zsh CLI** → `~/.ziro/commands/`, `~/.ziro/lib/`, `~/.ziro/ziro.zsh`

The `core/` package replaces all functionality here.

## Proof of non-use

```bash
# No imports of ziro/ exist anywhere:
grep -rn 'from ziro' ~/.ziro/core/ ~/.ziro/commands/ ~/.ziro/tests/
# (empty)

# All CLI entry points use core/:
grep -rn 'python3 -m core' ~/.ziro/commands/
# all wrappers use `-m core`
```

## Disposition plan

| Version | Action |
|---------|--------|
| v1.0.0 (current) | Documented as deprecated (this file) |
| v1.1.0 | Untrack with `git rm -r --cached ziro/` (git history preserved) |
| v1.2.0 | Physical deletion if no users report dependency |

**Do NOT delete now** — git history must be preserved until v1.1.0.

## Migration

If you were importing from `ziro/`:
```python
# OLD (deprecated)
from ziro.domain.plugin import Plugin

# NEW (use core/)
from core.models import AnalysisResult
from core.analyzer import analyze_plugin
```

See `ARCHITECTURE.md` for current layer model.

## Questions

Open issue at https://github.com/Pakrohk-DotFiles/ziro-shell/issues
