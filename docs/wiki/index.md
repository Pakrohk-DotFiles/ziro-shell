# Ziro Wiki — Index

Knowledge base for the ziro zsh configuration framework. Source layer is
immutable (code, docs); this layer synthesizes it.

## Overview

- [[entities/ziro]] — Ziro framework overview: layers, entry points, governing docs

## Entities — modules and components

- [[entities/shell-bootstrap]] — Layer 0, `integration.zsh` sourcing order + 5 ms budget
- [[entities/plugin-analyzer]] — Layer 1, Python static analysis, stdlib only
- [[entities/tag-system]] — Layer 2, tag resolution + `plugins.gen.zsh` generation
- [[entities/znap-runtime]] — Layer 3, znap + ziro-defer runtime, frozen backend
- [[entities/cli]] — `ziro.zsh` dispatcher + `commands/*.zsh` modules
- [[entities/ghost-plugin]] — ziro-ghost: sovereign ZLE autosuggestion plugin

## Concepts — patterns and conventions

- [[concepts/hot-path-cold-path]] — 5 ms / 5 s budget contract (roadmap P1)
- [[concepts/plugin-sovereignty]] — Constitution XIV: every plugin standalone
- [[concepts/xdg-path-layout]] — `lib/xdg.zsh` as the path source of truth
- [[concepts/znap-plugin-loading]] — `znap source` only clones git repos; local files `source` directly
- [[concepts/defer-naming-split]] — generator emits `ziro-defer`; vendored runtime only defines `zsh-defer` — broken deferred loads
- [[concepts/test-hermeticity]] — tests must not read the installed `~/.config/ziro`; CI has no HOME files

## Sources — external and decision documents

- [[sources/adr-002-znap-permanent]] — znap permanent backend; ziro-defer canonical
- [[sources/adr-003-two-layer-architecture]] — Python core + zsh CLI split
- [[sources/adr-004-fork-timing]] — ziro-defer fork deferred until bootstrap done; trigger fired, fork started
- [[sources/adr-005-ziro-defer-directory-placement]] — ziro-defer fork lives in own top-level dir, not vendor/ or ghost/
- [[sources/iris-polling-verification]] — Historical: IRIS evaluation (rejected; replaced by Ziro Ghost)

## Conventions

- Page frontmatter: `title`, `tags`, `sourceRefs`, `lastReviewed`
- One concept per page; cross-reference with `[[wiki/page-name]]`
- Append changes to [[log]]
