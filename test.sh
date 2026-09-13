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
    cp "$REPO/ziro-cli" "$d/"
    cp -r "$REPO/themes" "$d/"
    if [ -d "$REPO/znap" ]; then
        cp -r "$REPO/znap" "$d/"
    fi
    chmod +x "$d/ziro-cli"
    git -C "$d" init -q 2>/dev/null
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
git -C "$TMP/.ziro" remote set-url origin "https://github.com/Pakrohk-DotFiles/ziro-shell.git"
git -C "$TMP/.ziro" config http.lowSpeedLimit 1000
git -C "$TMP/.ziro" config http.lowSpeedTime 3
run_test_check "update" 0 "$TMP" \
    'test -f "$HOME/.ziro/.git/config"' \
    "$PY" "$ENGINE" update
rm -rf "$TMP"

# ═══════════════════════════════════════════════════════════════════════════════
# 7. Update with legacy (pre-rename) origin — allowed + healed
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 7. Update with dirty state ==="
TMP=$(mktemp -d /tmp/opencode/ziro-7-XXXX)
cp -r "$REPO" "$TMP/.ziro"
echo "# dirty" >> "$TMP/.ziro/readme.md"
git -C "$TMP/.ziro" config http.lowSpeedLimit 1000
git -C "$TMP/.ziro" config http.lowSpeedTime 3
run_test_check "update-dirty" 0 "$TMP" \
    'test -f "$HOME/.ziro/readme.md"' \
    "$PY" "$ENGINE" update
rm -rf "$TMP"

echo "=== 7b. Update heals legacy origin ==="
TMP=$(mktemp -d /tmp/opencode/ziro-7b-XXXX)
cp -r "$REPO" "$TMP/.ziro"
git -C "$TMP/.ziro" remote set-url origin https://github.com/Pakrohk-DotFiles/zsh_config.git
run_test_check "update-legacy-origin" 0 "$TMP" \
    'git -C "$HOME/.ziro" remote get-url origin | grep -q "Pakrohk-DotFiles/ziro-shell"' \
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
# 12. Theme packages — install copies default, list/current/apply work
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 12. Theme packages ==="
TMP=$(mktemp -d /tmp/opencode/ziro-12-XXXX)
seed_repo "$TMP/.ziro"
run_test_check "install-copies-default-theme" 0 "$TMP" \
    'test -f "$HOME/.config/starship.toml" && grep -q "Ziro starship prompt config" "$HOME/.config/starship.toml"' \
    "$PY" "$ENGINE" install --non-interactive --skip-deps --skip-shell
run_test "theme-list" 0 "$TMP" "$PY" "$ENGINE" theme list
# lambda must appear in the list
TOTAL=$((TOTAL + 1))
if HOME="$TMP" "$PY" "$ENGINE" theme list 2>/dev/null | grep -q "lambda"; then
    PASSED=$((PASSED + 1)); echo "[PASS] theme-list-shows-lambda"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - theme-list-shows-lambda\n"
    echo "[FAIL] theme-list-shows-lambda"
fi
run_test "theme-apply-lambda" 0 "$TMP" "$PY" "$ENGINE" theme apply lambda
# current reports the installed theme
TOTAL=$((TOTAL + 1))
if HOME="$TMP" "$PY" "$ENGINE" theme current 2>/dev/null | grep -q "lambda"; then
    PASSED=$((PASSED + 1)); echo "[PASS] theme-current"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - theme-current\n"
    echo "[FAIL] theme-current"
fi
run_test "theme-apply-unknown" 2 "$TMP" "$PY" "$ENGINE" theme apply bogus
# apply must refuse to clobber a differing user-owned file (rc=1, file intact)
TOTAL=$((TOTAL + 1))
printf '# my custom config\n' > "$TMP/.config/starship.toml"
actual_rc=0
HOME="$TMP" "$PY" "$ENGINE" theme apply lambda >/dev/null 2>&1 || actual_rc=$?
if [ "$actual_rc" -eq 1 ] && grep -q "my custom config" "$TMP/.config/starship.toml"; then
    PASSED=$((PASSED + 1)); echo "[PASS] theme-protect-user-file"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - theme-protect-user-file\n"
    echo "[FAIL] theme-protect-user-file"
fi
# --force overwrites
run_test_check "theme-apply-force" 0 "$TMP" \
    'grep -q "Ziro starship prompt config" "$HOME/.config/starship.toml"' \
    "$PY" "$ENGINE" theme apply lambda --force
rm -rf "$TMP"

