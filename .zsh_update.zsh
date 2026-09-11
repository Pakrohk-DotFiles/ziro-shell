#!/bin/zsh

# --- Ziro Update Shim ---
# The update ENGINE is the Python CLI (ziro update). This file only:
#   1. provides the `zsh_update` function (backward compatibility), and
#   2. runs the background update check + notification (shell runtime).

# Resolve install dir: prefer new ~/.ziro, fall back to legacy ~/.zsh_config
if [[ -d "$HOME/.ziro" ]]; then
    ZSH_CONFIG_DIR="$HOME/.ziro"
else
    ZSH_CONFIG_DIR="${ZSH_CONFIG_DIR:-$HOME/.zsh_config}"
fi
LAST_CHECK_FILE="$ZSH_CONFIG_DIR/.last_update_check"
CHECK_INTERVAL=300 # 5 minutes cooldown to avoid redundant fetches

# Locate python3 once
_ziro_python="$(command -v python3 2>/dev/null)"

zsh_update() {
    if [[ -z "$_ziro_python" ]]; then
        echo -e "\e[31m[!] python3 not found; cannot run the Ziro update engine.\e[0m"
        return 1
    fi
    "$_ziro_python" "$ZSH_CONFIG_DIR/ziro/" update
}

# Backward-compat: some setups alias/autocomplete 'zsh_update'; keep name only.
check_for_updates() {
    # Only check if the directory is a git repository with the expected origin
    [[ -d "$ZSH_CONFIG_DIR/.git" ]] || return
    [[ -n "$_ziro_python" ]] || return
    local remote_url
    remote_url=$(git -C "$ZSH_CONFIG_DIR" remote get-url origin 2>/dev/null) || return
    [[ "$remote_url" == *Pakrohk-DotFiles/ziro-shell* || "$remote_url" == *Pakrohk-DotFiles/zsh_config* ]] || return

    local current_time=$(date +%s)
    local last_check=0
    [[ -f "$LAST_CHECK_FILE" ]] && last_check=$(cat "$LAST_CHECK_FILE")

    # Check if interval has passed
    if (( current_time - last_check > CHECK_INTERVAL )); then
        # Run the check in the background to avoid blocking the shell
        (
            cd "$ZSH_CONFIG_DIR"
            git fetch -q origin main > /dev/null 2>&1
            local local_hash=$(git rev-parse HEAD 2>/dev/null)
            local remote_hash=$(git rev-parse origin/main 2>/dev/null)
            [[ -z "$local_hash" || -z "$remote_hash" ]] && exit 0

            if [[ "$local_hash" != "$remote_hash" ]]; then
                # Create a flag file to notify the user
                touch "$ZSH_CONFIG_DIR/.update_available"
            fi
            echo "$current_time" > "$LAST_CHECK_FILE"
        ) &!
    fi

    # If an update was found, notify the user and remove the flag so they aren't spammed
    if [[ -f "$ZSH_CONFIG_DIR/.update_available" ]]; then
        send_notification
        rm -f "$ZSH_CONFIG_DIR/.update_available"
    fi
}

send_notification() {
    local title="Ziro Update"
    local msg="A new Ziro update is available! Run 'zsh_update' to install."

    # macOS system notification
    if [[ "$(uname)" == "Darwin" ]]; then
        osascript -e "display notification \"$msg\" with title \"$title\"" >/dev/null 2>&1
    # Linux system notification
    elif command -v notify-send >/dev/null 2>&1; then
        notify-send "$title" "$msg" >/dev/null 2>&1
    fi

    # Terminal message
    echo -e "\n\e[33m[*] A new update is available for Ziro!\e[0m"
    echo -e "\e[32m[*] Run: \e[34mzsh_update\e[0m to apply the updates automatically!\n"
}

check_for_updates
