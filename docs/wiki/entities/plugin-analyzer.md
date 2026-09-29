---
title: Plugin Analyzer (Layer 1)
tags: [layer1, analyzer, python, static-analysis]
sourceRefs: ["/home/ali/.ziro/.specify/specs/001-plugin-analyzer/spec.md", "/home/ali/.ziro/.specify/roadmap.json"]
lastReviewed: 2026-09-24
---

Static analysis of plugin sources. Spec 001. Layer A per
[[sources/adr-003-two-layer-architecture]].

## Contract

- **in**: plugin paths (git clones managed by
  [[entities/znap-runtime]])
- **out**: Schema A analysis cache →
  `~/.cache/ziro/analysis/<plugin>.json` (see [[concepts/xdg-path-layout]])
- **budget**: 5 s per plugin, async, parallel — cold path only
  ([[concepts/hot-path-cold-path]])
- **deps**: Python 3.12+, **stdlib only**, no PyO3, no third-party

## Constraints

- **Forbidden**: running in the hot path; writing to `~/.config/ziro/`
  (that's Layer 2's job — [[entities/tag-system]])
- Sovereignty: never a runtime dependency of a published plugin
  ([[concepts/plugin-sovereignty]])
- Default-on but user-disableable (Constitution XII)

## Quality criteria

Acceptance requires every defined test passing. No failing tests allowed.

## Output consumer

Layer 2 ([[entities/tag-system]]) consumes Schema A, merges user tags
(Schema B), and generates `plugins.gen.zsh` (Schema C). The analyzer never
writes the generated file.
