---
title: IRIS polling verification (archived)
tags: [irisa, verification, polling, hot-path]
sourceRefs: ["/home/ali/.ziro/.specify/reviews/_archive_2026-09-23/iris-polling-verification.md"]
lastReviewed: 2026-09-24
---

See [[concepts/hot-path-cold-path]] for context.

## Result

**OK** — all polling is in the Go daemon, zero Zsh hot-path cost.

## Evidence

- IRIS replaces the shell process via `exec iris` (Go binary owns the TTY)
- Zsh-side integration is event-driven only: four ZLE hooks
  (`line-pre-redraw`, `precmd`, `preexec`, `chpwd`), each a single
  `print -u $IRIS_FD` line
- All tickers are in Go:
  - `time.NewTicker(1s)` — config change detection
  - `time.Since()` — update check throttle (24 h default)
  - `minIntervalMS` gates — AI request rate limiting (1000 ms default)
- Zero matches for `time.Tick`/`time.NewTicker`/polling in any `.zsh` file

## Relevance to ziro

IRIS model (process replacement + event-driven hooks) is the architectural
pattern [[entities/ghost-plugin]]'s sovereignty requirement is checked
against. Ghost, by contrast, is sourced *into* zsh, so it must keep its own
footprint minimal.
