#!/usr/bin/env bash
# Ziro test suite — isolated temp HOME runs.
# No sudo, no network, no damage to real user files.
#
# Design:
#   - Each test creates its own TMP dir, uses it as HOME, then rm -rf's it.
#   - No nested subshells creating their own tmpdirs.
#   - No `|| true` masking real failures.
#   - Exit code captured via `|| actual_rc=$?` pattern (not set -e).

PY="${ZIRO_PY:-python3}"
REPO="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ENGINE="$REPO/ziro/"
TOTAL=0; PASSED=0; FAILED=0; ERRORS=""

# run_test NAME EXPECTED_RC HOME_DIR CMD [ARGS...]
run_test() {
    local name="$1" expected_rc="$2" home="$3"; shift 3
    TOTAL=$((TOTAL + 1))
    local actual_rc=0
    HOME="$home" "$@" >/dev/null 2>&1 || actual_rc=$?
    if [ "$actual_rc" -eq "$expected_rc" ]; then
        PASSED=$((PASSED + 1)); echo "[PASS] $name"
    else
        FAILED=$((FAILED + 1))
        ERRORS="${ERRORS}  - ${name} (expected rc=${expected_rc}, got rc=${actual_rc})\n"
        echo "[FAIL] $name — expected rc=$expected_rc got rc=$actual_rc"
    fi
}

# run_test_check NAME EXPECTED_RC HOME_DIR VERIFY_CMD CMD [ARGS...]
run_test_check() {
    local name="$1" expected_rc="$2" home="$3" verify="$4"; shift 4
    TOTAL=$((TOTAL + 1))
    local actual_rc=0 vrc=0
    HOME="$home" "$@" >/dev/null 2>&1 || actual_rc=$?
    if [ "$actual_rc" -ne "$expected_rc" ]; then
        FAILED=$((FAILED + 1))
        ERRORS="${ERRORS}  - ${name} (cmd rc=${actual_rc}, expected ${expected_rc})\n"
        echo "[FAIL] $name — cmd expected rc=$expected_rc got rc=$actual_rc"
        return
    fi
    HOME="$home" bash -c "$verify" >/dev/null 2>&1 || vrc=$?
    if [ "$vrc" -eq 0 ]; then
        PASSED=$((PASSED + 1)); echo "[PASS] $name"
    else
        FAILED=$((FAILED + 1))
        ERRORS="${ERRORS}  - ${name} (verify failed)\n"
        echo "[FAIL] $name — verify failed"
    fi
}

# seed_repo DIR — copy a minimal Ziro repo into DIR (no znap plugins, no .zwc)
seed_repo() {
    local d="$1"
    mkdir -p "$d"
    cp "$REPO/.zshrc" "$d/"
    cp "$REPO/.zsh_aliases" "$d/"
    cp "$REPO/.gitignore" "$d/"
    if [ -d "$REPO/znap" ]; then
        cp -r "$REPO/znap" "$d/"
    fi
    git -C "$d" init -q 2>/dev/null
    git -C "$d" remote add origin https://github.com/Pakrohk-DotFiles/ziro-shell.git 2>/dev/null || true
}

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Dry-run — no filesystem changes
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 1. Dry-run ==="
TMP=$(mktemp -d /tmp/opencode/ziro-1-XXXX)
run_test "dry-run" 0 "$TMP" \
    "$PY" "$ENGINE" install --dry-run --non-interactive --skip-shell
rm -rf "$TMP"

# ═══════════════════════════════════════════════════════════════════════════════
# 2. Fresh install — creates ~/.ziro, ~/.zshrc symlink, .zshrc.local, CLI
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 2. Fresh install ==="
TMP=$(mktemp -d /tmp/opencode/ziro-2-XXXX)
run_test_check "fresh-install" 0 "$TMP" \
    'test -f "$HOME/.ziro/.zshrc" && test -f "$HOME/.ziro/.zshrc.local" && test -L "$HOME/.zshrc" && test "$(readlink "$HOME/.zshrc")" = "$HOME/.ziro/.zshrc" && test -f "$HOME/.ziro/ziro-cli" && test -L "$HOME/.local/bin/ziro" && test "$(readlink "$HOME/.local/bin/ziro")" = "$HOME/.ziro/ziro-cli"' \
    "$PY" "$ENGINE" install --non-interactive --skip-deps --skip-shell
rm -rf "$TMP"

# ═══════════════════════════════════════════════════════════════════════════════
# 3. Idempotent re-install — .zshrc.local user edits preserved
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 3. Idempotent re-install ==="
TMP=$(mktemp -d /tmp/opencode/ziro-3-XXXX)
seed_repo "$TMP/.ziro"
echo "user custom" > "$TMP/.ziro/.zshrc.local"
run_test_check "idem-install" 0 "$TMP" \
    'grep -q "user custom" "$HOME/.ziro/.zshrc.local"' \
    "$PY" "$ENGINE" install --non-interactive --skip-deps --skip-shell
rm -rf "$TMP"

# ═══════════════════════════════════════════════════════════════════════════════
# 4. Doctor (real environment — runs against actual repo)
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 4. Doctor ==="
TOTAL=$((TOTAL + 1))
actual_rc=0
python3 "$ENGINE" doctor >/dev/null 2>&1 || actual_rc=$?
if [ "$actual_rc" -eq 0 ]; then
    PASSED=$((PASSED + 1)); echo "[PASS] doctor"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - doctor (expected rc=0, got rc=${actual_rc})\n"
    echo "[FAIL] doctor — expected rc=0 got rc=$actual_rc"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 5. --version
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 5. Version ==="
TMP=$(mktemp -d /tmp/opencode/ziro-5-XXXX)
run_test "version" 0 "$TMP" "$PY" "$ENGINE" --version
rm -rf "$TMP"