# ═══════════════════════════════════════════════════════════════════════════════
# 12b. Theme schema strict validation
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 12b. Theme schema validation ==="
TMP=$(mktemp -d /tmp/opencode/ziro-12b-XXXX)
seed_repo "$TMP/.ziro"

# 12b-a. Valid lambda package is accepted
TOTAL=$((TOTAL + 1))
if HOME="$TMP" "$PY" "$ENGINE" theme list 2>/dev/null | grep -q "lambda"; then
    PASSED=$((PASSED + 1)); echo "[PASS] schema-valid-lambda"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - schema-valid-lambda\n"
    echo "[FAIL] schema-valid-lambda"
fi

# 12b-b. Missing [theme] section → package rejected
mkdir -p "$TMP/.ziro/themes/bad1"
printf 'name = "bad1"\nversion = "1.0.0"\ndescription = "bad"\n' > "$TMP/.ziro/themes/bad1/Theme.toml"
touch "$TMP/.ziro/themes/bad1/Starship.toml"
TOTAL=$((TOTAL + 1))
if ! HOME="$TMP" "$PY" "$ENGINE" theme list 2>/dev/null | grep -q "bad1"; then
    PASSED=$((PASSED + 1)); echo "[PASS] schema-reject-no-section"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - schema-reject-no-section\n"
    echo "[FAIL] schema-reject-no-section"
fi

# 12b-c. Missing required field (no version) → rejected
mkdir -p "$TMP/.ziro/themes/bad2"
printf '[theme]\nname = "bad2"\ndescription = "bad"\n' > "$TMP/.ziro/themes/bad2/Theme.toml"
touch "$TMP/.ziro/themes/bad2/Starship.toml"
TOTAL=$((TOTAL + 1))
if ! HOME="$TMP" "$PY" "$ENGINE" theme list 2>/dev/null | grep -q "bad2"; then
    PASSED=$((PASSED + 1)); echo "[PASS] schema-reject-missing-version"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - schema-reject-missing-version\n"
    echo "[FAIL] schema-reject-missing-version"
fi

# 12b-d. Empty name → rejected
mkdir -p "$TMP/.ziro/themes/bad3"
printf '[theme]\nname = ""\nversion = "1.0.0"\ndescription = "bad"\n' > "$TMP/.ziro/themes/bad3/Theme.toml"
touch "$TMP/.ziro/themes/bad3/Starship.toml"
TOTAL=$((TOTAL + 1))
if ! HOME="$TMP" "$PY" "$ENGINE" theme list 2>/dev/null | grep -q "bad3"; then
    PASSED=$((PASSED + 1)); echo "[PASS] schema-reject-empty-name"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - schema-reject-empty-name\n"
    echo "[FAIL] schema-reject-empty-name"
fi

# 12b-e. Missing Starship.toml → package rejected even with valid Theme.toml
mkdir -p "$TMP/.ziro/themes/bad4"
printf '[theme]\nname = "bad4"\nversion = "1.0.0"\ndescription = "bad"\n' > "$TMP/.ziro/themes/bad4/Theme.toml"
TOTAL=$((TOTAL + 1))
if ! HOME="$TMP" "$PY" "$ENGINE" theme list 2>/dev/null | grep -q "bad4"; then
    PASSED=$((PASSED + 1)); echo "[PASS] schema-reject-missing-starship"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - schema-reject-missing-starship\n"
    echo "[FAIL] schema-reject-missing-starship"
fi

# 12b-f. Missing author → rejected
mkdir -p "$TMP/.ziro/themes/bad5"
printf '[theme]\nname = "bad5"\nversion = "1.0.0"\ndescription = "bad"\nlicense = "MIT"\n' > "$TMP/.ziro/themes/bad5/Theme.toml"
touch "$TMP/.ziro/themes/bad5/Starship.toml"
TOTAL=$((TOTAL + 1))
if ! HOME="$TMP" "$PY" "$ENGINE" theme list 2>/dev/null | grep -q "bad5"; then
    PASSED=$((PASSED + 1)); echo "[PASS] schema-reject-missing-author"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - schema-reject-missing-author\n"
    echo "[FAIL] schema-reject-missing-author"
fi

# 12b-g. Missing license → rejected
mkdir -p "$TMP/.ziro/themes/bad6"
printf '[theme]\nname = "bad6"\nversion = "1.0.0"\ndescription = "bad"\nauthor = "test"\n' > "$TMP/.ziro/themes/bad6/Theme.toml"
touch "$TMP/.ziro/themes/bad6/Starship.toml"
TOTAL=$((TOTAL + 1))
if ! HOME="$TMP" "$PY" "$ENGINE" theme list 2>/dev/null | grep -q "bad6"; then
    PASSED=$((PASSED + 1)); echo "[PASS] schema-reject-missing-license"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - schema-reject-missing-license\n"
    echo "[FAIL] schema-reject-missing-license"
