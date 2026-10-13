# ADR-001: Backend Adapter Strategy — Resolve the 000-architecture Reality Flag

**Status**: Superseded by ADR-002
**Date**: 2026-09-16
**Decides**: Reality Flag in `000-architecture` (R1 vs R2 vs new R3)
**Affects**: Constitution v0.1.2 Principle IV; specs 000, 001; future 002/003a/003b/004/005

> **LEGACY REFERENCE**: This section documents Zinit options for historical
> context. ADR-002 permanently removed Zinit. The capability matrix and
> fallback syntax below are retained as the record of *why* znap won; they
> are not to be implemented.

## Context

The umbrella architecture named Layer 3 "Zinit Adapter" while the repo, the
constitution, and PR #19 all run on znap (`zsh-snap`). Layer 2's generated
`plugins.gen.zsh` must target *some* backend at shell startup, and future
specs are blocked on that choice. This ADR resolves it without breaking
working znap flows or losing any backend's capabilities.

## Evidence (gathered 2026-09-16, cited)

1. **Backend reality**: `.zshrc:34-35` clones/sources `marlonrichert/zsh-snap`;
   all loads today are `znap source|eval|prompt` (e.g. `.zshrc:108,131-138`,
   `.zsh_aliases`). `git grep -in zinit` finds exactly one comment
   (`ziro/updater.py:164`). znap's command set (from
   `znap/functions/.znap.*`): `clean clone compile eval fpath function
   multi prompt pull restart source status` — **no load, no ice, no wait,
   no annex, no trigger-load, no async/defer in core** (verified: `grep
   defer znap/znap.zsh` empty; zsh-defer not installed anywhere in the tree).
2. **PR #19 dependency check**: `git diff origin/main...HEAD -- .zshrc |
   grep -E "^\+.*znap"` → **empty**. #19 (compinit dedup, `.zshrc.local`
   idempotency, lazy ssh-agent preexec hook) touches zero plugin-backend
   surface. Neither R2 nor R3 forces any rewrite of #19. **(OUT-1 met)**
3. **Constitution quote (v0.1.2, Principle IV)**: "For unknown plugins the
   fallback is eager loading (inspired by zinit's `wait\"2\" lucid` styles,
   adapted to the actual backend: loaded via `znap source` without any
   deferred wrapper...)". znap is codified as *the* current backend, with
   zinit intent acknowledged.
4. **Performance baseline**: warm pty-to-prompt ≈ 19.6ms measured on
   `perf/startup` (documented in constitution Non-Functional section); all
   of it with znap eager loads — the budget #19 bought is on the znap path.
5. **Layering reality**: znap *is* plain Zsh — `znap source` ultimately runs
   `. "$file"` inside a named function (`.znap.source`). Therefore a
   backend-agnostic call layer (`ziro_load`) can emit either znap commands or
   raw Zsh + a small defer shim without any znap knowledge in Layers 1/2.

## CAPABILITY MATRIX (Zinit feature → znap mapping, evidence-graded)

Grading: **(a)** = found equivalent in znap source; **(b)** = designed
fallback via zsh-defer/Zsh shim/post-load hook; **(c)** = known limitation.

| # | Zinit capability | Zinit syntax | znap native | Adapter fallback | Grade |
|---|---|---|---|---|---|
| 1 | Load plugin | `zinit light` | `znap source` | direct | (a) |
| 2 | Pick main file | `pick"…"` | `znap source repo <file…>` | map `--pick` → positional src | (a) |
| 3 | Explicit source file | `-src` | `znap source repo path/to/file` | direct | (a) |
| 4 | Pre-load hook | `atinit"…"` | — | run code immediately before `znap source` inside same `ziro_load` call (source-time == atinit-time for `light`, which does not parse .zinitrc) | (a) shim-in-adapter |
| 5 | Post-load hook | `atload"…"` | — | run code immediately after `znap source` returns (eager path); for deferred path via defer task tail | (a) shim |
| 6 | Compile on/off | `nocompile` | global `znap compile`/auto-compile zstyle | per-plugin: set `ZPFX`-independent skip by touching znap's ignore mechanism (`znap ignore`) — verified `.znap.ignore` exists | (a) |
| 7 | eval + cache | `from gh-release`/`as-command` | `znap eval <slug> <cmd>` (evals + caches result as function) | `--eval-cache` direct; `--from-gh-release`: adapter curls the release asset itself then `znap source` of local path | (b) |
| 8 | Eager load | (default) / `wait""` | default | `--lazy=false` direct | (a) |
| 9 | Deferred after prompt | `wait"2"` | none | **zsh-defer** (`romkatv/zsh-defer`) tasks: `zdefer { znap source … }` — zsh-defer is a separate 1-file plugin, adapter clones it in Layer 0; not currently installed | (b) |
| 10 | Load at prompt | `at-prompt` (`wait"0"`) | none | zsh-defer first-task (runs immediately after prompt is drawn) | (b) |
| 11 | Sub-slot ordering | `wait"0a/0b/0c"` | none | ordered zsh-defer queue — zsh-defer executes tasks FIFO, so `--sub-slot=a|b|c` = positional index in queue | (b) |
| 12 | Lazy by command | `wait"-0" as"command"` | none | adapter wraps: define a shell function named `<cmd>` that on first call runs `zdefernow { znap source … }` then execs the real command | (b) |
| 13 | Lazy by function | `trigger-load` | none | same shim keyed on function name (`functions -M` / preexec matcher) | (b) |
| 14 | lucid (silence) | `lucid"…"` | znap has no auto-run noise for `source` | map to no-op on znap (nothing to silence) | (a) |
| 15 | reset-prompt | `atload"…zle .reset-prompt…"` | none | adapter appends `zle -R` / `zle .reset-prompt` in atload slot | (b) |
| 16 | notify | `notify"…"` | none | adapter prints via `print -u2` on load failure inside `ziro_load` (TRY/always block, mirroring `.znap.source`) | (b) |
| 17 | Turbo mode (block-grouped parallel loads) | `Turbo` + subslots | none | zsh-defer batching approximates it; NOT equal (no per-block `wait` slices mid-prompt) — acceptable because every fixture plugin needs only rows 9-13 semantics, and those the shim provides | (b) with note |
| 18 | Annexes | `zinit load for`/etc | none | Annexes are Zinit-only *plugins themselves*; adapter cannot synthesize them on znap | **(c)** |
| 19 | compinit integration | `atinit"zicompinit"` | `.znap.compinit-hook` exists (registered by znap init) | map to znap's own compinit hook + explicit `compinit` call in atinit slot | (a) |
| 20 | `--wait-condition=<expr>` | `wait"[[ … ]]"` | none | zsh-defer `zwait` primitive (busy-wait with yield) | (b) |

