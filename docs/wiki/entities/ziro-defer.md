---
title: ziro-defer (fork)
tags: [fork, layer3, zsh-defer, deferral]
sourceRefs: ["/home/ali/.ziro/ziro-defer/ziro-defer.plugin.zsh", "/home/ali/.ziro/.specify/decisions/ADR-004-fork-timing.md", "/home/ali/.ziro/.specify/decisions/ADR-005-ziro-defer-directory-placement.md", "/home/ali/.ziro/integration.zsh"]
lastReviewed: 2026-09-29
---
ziro-defer is a **fork of `romkatv/zsh-defer`** (v0.1.0 MVP). It lives in the
first-class `ziro-defer/` top-level directory — neither `vendor/` (pristine
third-party, gitignored) nor `ghost/` (ziro-original). See [[sources/adr-005-ziro-defer-directory-placement]]
for rationale.

## Directory layout
```
ziro-defer/
├── ziro-defer.plugin.zsh   ← our wrapper (fork entry point)
├── upstream/               ← vendored romkatv/zsh-defer
│   ├── zsh-defer.plugin.zsh
│   └── LICENSE             ← romkatv MIT preserved
├── LICENSE                 ← our MIT
└── README.md               ← lineage + roadmap
```

## API (v0.1.0 MVP)
Wrapper exposes `ziro-defer` as a shell function. Flags:
- `--wait=N` → translated to upstream `-t N`
- `--slot`, `--lazy-by-command`, `--lazy-by-function`, `--atinit`, `--atload`
  accepted but **not implemented** yet (TODO v0.2+)

The wrapper loads the upstream engine via:
```zsh
source "${ZSH_DEFER_UPSTREAM:-${0:h}/upstream/zsh-defer.plugin.zsh}"
```

## Fallback chain in `integration.zsh`
1. `ziro-defer/ziro-defer.plugin.zsh` — canonical fork (preferred)
2. `vendor/ziro-defer/ziro-defer.plugin.zsh` — shim (deprecated)
3. `vendor/ziro-defer/zsh-defer.plugin.zsh` — upstream directly
4. `zsh-defer` on `PATH`
5. Eager stub: `ziro-defer() { "$@"; }`

## Naming
Generator in `core/ziro_load.py` emits `ziro-defer ...` (line 53). At runtime
the function exists because this wrapper defines it. Spec 006 §B.3 calls
`ziro-defer source <(znap source X)>` an anti-pattern and prefers
`zsh-defer znap source X`. The split is logged as [[concepts/defer-naming-split]]
(Bug #2). Not a blocker — shim makes it work.

## Roadmap
- v0.2.0: `--slot` a|b|c
- v0.3.0: `--lazy-by-command/function`
- v0.4.0: `--atinit` / `--atload` + auto re-registration
- v1.0.0: full Spec 005
- v1.1.0: **migration to `Pakrohk-DotFiles/ziro-defer` GitHub repo**.
  Directory becomes a standalone repo installable via `znap source
  Pakrohk-DotFiles/ziro-defer`. API stable, consumers unaffected.

Related: [[entities/znap-runtime]], [[sources/adr-002-znap-permanent]],
[[concepts/defer-naming-split]], [[concepts/plugin-sovereignty]]
