# ADR-005: ziro-defer Directory Placement

**Status**: Adopted
**Date**: 2026-09-28

## Context

Once the decision was made to start the ziro-defer fork earlier than
ADR-004 anticipated (bootstrap working, eager fallback verified), the
question became *where* to put the fork in the repository tree.

Three candidate locations existed:

1. `vendor/ziro-defer/` — where the upstream copy currently lives
2. `ghost/` — where ziro-original code lives
3. A new top-level `ziro-defer/` directory

Placing it wrongly would create a category error: either contaminating
the pristine third-party vendoring area, or burying a fork inside a
directory whose purpose is original ziro code.

## Decision

Create a **first-class top-level `ziro-defer/` directory**.

```
ziro-defer/
├── ziro-defer.plugin.zsh       # our wrapper (fork entry point)
├── upstream/
│   ├── zsh-defer.plugin.zsh    # vendored upstream (MIT, attributed)
│   └── LICENSE                 # romkatv's MIT license
├── LICENSE                     # our MIT license
└── README.md
```

### Rationale

- **`vendor/` is for pristine third-party.** Its `.gitignore` and
  documentation describe it as a cache of unmodified upstream sources.
  A fork — by definition modified — would violate that contract.
  Also, `vendor/` entries are gitignored in part; a fork must be
  tracked.
- **`ghost/` is for ziro-original code.** ziro-defer is derived from
  romkatv/zsh-defer. Putting it in `ghost/` would misrepresent
  provenance and complicate MIT attribution.
- **A fork deserves its own namespace.** The fork has its own release
  cadence, its own README, its own LICENSE, and eventually its own
  GitHub repository. A top-level directory makes all of that visible
  at a glance and keeps the exit door open (see ADR-004 migration).

### `integration.zsh` fallback chain

The bootstrap prefers the fork, then falls back to vendored upstream,
then to an eager stub — matching Spec 004 R2 and ADR-002:

```zsh
if [[ -r "$ZIRO_HOME/ziro-defer/ziro-defer.plugin.zsh" ]]; then
  source "$ZIRO_HOME/ziro-defer/ziro-defer.plugin.zsh"
elif [[ -r "$ZIRO_HOME/vendor/ziro-defer/ziro-defer.plugin.zsh" ]]; then
  ...
```

## Consequences

**Positive:**
- Provenance is unambiguous: `vendor/` = untouched, `ziro-defer/` = fork,
  `ghost/` = original.
- Clean extraction to `Pakrohk-DotFiles/ziro-defer` when the fork
  matures (ADR-004 migration target).
- Attribution preserved: upstream MIT license kept at
  `ziro-defer/upstream/LICENSE`.
- No conflict with the gitignored vendor tree.

**Negative:**
- One more top-level directory to document.
- Must be remembered when grepping for "where is the defer engine" —
  the answer is now two places (fork wrapper + vendored upstream inside
  it).

## Alternatives considered

- **Fork in `vendor/ziro-defer/`** — rejected: violates vendor's
  pristine-third-party contract; partially gitignored.
- **Fork in `ghost/`** — rejected: misrepresents provenance; ghost/ is
  for ziro-original code.
- **Keep fork outside the repo entirely until v1.1** — rejected: no way
  to develop/test the wrapper against the live bootstrap.

## Related

- [[wiki/ADR-004 — ziro-defer Fork Timing]]
- Spec 004 (R2 fallback chain), Spec 005, Spec 009 (directory topology)
- `ziro-defer/README.md`
