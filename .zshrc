########################################
# Ziro ~/.zshrc - Complete ZSH Configuration
########################################

# --- Centralized Config Path ---
# All other config files are sourced from here.
# Supports both new (~/.ziro) and legacy (~/.zsh_config) install locations.
if [[ -d ~/.ziro ]]; then
    ZSH_CONFIG_DIR=~/.ziro
elif [[ -d ~/.zsh_config ]]; then
    ZSH_CONFIG_DIR=~/.zsh_config
else
    # Neither directory exists — not installed yet. Bail out early.
    return 2>/dev/null || exit 0
fi

# --- macOS-specific Homebrew environment setup ---
if [[ "$(uname)" == "Darwin" ]]; then
    # Bootstrap Homebrew path if brew is not in PATH
    if ! command -v brew >/dev/null 2>&1; then
        if [[ -f /opt/homebrew/bin/brew ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f /usr/local/bin/brew ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    fi
    # Ensure sbin is in PATH for tools like mtr
    [[ -d "/opt/homebrew/sbin" && ":$PATH:" != *":/opt/homebrew/sbin:"* ]] && export PATH="/opt/homebrew/sbin:$PATH"
    [[ -d "/usr/local/sbin" && ":$PATH:" != *":/usr/local/sbin:"* ]] && export PATH="/usr/local/sbin:$PATH"
fi

### --- Bootstrap Znap ---
# This must happen before sourcing .zshrc.local if it uses znap
[[ -r $ZSH_CONFIG_DIR/znap/znap.zsh ]] || git clone --depth 1 https://github.com/marlonrichert/zsh-snap.git $ZSH_CONFIG_DIR/znap
source $ZSH_CONFIG_DIR/znap/znap.zsh

# Disable warncreateglobal (enabled by znap opts) to silence plugin global-var warnings
setopt NO_WARN_CREATE_GLOBAL

########################################
# External Configs & Overrides (Priority)
########################################
# Load local overrides early to set environment type & language support variables
[ -f "$ZSH_CONFIG_DIR/.zshrc.local" ] && source "$ZSH_CONFIG_DIR/.zshrc.local"

# Force server mode if running as root
if [[ "$EUID" -eq 0 ]]; then
    export ZSH_ENV_TYPE='server'
fi

# Define defaults for language flags if not set by .zshrc.local
[[ -z "$ENABLE_PYTHON" ]] && export ENABLE_PYTHON="yes"
[[ -z "$ENABLE_RUST" ]] && export ENABLE_RUST="yes"
[[ -z "$ENABLE_GO" ]] && export ENABLE_GO="yes"
[[ -z "$ENABLE_NODE" ]] && export ENABLE_NODE="yes"

########################################
# ZSH Options
########################################
setopt AUTO_PUSHD
setopt AUTO_CD
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_SAVE_NO_DUPS
setopt INC_APPEND_HISTORY
setopt SHARE_HISTORY

########################################
# History
########################################
HISTFILE=~/.zsh_history
HISTSIZE=100000
SAVEHIST=100000

########################################
# Key Bindings
########################################
# bindkey -v  # vi-mode if you prefer
bindkey '^[[A' history-beginning-search-backward
bindkey '^[[B' history-beginning-search-forward
bindkey '^R' history-incremental-search-backward
bindkey '^P' up-line-or-search
bindkey '^N' down-line-or-search

########################################
# Completion
########################################
znap source zsh-users/zsh-completions
autoload -Uz compinit && compinit

zstyle ':completion:*' menu select
zstyle ':completion:*' use-cache on
zstyle ':completion:*' cache-path "$XDG_CACHE_HOME/zsh/.zcompcache"
zstyle ':completion:*:default' list-colors ${(s.:.)LS_COLORS}
zstyle ':completion:*:*:*:*:corrections' format '%F{yellow}!- %d (errors: %e) -!%f'
zstyle ':completion:*:messages' format ' %F{purple} -- %d --%f'
zstyle ':completion:*:warnings' format ' %F{red}-- no matches found --%f'
zstyle ':completion:*:descriptions' format '%F{yellow}%B%d%b%f'
zstyle ':completion:*' group-name ''
zstyle ':completion:*:*:-command-:*:*' group-order alias builtins functions commands
zstyle ':completion:*' squeeze-slashes true
zstyle ':completion:*' complete-options true
zstyle ':completion:*' matcher-list '' 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'
zstyle ':completion:*' rehash true
ENABLE_CORRECTION="true"

########################################
# Prompt / Theme
########################################
[ -f "$ZSH_CONFIG_DIR/.prompt.local" ] && source "$ZSH_CONFIG_DIR/.prompt.local"
znap prompt

########################################
# Plugins
########################################
znap source zdharma-continuum/fast-syntax-highlighting
znap source zsh-users/zsh-autosuggestions
znap source ohmyzsh/ohmyzsh plugins/git
znap source ohmyzsh/ohmyzsh plugins/colored-man-pages

# Server-specific network plugins
if [[ "$ZSH_ENV_TYPE" == "server" ]]; then
    znap source ohmyzsh/ohmyzsh plugins/nmap
fi

# Load heavier/non-essential plugins only on Desktop
if [[ "$ZSH_ENV_TYPE" != "server" ]]; then
    # zcolors: single plain `zcolors` script (no plugin.zsh), so `znap source`
    # cannot handle it. It is a program: put it on PATH; the `znap eval` below
    # runs `zcolors` and caches its output (which defines colors/functions).
    export PATH="$ZSH_CONFIG_DIR/marlonrichert/zcolors:$PATH"

    znap source mfaerevaag/wd
    znap source djui/alias-tips
    if [[ "$ENABLE_PYTHON" == "yes" ]]; then
        znap source ohmyzsh/ohmyzsh plugins/virtualenvwrapper
    fi
    znap source rupa/z
fi

# Evaluate zcolors (if loaded)
if [[ "$ZSH_ENV_TYPE" != "server" ]]; then
    znap eval zcolors "zcolors ${(q)LS_COLORS}"
fi

########################################
# Environment
########################################
# Defaults (only if not already set by .zshrc.local)
if [[ -z "$EDITOR" ]]; then
    if command -v nvim >/dev/null 2>&1; then
        export EDITOR='nvim'
    else
        export EDITOR='vim'
    fi
fi

[[ -z "$BROWSER" ]] && export BROWSER='echo'
[[ -z "$TERMINAL" ]] && export TERMINAL='xterm'
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"


########################################
# Aliases & Functions
########################################
# Keep the main config clean
[ -f "$ZSH_CONFIG_DIR/.zsh_aliases" ] && source "$ZSH_CONFIG_DIR/.zsh_aliases"

########################################
# Conditional loading based on environment
########################################
# Only load paru/fzf helper on Desktop environments
if [[ "$ZSH_ENV_TYPE" != "server" ]]; then
    [ -f "$ZSH_CONFIG_DIR/.paru_fzf.zsh" ] && source "$ZSH_CONFIG_DIR/.paru_fzf.zsh"
fi

# Dart completion
[ -f ~/.config/.dart-cli-completion/zsh-config.zsh ] && source ~/.config/.dart-cli-completion/zsh-config.zsh

# Background update check
[ -f "$ZSH_CONFIG_DIR/.zsh_update.zsh" ] && source "$ZSH_CONFIG_DIR/.zsh_update.zsh"

########################################
# Evals
########################################


########################################
# SSH Agent Management (Zsh Compatible)
# - Starts ssh-agent if not already running
# - Reuses environment across sessions
# - Loads key only once to avoid repeated passphrase prompts
# DISABLED on Server for security
########################################

if [[ "$ZSH_ENV_TYPE" != "server" ]]; then

SSH_ENV="$HOME/.ssh/agent-environment"

# Start a new ssh-agent and save its environment variables
start_agent() {
    /usr/bin/ssh-agent | sed 's/^echo/#echo/' > "$SSH_ENV"
    chmod 600 "$SSH_ENV"
    . "$SSH_ENV" >/dev/null
}

# Add private key if agent has no keys loaded
load_keys() {
    if ! ssh-add -l >/dev/null 2>&1; then
        ssh-add ~/.ssh/id_ed25519 >/dev/null 2>&1
    fi
}

# Restore existing agent environment if available
if [[ -f "$SSH_ENV" ]]; then
    . "$SSH_ENV" >/dev/null
    if ! kill -0 "$SSH_AGENT_PID" >/dev/null 2>&1; then
        start_agent
    fi
else
    start_agent
fi

# Ensure environment is valid
if [[ -z "$SSH_AUTH_SOCK" ]] || ! kill -0 "$SSH_AGENT_PID" >/dev/null 2>&1; then
    start_agent
fi

# Load keys only if necessary
load_keys

fi # End of SSH Agent check

########################################
# Fallback for custom functions
########################################
[ -d "$ZSH_CONFIG_DIR/.zfunc" ] && fpath+="$ZSH_CONFIG_DIR/.zfunc"
autoload -Uz compinit
compinit

########################################
# End of Ziro ~/.zshrc
########################################
