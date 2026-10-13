---
title: ADR-007 — Versioning Policy & Release Tier Discipline
tags: [adr, versioning, governance, roadmap]
sourceRefs: ["/home/ali/.ziro/.specify/decisions/ADR-007-versioning-policy.md"]
lastReviewed: 2026-10-13
---

# ADR-007: Versioning Policy & Release Tier Discipline

**Status**: Adopted  
**Date**: 2026-10-13  
**Authors**: Ziro Shell Architecture Team  
**Relates to**: Constitution Principle XV, Spec 000, CHANGELOG.md  

---

## Context

Ziro Shell released its `v1.0.0` milestone as the "Foundation Release" (establishing Layer 0 bootstrap, frozen `ziro_load` emitter, XDG directory layout, and the CLI baseline).

As development moves into feature enhancements, standalone plugins, and sub-systems, a formal, disciplined semantic versioning scheme is required to guide release planning, avoid version number inflation, and provide unambiguous expectations to users and contributors.

---

## Decision

The project formally adopts a strict 3-tier versioning policy:

### 1. Version Number Semantics

| Tier | Format | Trigger Criteria | Scope & Examples |
|---|---|---|---|
| **Patch Tier** | `X.X.Y` | Bug fixes, internal optimizations, UI polish, CLI UX enhancements, standalone plugin additions | `v1.0.1` (CLI Modernization & Rich UI), `v1.1.2` (Ziro Ghost standalone plugin) |
| **Patch-Large Tier** | `X.X.Y` (jump) | Major component within existing architecture layers | `v1.0.5` (Layer 1 Static Analyzer engine) |
| **Minor Tier** | `X.Y.X` | Large new features, full multi-layer subsystem orchestrations | `v1.1.0` (Full Pipeline integration: L1 Analyzer + L2 Tag System + Code Generator) |
| **Major Tier** | `Y.X.X` | Fundamental architecture rewrites, breaking core principles | `v2.0.0` (Complete paradigm shift or breaking Layer 0 contract) |

### 2. Roadmap Mapping

The immediate version progression following `v1.0.0` is structured as follows:

| Target Version | Milestone / Scope | Tier Classification |
|---|---|---|
| **v1.0.0** | **Foundation Release** (shipped `1a1212d` / PR #20) | Baseline Major |
| **v1.0.1** | **CLI Modernization** (Help system, Rich UI, Zsh tab completion, spec 008) | Patch Tier (UX polish & interface robustness) |
| **v1.0.5** | **Layer 1 Analyzer** (Plugin AST / regex parser, signal classifier, spec 001) | Patch-Large Tier (Layer 1 component) |
| **v1.1.0** | **Full Pipeline** (Analyzer + Tag Resolver + `plugins.gen.zsh` generation) | Minor Tier (Subsystem orchestration) |
| **v1.1.2** | **Ziro Ghost Plugin** (Standalone POSTDISPLAY fuzzy autosuggestion, spec 009) | Patch Tier (Standalone plugin addition) |

### 3. Release Rules

1. Standalone plugins (e.g. Ghost) adhere to Constitution Principle XIV (Plugin Sovereignty) and land in the **Patch tier** since they operate independently without altering the core shell bootstrap architecture.
2. Polish, refactoring, and UI improvements never bump the minor version; they land strictly in the **Patch tier**.
3. CHANGELOG entries must be clearly grouped and state the release tier.
4. Git tags must strictly follow `vX.Y.Z` matching the release tier.

---

## Consequences

- **Constitution**: Amended to `v0.2.0` by ratifying **Principle XV (Semantic Versioning Discipline)**.
- **Documentation**: `CHANGELOG.md` explicitly documents release tiers, reclassifying `v1.0.0` as the Foundation Release.
- **Workflow**: PRs and branches target specific tier releases (e.g. `feat/cli-modernization` targets `v1.0.1`).
- **Public Visibility**: Mirrored to `docs/wiki/sources/adr-007-versioning-policy.md` per the Option A documentation policy.

---

## References

- Constitution: `Principle XV` (`.specify/memory/constitution.md`)
- Spec 000: Architecture Overview (`.specify/specs/000-architecture/spec.md`)
- Spec 008: Modular CLI Architecture (`.specify/specs/008-modular-cli/spec.md`)
- Spec 009: Ziro Ghost Plugin (`.specify/specs/009-ziro-ghost-plugin/spec.md`)
- ADR-003: Two-Layer Architecture (`docs/wiki/sources/adr-003-two-layer-architecture.md`)