fi

# 12b-h. Name mismatch (Theme.toml name != directory name) → rejected
mkdir -p "$TMP/.ziro/themes/mismatch"
printf '[theme]\nname = "somethingelse"\nversion = "1.0.0"\ndescription = "mismatch"\nauthor = "test"\nlicense = "MIT"\n' > "$TMP/.ziro/themes/mismatch/Theme.toml"
touch "$TMP/.ziro/themes/mismatch/Starship.toml"
TOTAL=$((TOTAL + 1))
if ! HOME="$TMP" "$PY" "$ENGINE" theme list 2>/dev/null | grep -q "somethingelse"; then
    PASSED=$((PASSED + 1)); echo "[PASS] schema-reject-name-mismatch"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - schema-reject-name-mismatch\n"
    echo "[FAIL] schema-reject-name-mismatch"
fi

# 12b-i. Empty Starship.toml → rejected
mkdir -p "$TMP/.ziro/themes/emptystar"
printf '[theme]\nname = "emptystar"\nversion = "1.0.0"\ndescription = "empty"\nauthor = "test"\nlicense = "MIT"\n' > "$TMP/.ziro/themes/emptystar/Theme.toml"
printf '' > "$TMP/.ziro/themes/emptystar/Starship.toml"
TOTAL=$((TOTAL + 1))
if ! HOME="$TMP" "$PY" "$ENGINE" theme list 2>/dev/null | grep -q "emptystar"; then
    PASSED=$((PASSED + 1)); echo "[PASS] schema-reject-empty-starship"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - schema-reject-empty-starship\n"
    echo "[FAIL] schema-reject-empty-starship"
fi

# 12b-j. Invalid TOML in Starship.toml → rejected
mkdir -p "$TMP/.ziro/themes/badstar"
printf '[theme]\nname = "badstar"\nversion = "1.0.0"\ndescription = "bad"\nauthor = "test"\nlicense = "MIT"\n' > "$TMP/.ziro/themes/badstar/Theme.toml"
printf 'this is not { valid toml' > "$TMP/.ziro/themes/badstar/Starship.toml"
TOTAL=$((TOTAL + 1))
if ! HOME="$TMP" "$PY" "$ENGINE" theme list 2>/dev/null | grep -q "badstar"; then
    PASSED=$((PASSED + 1)); echo "[PASS] schema-reject-invalid-starship-toml"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - schema-reject-invalid-starship-toml\n"
    echo "[FAIL] schema-reject-invalid-starship-toml"
fi

# 12b-k. Non-semver version → rejected
mkdir -p "$TMP/.ziro/themes/badver"
printf '[theme]\nname = "badver"\nversion = "latest"\ndescription = "bad"\nauthor = "test"\nlicense = "MIT"\n' > "$TMP/.ziro/themes/badver/Theme.toml"
printf 'add_newline = true\n' > "$TMP/.ziro/themes/badver/Starship.toml"
TOTAL=$((TOTAL + 1))
if ! HOME="$TMP" "$PY" "$ENGINE" theme list 2>/dev/null | grep -q "badver"; then
    PASSED=$((PASSED + 1)); echo "[PASS] schema-reject-bad-version"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - schema-reject-bad-version\n"
    echo "[FAIL] schema-reject-bad-version"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 12c. Install must NOT copy an invalid default theme to ~/.config/starship.toml
#      (theme_file is weak; the strict list_themes gate must reject a broken
#       lambda Starship.toml instead of installing it.)
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 12c. install rejects broken default theme ==="
TMP=$(mktemp -d /tmp/opencode/ziro-12c-XXXX)
mkdir -p "$TMP/.ziro/themes/lambda"
cp "$REPO/.zshrc" "$REPO/.zsh_aliases" "$REPO/.gitignore" "$TMP/.ziro/" 2>/dev/null
[ -d "$REPO/znap" ] && cp -r "$REPO/znap" "$TMP/.ziro/"
printf '[theme]\nname = "lambda"\nversion = "1.0.0"\ndescription = "broken"\nauthor = "test"\nlicense = "MIT"\n' > "$TMP/.ziro/themes/lambda/Theme.toml"
printf 'this is not { valid toml' > "$TMP/.ziro/themes/lambda/Starship.toml"
git -C "$TMP/.ziro" init -q 2>/dev/null
run_test_check "install-skips-broken-default-theme" 0 "$TMP" \
    '! test -e "$HOME/.config/starship.toml"' \
    "$PY" "$ENGINE" install --non-interactive --skip-deps --skip-shell