# ═══════════════════════════════════════════════════════════════════════════════
# 6. Update (same commit, no-op)
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 6. Update ==="
TMP=$(mktemp -d /tmp/opencode/ziro-6-XXXX)
cp -r "$REPO" "$TMP/.ziro"
run_test_check "update" 0 "$TMP" \
    'test -f "$HOME/.ziro/.git/config"' \
    "$PY" "$ENGINE" update
rm -rf "$TMP"

# ═══════════════════════════════════════════════════════════════════════════════
# 7. Update with dirty state (stash + restore)
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 7. Update with dirty state ==="
TMP=$(mktemp -d /tmp/opencode/ziro-7-XXXX)
cp -r "$REPO" "$TMP/.ziro"
echo "# dirty" >> "$TMP/.ziro/readme.md"
run_test_check "update-dirty" 0 "$TMP" \
    'test -f "$HOME/.ziro/readme.md"' \
    "$PY" "$ENGINE" update
rm -rf "$TMP"

# ═══════════════════════════════════════════════════════════════════════════════
# 8. Migration: ~/.zsh_config -> ~/.ziro
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 8. Migration ==="
TMP=$(mktemp -d /tmp/opencode/ziro-8-XXXX)
mkdir -p "$TMP/.zsh_config"
for f in .zshrc .zsh_aliases .zsh_update.zsh .prompt.local .gitignore .zshrc.local readme.md install.sh install.ps1; do
    cp "$REPO/$f" "$TMP/.zsh_config/" 2>/dev/null || true
done
cp -r "$REPO/znap" "$TMP/.zsh_config/"
git -C "$TMP/.zsh_config" init -q 2>/dev/null
git -C "$TMP/.zsh_config" remote add origin https://github.com/Pakrohk-DotFiles/ziro-shell.git
sed -i 's|ZSH_CONFIG_DIR=~/.ziro|ZSH_CONFIG_DIR=~/.zsh_config|' "$TMP/.zsh_config/.zshrc"
echo "legacy user config" > "$TMP/.zsh_config/.zshrc.local"
ln -sf "$TMP/.zsh_config/.zshrc" "$TMP/.zshrc"
run_test_check "migration" 0 "$TMP" \
    'test -d "$HOME/.ziro" && ! test -d "$HOME/.zsh_config" && grep -q "ZSH_CONFIG_DIR=~/.ziro" "$HOME/.ziro/.zshrc" && grep -q "legacy user config" "$HOME/.ziro/.zshrc.local"' \
    "$PY" "$ENGINE" install --non-interactive --skip-deps --skip-shell
rm -rf "$TMP"

# ═══════════════════════════════════════════════════════════════════════════════
# 9. Broken symlink ~/.zshrc — replaced with valid symlink
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 9. Broken symlink ==="
TMP=$(mktemp -d /tmp/opencode/ziro-9-XXXX)
seed_repo "$TMP/.ziro"
ln -sf /nonexistent "$TMP/.zshrc"
run_test_check "broken-symlink" 0 "$TMP" \
    'test -L "$HOME/.zshrc" && test "$(readlink "$HOME/.zshrc")" = "$HOME/.ziro/.zshrc"' \
    "$PY" "$ENGINE" install --non-interactive --skip-deps --skip-shell
rm -rf "$TMP"

# ═══════════════════════════════════════════════════════════════════════════════
# 10. User-owned regular .zshrc — backed up, not destroyed
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 10. User-owned .zshrc ==="
TMP=$(mktemp -d /tmp/opencode/ziro-10-XXXX)
seed_repo "$TMP/.ziro"
echo "export FOO=bar" > "$TMP/.zshrc"
run_test_check "user-owned" 0 "$TMP" \
    'bak=$(ls "$HOME"/.zshrc.bak.* 2>/dev/null | head -1) && test -n "$bak" && grep -q "FOO=bar" "$bak"' \
    "$PY" "$ENGINE" install --non-interactive --skip-deps --skip-shell
rm -rf "$TMP"

# ═══════════════════════════════════════════════════════════════════════════════
# 11. Doctor on legacy install — correctly reports failures (rc=1)
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 11. Legacy doctor ==="
TMP=$(mktemp -d /tmp/opencode/ziro-11-XXXX)
mkdir -p "$TMP/.zsh_config"
cp "$REPO/.zshrc" "$TMP/.zsh_config/"
cp "$REPO/.zsh_update.zsh" "$TMP/.zsh_config/"
git -C "$TMP/.zsh_config" init -q 2>/dev/null
git -C "$TMP/.zsh_config" remote add origin https://github.com/Pakrohk-DotFiles/ziro-shell.git
ln -sf "$TMP/.zsh_config/.zshrc" "$TMP/.zshrc"
run_test "legacy-doctor" 1 "$TMP" "$PY" "$ENGINE" doctor
rm -rf "$TMP"

# ═══════════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "================================================"
printf "  RESULTS: %d/%d passed, %d failed\n" "$PASSED" "$TOTAL" "$FAILED"
echo "================================================"

if [ "$FAILED" -gt 0 ]; then
    printf "FAILED TESTS:\n%s" "$ERRORS"
    exit 1
fi

echo "All tests passed."
