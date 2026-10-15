#!/usr/bin/env bash
# scripts/mirror-adrs.sh — Mirror ADRs from local .specify/decisions to docs/wiki/sources/
# Ensures architecture decisions are published in official docs without tracking .specify/

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="${REPO_ROOT}/.specify/decisions"
DEST_DIR="${REPO_ROOT}/docs/wiki/sources"

if [[ ! -d "$SRC_DIR" ]]; then
  echo "Error: source directory $SRC_DIR does not exist." >&2
  exit 1
fi

mkdir -p "$DEST_DIR"

# Canonical mappings for existing wiki source files
declare -A MAP=(
  ["ADR-001-backend-strategy.md"]="adr-001-backend-strategy.md"
  ["ADR-002-znap-permanent-zirodefer.md"]="adr-002-znap-permanent.md"
  ["ADR-003-two-layer-architecture.md"]="adr-003-two-layer-architecture.md"
  ["ADR-004-ziro-defer-fork-timing.md"]="adr-004-fork-timing.md"
  ["ADR-005-ziro-defer-directory-placement.md"]="adr-005-ziro-defer-directory-placement.md"
  ["ADR-006-ghost-architecture.md"]="adr-006-ghost-architecture.md"
  ["ADR-007-versioning-policy.md"]="adr-007-versioning-policy.md"
  ["ADR-008-roadmap-phases-7-9.md"]="adr-008-roadmap-phases.md"
)

count=0
for src in "$SRC_DIR"/ADR-*.md; do
  [[ -f "$src" ]] || continue
  filename="$(basename "$src")"
  dest_name="${MAP[$filename]:-$(echo "$filename" | tr '[:upper:]' '[:lower:]')}"
  dest="${DEST_DIR}/${dest_name}"

  if [[ ! -f "$dest" ]]; then
    echo "Creating mirror for $filename -> $dest_name"
    cp "$src" "$dest"
    count=$((count + 1))
  else
    if [[ "$src" -nt "$dest" ]]; then
      echo "Updating mirror for $filename -> $dest_name"
      cp "$src" "$dest"
      count=$((count + 1))
    fi
  fi
done

echo "ADR mirroring complete. Processed $count updates."
