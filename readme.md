# Ziro

> Zero setup. Just a better shell.

Ziro is a complete shell environment for developers and power users. It installs Zsh, Starship, syntax highlighting, autosuggestions, completions, and a curated set of aliases and functions. Everything lives in `~/.ziro` and updates with a single command.

## What it installs

- Zsh with fast startup
- [Starship](https://starship.rs/) prompt (auto-installed)
- [zsh-snap](https://github.com/marlonrichert/zsh-snap) plugin manager
- `fast-syntax-highlighting`, `zsh-autosuggestions`, `zsh-completions`
- `pf` - interactive `fzf` package manager (supports pacman, brew, apt, dnf, apk, zypper)
- Aliases: `mkcd`, `cdf`, `up`, `extract`, `softar`, `cheat`, `refonts`, `rebuild_system` (Arch), `reflectmirrors` (Arch)
- `z` for directory jumping, `wd` for bookmarks, `alias-tips`
- SSH agent management (desktop only)
- Cross-platform: Arch Linux, Debian/Ubuntu, Fedora, Alpine, openSUSE, macOS, Windows (MSYS2)

## Supported systems

| Platform | Package manager | Notes |
|---|---|---|
| Arch Linux | pacman / paru | AUR helper auto-installed in Desktop mode |
| Debian / Ubuntu | apt | |
| Fedora | dnf | |
| Alpine | apk | |
| openSUSE | zypper | |
| macOS | brew | Homebrew auto-installed if missing |
| Windows | MSYS2 | Requires MSYS2 or WSL |

## Installation

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/Pakrohk-DotFiles/zsh_config/refs/heads/main/install.sh | bash
```

With options:

```bash
# Server mode (minimal)
curl -fsSL https://raw.githubusercontent.com/Pakrohk-DotFiles/zsh_config/refs/heads/main/install.sh | bash -s -- --server

# Desktop mode (full features)
curl -fsSL https://raw.githubusercontent.com/Pakrohk-DotFiles/zsh_config/refs/heads/main/install.sh | bash -s -- --desktop

# Non-interactive
curl -fsSL https://raw.githubusercontent.com/Pakrohk-DotFiles/zsh_config/refs/heads/main/install.sh | bash -s -- --non-interactive --skip-deps
```

### Windows (PowerShell)

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/Pakrohk-DotFiles/zsh_config/refs/heads/main/install.ps1'))
```

The PowerShell launcher finds Python and delegates to the same engine. Use WSL for the full experience; native Windows supports `ziro doctor` but `install` requires a Unix environment.

### From a local clone

```bash
git clone https://github.com/Pakrohk-DotFiles/zsh_config.git ~/.ziro
bash ~/.ziro/install.sh
```

## Updating

```bash
zsh_update
```

This pulls the latest changes from GitHub, recompiles plugins, and preserves your local `.zshrc.local` and Starship configuration.

## Checking health

```bash
ziro doctor
```

Reports the status of zsh, git, python3, fzf, starship, znap, plugins, symlink, default shell, remote origin, `.zshrc.local`, and `starship.toml`.

## Python CLI

The installer, updater, and doctor are powered by a Python 3 engine in `ziro/`. All three entry points (`install.sh`, `install.ps1`, `zsh_update`) delegate to it.

```bash
ziro install          # install or repair
ziro install --dry-run
ziro update           # update Ziro
ziro doctor           # check health
ziro --version        # show version
```

Requires Python 3.8 or later. Uses only the standard library (no pip dependencies).

## What the installer does

1. Detects your OS, distro, and package manager
2. Installs system packages (zsh, git, curl, fzf, starship, and optionally rustup, go, node)
3. Clones or pulls the Ziro repository into `~/.ziro`
4. Migrates `~/.zsh_config` to `~/.ziro` if found (legacy support)
5. Backs up existing `.zshrc`, `.zimrc`, `.zpreztorc`, `.zprofile`, `.zshenv` and framework directories
6. Symlinks `~/.zshrc` to `~/.ziro/.zshrc`
7. Creates `.zshrc.local` with sensible defaults (preserves existing)
8. Optionally changes the default shell to Zsh
9. Compiles Zsh files for faster startup
10. Verifies the installation loads without errors

## Security

Server mode disables SSH agent management, installs only essential plugins, and skips GUI-related tools. The installer uses subprocess argument arrays throughout (no shell injection vectors). The only remote execution is the official Homebrew installer on macOS (documented and unavoidable for bootstrap).

## Configuration

### Files in `~/.ziro`

| File | Purpose |
|---|---|
| `.zshrc` | Main entry point. Handles znap bootstrap, options, and sources all other files. Symlinked from `~/.zshrc`. |
| `.prompt.local` | Manages Starship prompt. Auto-installs Starship if missing. Generates default `starship.toml`. |
| `.zsh_aliases` | Curated aliases and functions. |
| `.paru_fzf.zsh` | Interactive package manager (`pf` command). |
| `.zshrc.local` | Your machine-specific settings. Never overwritten by the installer. |
| `.zsh_update.zsh` | Background update checker (runs on shell startup). |
| `ziro/` | Python engine (install/update/doctor). |

### Your own settings

Edit `~/.ziro/.zshrc.local` for machine-specific configuration:

```bash
# Personal aliases
alias work='cd ~/projects/work'

# Environment variables
export EDITOR='nvim'
export BROWSER='firefox'
```

The installer never modifies `.zshrc.local` if it already exists. Your Starship configuration (`~/.config/starship.toml`) is also preserved if you customize it.

### Key aliases and functions

| Command | Description |
|---|---|
| `pf` | Interactive package manager (fzf) |
| `softar` | Remove orphaned packages |
| `extract <file>` | Extract any archive |
| `mkcd <dir>` | Create and enter a directory |
| `cdf` | Fuzzy-find a subdirectory |
| `up <n>` | Go up n directories |
| `cheat <cmd> <term>` | Search man pages |
| `refonts` | Refresh font cache |
| `rebuild_system` | Rebuild initramfs + GRUB (Arch) |
| `reflectmirrors` | Refresh Arch mirrors by speed |
| `zsh_update` | Update Ziro |
| `ziro doctor` | Check installation health |

Global aliases: `G` (grep), `H` (head), `T` (tail), `L` (less).

### Plugins (via znap)

- `fast-syntax-highlighting` - real-time syntax highlighting
- `zsh-autosuggestions` - autosuggest from history
- `zsh-completions` - additional completions
- `z` - directory jumping by frecency
- `wd` - bookmarks (desktop)
- `alias-tips` - hints for available aliases (desktop)

## Upgrading from legacy installs

If you previously installed Ziro at `~/.zsh_config`, the installer migrates it to `~/.ziro` automatically. The runtime checks `~/.ziro` first, then falls back to `~/.zsh_config`. Your `.zshrc.local` and Starship configuration are preserved through migration.

## License

MIT
