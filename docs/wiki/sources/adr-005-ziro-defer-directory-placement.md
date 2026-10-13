---
title: ADR-005 — Fork Directory Convention
tags: [adr, architecture, fork, ziro-defer]
sourceRefs: ["/home/ali/.ziro/.specify/decisions/ADR-005-ziro-defer-directory-placement.md"]
lastReviewed: 2026-09-28
---
Where do forks of third-party code live? `vendor/` is for pristine
third-party (gitignored); `ghost/` is for ziro-original plugins. A fork is
neither. ADR-005 grants each fork a first-class top-level directory.

## Directory taxonomy
```
~/.ziro/
├── vendor/        ← pristine third-party clones (znap, gitignored)
├── ziro-defer/    ← fork of romkatv/zsh-defer (tracked)
│   ├── ziro-defer.plugin.zsh   ← our wrapper (fork entry point)
│   ├── upstream/               ← vendored upstream (MIT, attributed)
│   │   ├── zsh-defer.plugin.zsh
│   │   └── LICENSE             ← romkatv MIT, preserved
│   ├── LICENSE                 ← our MIT
│   └── README.md               ← lineage + roadmap
├── ghost/         ← ziro-original plugins (tracked)
└── ziro/          ← (legacy Python core namespace)
```

## Why a fork is not vendor nor ghost
- **Not `vendor/`**: that directory is for clones of third-party repos and is
  gitignored — committing a fork there forces `git add -f`, violating the
  gitignore architecture.
- **Not `ghost/`**: that is the namespace for ziro-original code. A fork
  derives from someone else's work.
- **Own directory**: gives the fork its own LICENSE, README, and provenance,
  and a clean path to extraction into its own repo later.

## Consequences
- `integration.zsh` sources `$ZIRO_HOME/ziro-defer/ziro-defer.plugin.zsh`
  **first**, before `vendor/` (fork preferred, vendor as deprecated fallback).
- Provenance is unambiguous: `upstream/` subdir documents derivation and
  preserves the author's MIT license.
- Future forks (e.g. `ziro-omp`) follow the same pattern.

## Relation to defer-naming-split
This ADR is the *placement* answer to the [[concepts/defer-naming-split]]
problem (generator emits `ziro-defer`, which used to be undefined). The fork
now defines that name with a stable wrapper; `core/ziro_load.py` is unchanged
and still emits `ziro-defer`. Related: [[entities/znap-runtime]],
[[sources/adr-002-znap-permanent]], [[concepts/plugin-sovereignty]].

## Migration plan
At v1.1.0 the `ziro-defer/` directory becomes the
`Pakrohk-DotFiles/ziro-defer` GitHub repo, installable via
`znap source Pakrohk-DotFiles/ziro-defer`. Consumers unaffected (API stable).