rm -rf "$TMP"

# ═══════════════════════════════════════════════════════════════════════════════
# 12d. CLI symlink healed to ~/.ziro/ziro-cli after legacy migration
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 12d. CLI symlink after migration ==="
TMP=$(mktemp -d /tmp/opencode/ziro-12d-XXXX)
mkdir -p "$TMP/.zsh_config"
cp "$REPO/.zshrc" "$REPO/.zsh_aliases" "$REPO/.gitignore" "$REPO/ziro-cli" "$TMP/.zsh_config/" 2>/dev/null
cp -r "$REPO/themes" "$TMP/.zsh_config/"
[ -d "$REPO/znap" ] && cp -r "$REPO/znap" "$TMP/.zsh_config/"
git -C "$TMP/.zsh_config" init -q 2>/dev/null
git -C "$TMP/.zsh_config" remote add origin https://github.com/Pakrohk-DotFiles/ziro-shell.git
ln -sf "$TMP/.zsh_config/.zshrc" "$TMP/.zshrc"
mkdir -p "$TMP/.local/bin"
ln -sf "$TMP/.zsh_config/ziro-cli" "$TMP/.local/bin/ziro"
run_test_check "cli-symlink-healed-after-migration" 0 "$TMP" \
    'test "$(readlink "$HOME/.local/bin/ziro")" = "$HOME/.ziro/ziro-cli"' \
    "$PY" "$ENGINE" install --non-interactive --skip-deps --skip-shell
rm -rf "$TMP"

# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 13. Untrack .zshrc.local ==="
TMP=$(mktemp -d /tmp/opencode/ziro-14-XXXX)
cp -r "$REPO" "$TMP/.ziro"
rm -f "$TMP/.ziro/.zshrc.local"
printf 'export EDITOR=vim\n' > "$TMP/.ziro/.zshrc.local"
git -C "$TMP/.ziro" add -f .zshrc.local
git -C "$TMP/.ziro" -c user.email=t@t -c user.name=t commit -qm "track local"
run_test_check "update-untracks-zshrc-local" 0 "$TMP" \
    'grep -q "EDITOR=vim" "$HOME/.ziro/.zshrc.local" && ! git -C "$HOME/.ziro" ls-files --error -- .zshrc.local 2>/dev/null' \
    "$PY" "$ENGINE" update
rm -rf "$TMP"

# ═══════════════════════════════════════════════════════════════════════════════
# 14. Python package-map regression
# ═══════════════════════════════════════════════════════════════════════════════
echo "=== 14. Python package regression ==="

# Helper: query packages_for via Python, output space-separated base list
_py() {
    python3 -c "
from ziro.packages import packages_for
from ziro.platform import Platform
p = Platform(os_name='$1', pkg_mgr='$2')
base, extra = packages_for(p, '$3', $4, $5, $6, $7)
print('BASE:' + ' '.join(base))
print('EXTRA:' + ' '.join(extra))
" 2>/dev/null
}

check_has()    { echo "$1" | grep -qw "$2"; }
check_no()     { ! echo "$1" | grep -qw "$2"; }
check_in()     { check_has "$1" "$2"; }
check_not_in() { check_no "$1" "$2"; }

# ── 15a. Arch + Python: python present, virtualenvwrapper absent ──
TOTAL=$((TOTAL + 1))
out=$(_py Arch pacman Desktop True True True True)
if check_in "$out" "python" && check_not_in "$out" "python-virtualenvwrapper"; then
    PASSED=$((PASSED + 1)); echo "[PASS] arch-python-present-no-vw"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - arch-python-present-no-vw\n"
    echo "[FAIL] arch-python-present-no-vw"
fi

# ── 15b. Arch + no-python: python absent ──
TOTAL=$((TOTAL + 1))
out=$(_py Arch pacman Desktop False True True True)
if check_not_in "$out" "python"; then
    PASSED=$((PASSED + 1)); echo "[PASS] arch-no-python-absent"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - arch-no-python-absent\n"
    echo "[FAIL] arch-no-python-absent"
fi

