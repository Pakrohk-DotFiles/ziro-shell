# Ziro Wiki — Log

Append-only timeline. Format: `## [date] op | title`

## 2026-09-24 seed | Initial wiki seeded

Built from `.specify/` spec suite (specs 000–009), `decisions/`
(ADR-002, ADR-003), `roadmap.json`, `memory/constitution.md`, and live source
(`integration.zsh`, `ziro.zsh`, `ghost/ghost.zsh`, `lib/xdg.zsh`,
`lib/log.zsh`, `commands/help.zsh`, `.zshrc`).

Created pages:
- entities: ziro, shell-bootstrap, plugin-analyzer, tag-system, znap-runtime,
  cli, ghost-plugin
- concepts: hot-path-cold-path, plugin-sovereignty, xdg-path-layout,
  znap-plugin-loading
- sources: adr-002-znap-permanent, adr-003-two-layer-architecture

Key synthesized findings:
- ADR-001 is superseded — cite ADR-002 for backend decisions
- Hot path forbids all Python/subprocess/file-parsing/network; 5 ms budget
- Constitution XIV plugin sovereignty is why local plugins are `source`d
  directly rather than passed to `znap source`
- Spec 007 (ghost autosuggest) is deprecated; current spec is 009
- IRIS verification confirmed zero zsh-side polling — all tickers in Go;
  zsh is event-driven via four ZLE hooks

## [2026-09-25] ingest | Test hermeticity (CI red → green)

Discovered `tests/test_tags.py` and `tests/test_resolver.py` were reading tag
definitions from the *installed* `~/.config/ziro/tags/builtin.toml` — an
install-time, gitignored file absent on fresh CI runners. Suite was green
locally, red in CI. Fixed both to seed an inline minimal `builtin.toml` into
a temp dir. Also set `PYTHONPATH` to the workspace in
`.github/workflows/test.yml` (28 test modules do `sys.path.insert(0,
$HOME/.ziro`, which does not exist in CI).

Verified hermetic: fresh `git archive HEAD` checkout + empty HOME → 129 tests
OK. CI now passes on 3.11 and 3.12 (run 36086251950). Commit 1e6c6a4 on
`perf/startup`; PR #20.

## [2026-09-25] ingest | defer-naming-split (concepts)
`core/ziro_load.py:53` emits `ziro-defer` as the deferral command, but the
vendored plugin at `vendor/ziro-defer/zsh-defer.plugin.zsh` only defines
`zsh-defer` (zero matches for `ziro-defer` in that file). Deferred-strategy
plugins produce `plugins.gen.zsh` lines failing with
`command not found: ziro-defer`. Spec 006 §B.3 explicitly labels
`ziro-defer source <(...)` an anti-pattern and mandates
`zsh-defer znap source X`. Fix: change `prefix` in `core/ziro_load.py` plus
the assertion in `tests/test_generator.py:29`; `integration.zsh` and
`doctor_cli.py` already accept either name. New page
[[concepts/defer-naming-split]].

## [2026-09-25] ingest | ziro-defer v0.1.0 progressive fork (concepts/defer-naming-split)
Bug closed without touching the emitter: created
`vendor/ziro-defer/ziro-defer.plugin.zsh` (v0.1.0 MVP). It sources the
vendored upstream `zsh-defer.plugin.zsh` then defines `ziro-defer()` with
`--wait=N` → `-t N` translation; `--slot=*`, `--lazy-by-command=*`,
`--lazy-by-function=*`, `--atinit=*`, `--atload=*` accepted-but-ignored with
TODO markers for v0.2+. `integration.zsh:28-31` already prefers this filename
(no change). `core/ziro_load.py` and `tests/test_generator.py` unchanged —
129 tests OK. Verified end-to-end: emitted line
`ziro-defer --wait="0" --slot=b znap source test-plugin` runs in full
integration context with no `command not found`. Page
[[concepts/defer-naming-split]] updated with RESOLVED status + roadmap table.
Also learned: zsh-defer fires on first precmd, not after N seconds, so
deferred stdout is invisible under `zsh -c` — verify via `type ziro-defer`.

## [2026-09-28] ingest | adr-005-ziro-defer-directory-placement (sources)
Added wiki page for `.specify/decisions/ADR-005-ziro-defer-directory-placement.md`.
Decision: forks of third-party code (ziro-defer = fork of romkatv/zsh-defer)
live in a first-class top-level tracked directory `ziro-defer/`, NOT in
`vendor/` (pristine third-party, gitignored, would need force-add) and NOT in
`ghost/` (ziro-original namespace). Directory bundles own wrapper +
`upstream/` (vendored upstream + preserved MIT LICENSE) + own LICENSE + README
(lineage + roadmap). integration.zsh sources `$ZIRO_HOME/ziro-defer/` first,
vendor/ as deprecated fallback. At v1.1.0 the dir becomes
`Pakrohk-DotFiles/ziro-defer` repo (znap source installable). Cross-refs
[[concepts/defer-naming-split]], [[entities/znap-runtime]],
[[sources/adr-002-znap-permanent]], [[concepts/plugin-sovereignty]].

## [2026-09-29] ingest | adr-004-fork-timing (sources)

Created [[sources/adr-004-fork-timing]] to close a dangling `ADR-004`
reference in the ADR-005 page. Records the fork-timing decision (fork
DEFERRED until Phase 0 complete + Phase 4 stable), the interim thin
wrapper `ziro-defer() { zsh-defer "$@"; }`, and notes the reversal
trigger has since fired — bootstrap verified, so the fork was started
early and v0.1.0 now lives in `ziro-defer/` per
[[sources/adr-005-ziro-defer-directory-placement]]. Also deleted a stray
duplicate untracked file `.specify/decisions/ADR-005-fork-directory-convention.md`
(superseded by the tracked `ADR-005-ziro-defer-directory-placement.md`).

## [2026-09-29] ingest | wiki-moved-to-docs (concepts)

Moved the wiki from `.opencode/wiki/` to `docs/wiki/`. `.opencode/` is
gitignored by architectural decision (local AI-tooling state); the previous
session force-added the wiki past that rule, which violated it. The move keeps
the knowledge tracked while respecting the original intent — no gitignore
exceptions were added.

Renamed `sources/adr-005-fork-directory-convention.md` →
`sources/adr-005-ziro-defer-directory-placement.md` to match the actual ADR
filename (`.specify/decisions/ADR-005-ziro-defer-directory-placement.md`) and
updated all 6 internal `[[...]]` links referencing the old slug.
