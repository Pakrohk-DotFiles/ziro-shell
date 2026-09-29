---
title: ziro-defer vs zsh-defer — the naming split
tags: [defer, zsh-defer, ziro-defer, gotcha, bug, generator, emit]
sourceRefs:
  - "/home/ali/.ziro/core/ziro_load.py"
  - "/home/ali/.ziro/integration.zsh"
  - "/home/ali/.ziro/.specify/specs/006-install-defaults-registry/spec.md"
  - "/home/ali/.ziro/doctor_cli.py"
lastReviewed: 2026-09-25
---

The deferral engine is **`zsh-defer`**, upstream. The generator emits
**`ziro-defer`**, a name that does not exist at runtime. Any deferred plugin
strategy currently produces a line that fails with
`command not found: ziro-defer`.

## The split

| Layer | Name | Where |
|---|---|---|
| Emitted code | `ziro-defer` | `core/ziro_load.py:53` (`prefix = "ziro-defer"`), `tests/test_generator.py:29` |
| Vendored binary | `zsh-defer` | `vendor/ziro-defer/zsh-defer.plugin.zsh` |
| Bootstrap fallback | both | `integration.zsh:28-36` |
| Doctor check | both | `doctor_cli.py:46-52` |

`vendor/ziro-defer/` contains **only** `zsh-defer.plugin.zsh` — the vendored
upstream `romkatv/zsh-defer`. It defines the `zsh-defer` function. A grep for
`ziro-defer` in that file returns **zero** matches. The name `ziro-defer` is
aspirational: ADR-002 calls ziro-defer "our deferral engine," but no fork
exists in the repo.

## Spec 006 calls `ziro-defer` an anti-pattern

`.specify/specs/006-install-defaults-registry/spec.md` (§B.3) is explicit:

> The originally proposed `ziro-defer source <(znap source X)` is an
> anti-pattern (use `znap source X` with `zsh-defer` fallback only): `znap
> source` does not print code to stdout, so the process substitution feeds
> `source` an empty file — defer silently loads nothing.

The spec mandates the form `zsh-defer znap source <owner>/<repo>` and claims
the repo's own `.zshrc` "already uses the correct form." The generator does
not follow this — it emits `ziro-defer ... znap source X`.

## Reproduction

```zsh
ziro plugin add mfaerevaag/wd wd @defer-comp   # adds a deferred plugin
zsh -c 'source ~/.ziro/integration.zsh; \
        source $ZIRO_CONFIG/derived/plugins.gen.zsh'
# → plugins.gen.zsh:5: command not found: ziro-defer
```

Generated line:
```
ziro-defer --wait="0" --slot=0 znap source wd
```

## Bootstrap does the right thing — generator does not

`integration.zsh` tries `ziro-defer.plugin.zsh`, falls back to
`zsh-defer.plugin.zsh`, then to a `zsh-defer` on PATH, and finally defines an
eager no-op stub `ziro-defer() { "$@"; }`. Only the **last** branch defines
the `ziro-defer` name, and it is reached only when the vendored plugin file
is entirely absent. In the normal case the `zsh-defer` branch is taken and
`ziro-defer` is never defined — so the emitted line is dead on arrival.

## Status: RESOLVED (v0.1.0 MVP, 2026-09-25)

The gap is closed by a **progressive fork**, not by editing the emitter.
`vendor/ziro-defer/ziro-defer.plugin.zsh` now exists, sources the vendored
upstream `zsh-defer.plugin.zsh`, and defines the `ziro-defer` function that
`core/ziro_load.py` emits. Deferred-strategy plugins load correctly;
`core/ziro_load.py` and `tests/test_generator.py` are unchanged.

## Progressive Fork Strategy (v0.8.11)

The project uses a **progressive fork** approach for ziro-defer:

| Version | Scope | Status |
|---------|-------|--------|
| v0.1.0 | MVP wrapper over upstream zsh-defer | **implemented** |
| v0.2.0 | --slot=a\|b\|c sub-slot priority | TODO |
| v0.3.0 | --lazy-by-command, --lazy-by-function | TODO |
| v0.4.0 | --atinit, --atload, auto re-register | TODO |
| v1.0.0 | Full spec 005 feature set | TODO |

**Key design:**
- `vendor/ziro-defer/ziro-defer.plugin.zsh` — our file (grows)
- `vendor/ziro-defer/zsh-defer.plugin.zsh` — upstream engine (unchanged)
- ziro-defer sources upstream, then wraps with fork-friendly API
- `core/ziro_load.py` emits `ziro-defer ...` (stable contract)

**v0.1.0 arg translation:**
- `--wait=N` → upstream `-t N`
- `--slot=*`, `--lazy-by-command=*`, `--lazy-by-function=*`, `--atinit=*`,
  `--atload=*` → accepted, silently ignored (TODO markers for v0.2+)
- all other args → pass-through to `zsh-defer`

**Why not a shim in integration.zsh?**
- Shim is temporary; must be deleted when fork arrives
- Progressive fork is permanent; API is the same file
- File version tracking shows evolution

**Sourcing order** (`integration.zsh:28-31`) prefers this file first, falling
back to upstream-only when it is absent — so the wrapper is picked up with
no change to `integration.zsh`.

**Note on `--wait` semantics:** upstream `zsh-defer` schedules work on the
*first prompt* after load (`precmd`), not after N seconds — the `-t` value
just delays within that scheduling window. Deferred output only appears at
the first interactive prompt, so a non-interactive `zsh -c` harness shows no
deferred output even when the deferral is correctly registered. Verify
registration with `type ziro-defer` / absence of `command not found`, not by
capturing deferred stdout.

**Verified arg translation (via shim, session 2026-09-25):** shimming
`zsh-defer` after sourcing our wrapper, `ziro-defer --wait="5" --slot=b znap
source test-plugin` produced `SHIM-GOT: -t 5 znap source test-plugin` —
`--wait=N` → `-t N` correct, `--slot` dropped as expected in v0.1.0. Calling
`_zsh-defer-apply "0 echo X"` directly (bypassing ZLE) printed `X`, proving
the deferred executor runs the translated task. Full interactive execution
requires a live ZLE widget, which a `zsh -c` harness cannot provide.

Related: [[entities/znap-runtime]], [[concepts/hot-path-cold-path]],
[[entities/plugin-analyzer]].
