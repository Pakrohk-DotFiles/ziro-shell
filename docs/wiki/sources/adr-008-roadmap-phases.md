# ADR-008: Roadmap Phases 7-9 and Per-Plugin Repositories

**Status**: Adopted  
**Date**: 2026-10-15  
**Authors**: Ziro Shell Architecture Team  
**Relates to**: Constitution Principle XIV (Plugin Sovereignty), Principle XV (Versioning Discipline), ADR-006, ADR-007, Spec 009, Spec 010  

---

## Context

Following the release of Ziro Shell `v1.0.1` (CLI Modernization & Rich UI), the project has transitioned from its foundational core into ecosystem expansion and repository hygiene. Over the course of earlier implementation cycles, several legacy artifacts, untracked temporary files, and personal helper files accumulated within the working repository.

Simultaneously, the architectural roadmap requires explicit definitions for upcoming milestones (Phases 7, 8, and 9) to maintain strict adherence to the 3-tier versioning policy established in ADR-007 and Constitution Principle XV.

A critical design tension emerged regarding whether ecosystem plugins—specifically Ziro Ghost, the upcoming `pf` cross-shell package manager, and shell alias helpers—should reside inside the core `ziro-shell` repository as monorepo subdirectories or be hosted in dedicated, sovereign repositories under `Pakrohk`.

Finally, repository governance rules require reiterating that internal specification and tracking files in `.specify/` remain strictly local and must never be force-added to git tracking.

---

## Decisions

### 1. Phase-to-Version Mapping (Phases 7 through 9)

In accordance with ADR-007 (Patch Tier for internal cleanup, optimizations, and plugin integrations):

| Phase | Target Version | Release Name & Scope | Tier |
|---|---|---|---|
| **Phase 7** | **`v1.0.2`** | **Project Cleanup & Hygiene**: Safe removal of ~15MB junk/backups, removal of personal configuration files, minimal 30-line `.zshrc` template rewrite, internalization of update routines into `ziro update`, public documentation sanitization, and capture of `pf` architecture in Spec 010. | Patch (`X.X.Y`) |
| **Phase 8** | **`v1.1.2`** | **Ziro Ghost Standalone Plugin**: Formal release of the `POSTDISPLAY` history autosuggestion engine, standalone test matrix, integration into `ziro suggest`, and packaging. | Patch (`X.X.Y`) |
| **Phase 9** | **`v1.1.5`** | **`pf` Package Manager & Helper Aliases**: High-performance interactive package management CLI (`pf`) supporting dual-mode interactive fzf and subcommand execution across pacman/paru/apt/dnf/brew/etc., plus standard helper aliases. | Patch (`X.X.Y`) |

### 2. Per-Plugin Repositories (Plugin Sovereignty Architecture)

Per Constitution Principle XIV (Plugin Sovereignty), every published plugin must operate completely standalone without assuming the presence of Ziro Shell or Python. To enforce true modularity, blast-radius isolation, and independent release lifecycles, ecosystem plugins will each reside in a dedicated GitHub repository under `Pakrohk`:

1. **`pf` Plugin**: `github.com/Pakrohk/ziro-pf`
   - Independent cross-shell package manager (POSIX core + Zsh wrapper + fzf integration).
2. **`ghost` Plugin**: `github.com/Pakrohk/ziro-ghost`
   - Standalone history autosuggestion plugin (pure Zsh, fast POSTDISPLAY, fuzzy search).
3. **`helpers` Plugin**: `github.com/Pakrohk/ziro-helpers`
   - Reusable shell aliases, functions, and navigation shortcuts decoupled from personal configurations.

**Rationale**:
- **Isolation**: Prevents core repository bloat and dependency leaks.
- **Sovereignty**: Users of Oh My Zsh, Prezto, Zim, or vanilla Zsh can install plugins directly without installing `ziro-shell`.
- **Independent Versioning**: Plugins can patch bugs and evolve their CLI syntax on their own semver schedules.
- **Ziro Distribution**: Ziro's Layer 0/Layer 3 engine clones and manages these repositories automatically via znap/git into `~/.local/share/ziro/plugins/`.

### 3. Repository Governance & `.specify/` Protection

- Internal planning documents, prompt specifications, and audit records residing in `.specify/` and `.opencode/` are strictly local developer state.
- **Rule H1 Prohibition**: Running `git add -f` on `.specify/`, `.opencode/`, or `plugins/` is strictly prohibited. Public documentation and architecture decisions must be mirrored to `docs/wiki/sources/` using `scripts/mirror-adrs.sh`.

### 4. Deferred Architectural Decisions (Future Candidates)

Two significant long-term architectural proposals are formally deferred and cataloged as candidates for future ADRs:

- **ADR-009 Candidate — znap Native Rewrite (Rust / PyO3)**:
  - *Proposal*: Rewrite the znap clone and compilation engine in Rust/PyO3 for sub-millisecond execution.
  - *Disposition*: Deferred to `v2.0.0+` (Major Tier). The current Python stdlib + pure Zsh Layer 0 meets all performance budgets (< 5ms hot-path).
- **ADR-010 Candidate — Bash-Compatible Integration Layer**:
  - *Proposal*: Provide an engine compatibility layer for GNU Bash.
  - *Disposition*: Deferred to a separate standalone project. Ziro Shell remains hyper-optimized for Zsh 5.8+.

---

## Consequences

- **Clear Roadmap**: Contributors and users have unambiguous expectations for `v1.0.2`, `v1.1.2`, and `v1.1.5`.
- **Ecosystem Cleanliness**: Core `ziro-shell` remains lean and focused on runtime bootstrap, plugin analysis, tag resolution, and CLI dispatch.
- **Public vs. Local State**: Architecture decisions are mirrored to `docs/wiki/sources/adr-008-roadmap-phases.md` while `.specify/` remains untracked.
