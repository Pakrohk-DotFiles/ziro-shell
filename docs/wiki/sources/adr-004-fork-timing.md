---
title: ADR-004 — ziro-defer Fork Timing
tags: [adr, ziro-defer, fork-timing, phase-0, sequencing]
sourceRefs:
  - .specify/decisions/ADR-004-ziro-defer-fork-timing.md
lastReviewed: 2026-09-29
---

# ADR-004: ziro-defer Fork Timing

**Status**: Adopted (2026-09-23) — **superseded in part by [[sources/adr-005-ziro-defer-directory-placement]]**

## Decision

Spec 005 calls for forking upstream `zsh-defer` into `ziro-defer` with 9 new
features. Per ADR-004, the fork itself was **deferred** until Phase 0
(bootstrap) was complete and verified.

Interim approach — the `ziro-defer` command is provided by a thin wrapper:

```zsh
ziro-defer() { zsh-defer "$@"; }
```

supplied by `integration.zsh` when the fork was not yet present.

## Rationale

1. Fork complexity can wait — bootstrap is the critical path.
2. Upstream zsh-defer is stable and tested.
3. The interface (`ziro-defer`) is what matters, not internals.
4. Fork work belongs to Phase 5 (znap optimization + ziro-defer).

## Consequences

- `integration.zsh` checks for `ziro-defer.plugin.zsh` first, then falls back
  to `zsh-defer.plugin.zsh`, then to an eager stub.
- If the ziro-defer fork exists, it takes priority.
- Spec 005 remains valid; the fork was still planned.

## Reversal trigger

"Phase 0 complete AND Phase 4 (runtime adapter) stable."

**This trigger fired** — bootstrap working, eager fallback verified, so the
fork was started early. v0.1.0 of the fork now lives in the
`ziro-defer/` directory (see [[sources/adr-005-ziro-defer-directory-placement]]).

## Relationship to other ADRs

- **ADR-002** ([[sources/adr-002-znap-permanent]]) — znap is the permanent
  plugin backend; ziro-defer is its deferred-load companion.
- **ADR-003** ([[sources/adr-003-two-layer-architecture]]) — Python core +
  zsh CLI split; ziro-defer is pure zsh, on the shell side.
- **ADR-005** ([[sources/adr-005-ziro-defer-directory-placement]]) — where the
  fork went once the timing decision was overtaken.

## Where the fork stands

v0.1.0 implements only `--wait=N` → `-t N` translation. The remaining spec 005
features (`--slot=`, `--lazy-by-command=`, `--lazy-by-function=`, `--atinit=`,
`--atload=`) are accepted but ignored, slated for v0.2.0–v0.4.0. See
[[concepts/defer-naming-split]] and [[entities/znap-runtime]].