**No blank cells. One row graded (c): Annexes (#18).**

**Relevance check against the 8 fixture plugins** (ohmyzsh[git,
colored-man-pages], zsh-autosuggestions, zsh-completions,
fast-syntax-highlighting, alias-tips, wd, z, zcolors): none is an Annex or
uses Annex-like behavior (verified — all are sourced today via
`znap source/eval` in `.zshrc`/`.zsh_aliases`). Per the decision framework,
the (c) row is **irrelevant to the fixtures** → R2 not forced to R1 by it.
Every other row is (a) or (b).

## Adapter Contract (frozen)

Between Layer 2 (only emitter) and Layer 3 (only implementer). Layer 2
appends `ziro_load` call blocks to `plugins.gen.zsh`; each backend ships one
`ziro_load` implementation. Parameters exactly as proposed in the brief, with
three refinements (marked ✱):

```
ziro_load \
  --source=<repo|gh-slug|local-path> \        # e.g. "zsh-users/zsh-autosuggestions"
  --wait=<N|"0a"|"0b"|"0c"|"0"|""> \          # seconds | subslot | at-prompt | eager
  --wait-condition=<expr> \                   # Zsh expression gate (row 20)
  --sub-slot=<a|b|c> \                        # ordered slot; alternative to --wait form
  --lazy-by-command=<cmd> \                   # function-stub trigger (row 12)
  --lazy-by-function=<fn> \                   # trigger-load equivalent (row 13)
  --lazy=<bool> \                             # generic; true ⇒ at-prompt deferral
  --compile=<bool> \                          # .zwc control via znap ignore / zcompile (row 6)
  --pick=<file> \                             # main-file selection (row 2)
  --src=<file> \                              # explicit source file (row 3)
  --atinit=<code> \                           # pre-load code (row 4)
  --atload=<code> \                           # post-load code (row 5)
  --notify=<msg> \                            # failure stderr line (row 16)
  --lucid=<bool> \                            # silence auto-run noise (row 14; no-op on znap) ✱-impl
  --reset-prompt=<bool> \                     # zle .reset-prompt after load (row 15)
  --eval-cache=<command> \                    # eval output cached as function (row 7)
  --from-gh-release=<bool> \                  # release-asset install (row 7)
  --raw=<string>                              # ESCAPE HATCH — verbatim backend syntax
```

✱ Refinements: (i) `--raw` MUST be the last parameter of a call and is
mutually exclusive with all others except `--source` (validator in Layer 2
enforces; adapter injects verbatim); (ii) every `ziro_load` call MUST be
standalone and order-independent on line placement (sub-slot ordering is
carried by `--sub-slot`, not by file position) so future backends don't
inherit zsh-defer's queue-position coupling; (iii) the contract file
`ziro/adapters/contract.md` (generated from this ADR table) is the single
normative list — implementations that add parameters are out of contract.

Example (power-user escape hatch):
`ziro_load --source="foo/bar" --raw='wait"0a" lucid atload"echo custom"'`
→ znap adapter emits `znap source foo/bar` around the literal? **No** —
`--raw` bypasses the adapter: the literal string is injected where backend
syntax belongs (Zinit adapter: as ice block; znap adapter: executed as a
znap-unknown raw line only inside an `# @adapter-raw` guarded eval). Layer 3
owns that translation; Layers 1/2 never see it.

## Decision: **R3** — znap now, frozen contract, Zinit deferred

Rationale against the framework gates:
- **(a)** Matrix has one (c) row (Annexes), irrelevant to the 8 fixtures →
  R2 was *possible* — but see (d).
- **(b)** PR #19 merges unchanged under any option (Evidence 2) → R2 allowed.
- **(c)** Constitution can carry the amendment below → R2 allowed.
- **(d) Fails for full R2 today**: a znap `ziro_load` that genuinely
  implements rows 9-13, 17, 20 is a **zsh-defer integration + trigger shim**
  — that is new runtime machinery in the hot path (Layer 0 must clone/source
  zsh-defer), and honest znap-path `ziro_load` lands at 250-400 lines with
  the shim. Meanwhile the *Zinit* half of R2 would be written today with
  zero installed users — dead code the evidence gate (measurement-first,
  constitution Workflow) argues against.

R3 = R2's contract, minus the speculative implementation. It freezes the
adapter interface and this matrix now (the prompt's explicit requirement for
R3), makes the znap adapter a **pure implementation task** with no design
left, and reserves Zinit as 005. No row-17 "approximation" ever ships
unmeasured against the 19.6ms baseline.

## Consequences

**Easier**: PR #19 and all current flows untouched; Layer 1/2 specs lose the
znap/Zinit question permanently (contract is the vocabulary); Zinit adoption
becomes a self-contained 005 with a ready parity suite; annex-style
capabilities can be gained *later by backend*, not by rewriting layers.
**Harder**: deferred/lazy UX (rows 9-13) is *not available to users until
either 002 or 005 ships the shim — v1 ships eager-only `ziro_load`* (rows
1-8, 14, 19 today); two backend implementations must keep parity forever
(the test suite is the tax for OUT-3); `--raw` semantics differ per backend
by construction (documented in contract item i).
**Risk**: zsh-defer becomes a new Layer 0 dependency when lazy lands —
budgeted in 004, not absorbed silently.

## Constitution Amendment draft (v0.1.2 → v0.1.3, minimal)

**Before (Principle IV, second sentence):**
> For unknown plugins the fallback is eager loading (inspired by zinit's
> `wait"2" lucid` styles, adapted to the actual backend: loaded via
> `znap source` without any deferred wrapper, per the ordering contract of
> the active feature spec): correct first, fast second.

**After:**
> For unknown plugins the fallback is eager loading without any deferred
> wrapper: correct first, fast second. The runtime backend is reached only
> through the frozen adapter contract (`ziro_load`, ADR-001); znap is the
> default backend, and swapping backends MUST require only a new adapter
> implementation — never changes to Layers 1-2, user tags, or
> `plugins.gen.zsh`.

**Before (Principle VI, first sentence):** unchanged — **After**: append one
sentence:
> Backend-specific syntax is confined to the Layer 3 adapter; bootstrap and
> generated artifacts name `ziro_load` semantics only.

(Rationale comment block added per governance; version bump minor.)

## Parity Test Specification (implemented in spec 004; normative here)

For each matrix row R, a test case `parity_R` that: (1) loads the fixture
plugin for R via `ziro_load` with the row's parameter set; (2) asserts the
observable (widget bound / completion registered / function deferred then
defined / hook fired / `.zwc` present or absent / stderr notify on forced
failure); (3) when a second backend implements `ziro_load`, reruns the
identical suite and reports divergence as a CI failure. Rows 1-8, 14, 19 are
testable with znap today; 9-13, 15-17, 20 activate when their shim lands;
18 (Annexes) is marked `backend-specific: Zinit` and its "test" is the
Zinit-side suite passing without znap regression. The suite is the sole
guarantee OUT-3 remains true over time.

## Follow-up actions

1. `000-architecture`: Layer 3 renamed "Backend Adapter (frozen contract;
   znap default implementation)"; Schema C rewritten around `ziro_load`
   (below).
2. `001`: analysis `recommended.*` keys already align (`strategy|wait|
   compile|pick`); `ice_modifiers` → `adapter_options` rename to drop Zinit
   vocabulary from Layer 1 output.
3. Next specs, in order: `003a-tag-system-core` → `004-shell-bootstrap-layer0`
   (hosts parity suite + `ziro bench` + zsh-defer budget decision) →
   `003b-plugins-gen-format` (emits `ziro_load` blocks) →
   `002-backend-adapter-layer3-znap` (first implementation; eager-only v1).
4. `005-backend-adapter-layer3-zinit` — reserved number, not scheduled.

## Schema C revision (for 000-architecture)

`plugins.gen.zsh` becomes: header line, a `ziro_load` **implementation
select** line owned by Layer 3 (`source ${ZIRO_ADAPTER:-~/.config/ziro/adapter.zsh}`),
then `ziro_load --…` blocks per plugin — no znap or zinit syntax appears in
the generated file at all.
