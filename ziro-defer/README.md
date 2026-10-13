# ziro-defer

Progressive fork of [romkatv/zsh-defer](https://github.com/romkatv/zsh-defer)
with additional features for the ziro-shell layered runtime.

## Status

| Version | Feature | Status |
|---------|---------|--------|
| v0.1.0  | MVP wrapper (`--wait=N` → `-t N`) | ✅ current |
| v0.2.0  | Sub-slot priority (`--slot=a\|b\|c`) | ⏳ planned |
| v0.3.0  | Lazy-by-command, Lazy-by-function | ⏳ planned |
| v0.4.0  | Init/load hooks, auto re-registration | ⏳ planned |
| v1.0.0  | Full spec 005 feature set | ⏳ planned |

## Why a fork?

Upstream `zsh-defer` is stable but minimal. The ziro-shell project
needs additional capabilities (sub-slots, conditional deferral,
batch loading, metrics) that are not in upstream's scope.

See `.specify/specs/005-znap-optimization-zirodefer/spec.md`
and `.specify/decisions/ADR-004-ziro-defer-fork-timing.md`.

## Directory structure

```
ziro-defer/
├── ziro-defer.plugin.zsh       ← our wrapper (fork entry point)
├── upstream/
│   ├── zsh-defer.plugin.zsh    ← vendored upstream (MIT, attributed)
│   └── LICENSE                 ← romkatv's MIT license
├── LICENSE                     ← our MIT license
└── README.md                   ← this file
```

## Installation (for ziro-shell)

`integration.zsh` sources this file before `plugins.gen.zsh`:

```zsh
if [[ -r "$ZIRO_HOME/ziro-defer/ziro-defer.plugin.zsh" ]]; then
  source "$ZIRO_HOME/ziro-defer/ziro-defer.plugin.zsh"
fi
```

## Installation (standalone, future)

Once moved to its own GitHub repository:

```zsh
znap source Pakrohk-DotFiles/ziro-defer
```

## API

### Supported today

| Arg | Behavior |
|-----|----------|
| `--wait=N` | Defer execution by N seconds (`-t N` upstream) |
| `-t N` | Upstream passthrough |
| `cmd ...` | Command to defer |

### Accepted but ignored (until v0.2+)

| Arg | Future feature |
|-----|----------------|
| `--slot=a\|b\|c` | Sub-slot priority |
| `--lazy-by-command=CMD` | Load after CMD first runs |
| `--lazy-by-function=FN` | Load after FN is defined |
| `--atinit=CODE` | Pre-load hook |
| `--atload=CODE` | Post-load hook |

## License

- Our wrapper: MIT (see `LICENSE`)
- Upstream `zsh-defer`: MIT (see `upstream/LICENSE`)

## Lineage

Forked from `romkatv/zsh-defer` (upstream commit preserved at
`upstream/`). Updates from upstream are merged manually as needed.

## Migration plan

When this fork matures (v1.1.0), it moves to:
`https://github.com/Pakrohk-DotFiles/ziro-defer`

Current location remains valid during transition.