# ── 15c. macOS + Python: python present, virtualenvwrapper absent ──
TOTAL=$((TOTAL + 1))
out=$(_py macOS brew Desktop True True True True)
if check_in "$out" "python" && check_not_in "$out" "python-virtualenvwrapper"; then
    PASSED=$((PASSED + 1)); echo "[PASS] mac-python-present-no-vw"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - mac-python-present-no-vw\n"
    echo "[FAIL] mac-python-present-no-vw"
fi

# ── 15d. macOS + no-python: python absent ──
TOTAL=$((TOTAL + 1))
out=$(_py macOS brew Desktop False True True True)
if check_not_in "$out" "python"; then
    PASSED=$((PASSED + 1)); echo "[PASS] mac-no-python-absent"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - mac-no-python-absent\n"
    echo "[FAIL] mac-no-python-absent"
fi

# ── 15e. Debian + Python: python3-venv present, python-virtualenvwrapper absent ──
TOTAL=$((TOTAL + 1))
out=$(_py "Debian/Ubuntu" apt Desktop True True True True)
if check_in "$out" "python3-venv" && check_not_in "$out" "python-virtualenvwrapper"; then
    PASSED=$((PASSED + 1)); echo "[PASS] debian-python-packages"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - debian-python-packages\n"
    echo "[FAIL] debian-python-packages"
fi

# ── 15f. Debian + no-python: python3-venv absent ──
TOTAL=$((TOTAL + 1))
out=$(_py "Debian/Ubuntu" apt Desktop False True True True)
if check_not_in "$out" "python3-venv"; then
    PASSED=$((PASSED + 1)); echo "[PASS] debian-no-python-absent"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - debian-no-python-absent\n"
    echo "[FAIL] debian-no-python-absent"
fi

# ── 15g. Fedora + Python: python3-virtualenvwrapper present ──
TOTAL=$((TOTAL + 1))
out=$(_py Fedora dnf Desktop True True True True)
if check_in "$out" "python3" && check_in "$out" "python3-virtualenvwrapper"; then
    PASSED=$((PASSED + 1)); echo "[PASS] fedora-python-packages"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - fedora-python-packages\n"
    echo "[FAIL] fedora-python-packages"
fi

# ── 15h. Fedora + no-python: python3-virtualenvwrapper absent ──
TOTAL=$((TOTAL + 1))
out=$(_py Fedora dnf Desktop False True True True)
if check_not_in "$out" "python3-virtualenvwrapper"; then
    PASSED=$((PASSED + 1)); echo "[PASS] fedora-no-python-absent"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - fedora-no-python-absent\n"
    echo "[FAIL] fedora-no-python-absent"
fi

# ── 15i. Core packages always present (Arch, all flags off) ──
TOTAL=$((TOTAL + 1))
out=$(_py Arch pacman Desktop False False False False)
has_core=true
for pkg in zsh git curl fzf starship; do
    check_in "$out" "$pkg" || has_core=false
done
if $has_core; then
    PASSED=$((PASSED + 1)); echo "[PASS] arch-core-packages"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - arch-core-packages\n"
    echo "[FAIL] arch-core-packages"
fi

# ── 15j. Core packages always present (Debian, all flags off) ──
TOTAL=$((TOTAL + 1))
out=$(_py "Debian/Ubuntu" apt Desktop False False False False)
has_core=true
for pkg in zsh git curl fzf starship; do
    check_in "$out" "$pkg" || has_core=false
done
if $has_core; then
    PASSED=$((PASSED + 1)); echo "[PASS] debian-core-packages"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - debian-core-packages\n"
    echo "[FAIL] debian-core-packages"
fi

# ── 15k. Server mode adds nmap, iftop, etc. (Arch) ──
TOTAL=$((TOTAL + 1))
out=$(_py Arch pacman Server True True True True)
if check_in "$out" "nmap" && check_in "$out" "iftop" && check_in "$out" "mtr"; then
    PASSED=$((PASSED + 1)); echo "[PASS] arch-server-net-packages"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - arch-server-net-packages\n"
    echo "[FAIL] arch-server-net-packages"
fi

# ── 15l. Language packages not in extras (Arch) ──
TOTAL=$((TOTAL + 1))
out=$(_py Arch pacman Desktop True True True True)
if check_not_in "$out" "EXTRA:python" && check_not_in "$out" "EXTRA:rustup" && check_not_in "$out" "EXTRA:go"; then
    PASSED=$((PASSED + 1)); echo "[PASS] arch-lang-not-in-extras"
else
    FAILED=$((FAILED + 1))
    ERRORS="${ERRORS}  - arch-lang-not-in-extras\n"
    echo "[FAIL] arch-lang-not-in-extras"
fi

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
