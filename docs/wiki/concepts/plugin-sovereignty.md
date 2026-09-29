---
title: Plugin sovereignty
tags: [constitution, plugin, sovereignty, concept]
sourceRefs: ["/home/ali/.ziro/.specify/memory/constitution.md", "/home/ali/.ziro/.specify/specs/000-architecture/spec.md"]
lastReviewed: 2026-09-24
---

Constitution **XIV**: every plugin must remain standalone, usable without ziro.

## Rule

A plugin that ziro ships must not require ziro to be installed or loaded in
order to work. It may be sourced by any zsh setup.

## Consequences

1. **No ziro-specific API surface in plugins.** Plugins cannot call into
   ziro's internals or depend on its runtime state.
2. **ziro-defer is a deferral engine, not a dependency.** Deferred plugins
   load later but still function if deferred plainly.
3. **Local plugins are `source`d directly**, not passed to `znap source` —
   `znap source` only clones git repos. See [[concepts/znap-plugin-loading]].
4. **Layer A is never a runtime dependency of a published plugin**
   ([[sources/adr-003-two-layer-architecture]]): the Python analyzer and
   resolver are cold-path only. A plugin must load even if Python is absent
   or the analyzer has never run.

## Motivation

Ziro wants to be load-bearing infrastructure, not a trap. A user who installs
ziro and later removes it should keep working plugins, not a broken shell.

## Related

[[entities/ghost-plugin]] is the reference implementation of a sovereign
plugin. [[entities/plugin-analyzer]] respects this by being default-on but
never required at runtime (Constitution XII, Layered Optionality).
