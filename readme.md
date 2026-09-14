# Ziro

> Zero setup. Just a better shell.

Ziro is a complete shell environment for developers and power users. It installs Zsh, Starship, syntax highlighting, autosuggestions, completions, and a curated set of aliases and functions. Everything lives in `~/.ziro` and updates with a single command.

## What it installs

- Zsh with fast startup
- [Starship](https://starship.rs/) prompt with theme packages (`ziro theme list`; edit `~/.config/starship.toml` freely)
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
curl -fsSL https://raw.githubusercontent.com/Pakrohk-DotFiles/ziro-shell/refs/heads/main/install.sh | bash
```

With options:

```bash
# Server mode (minimal)
curl -fsSL https://raw.githubusercontent.com/Pakrohk-DotFiles/ziro-shell/refs/heads/main/install.sh | bash -s -- --server

# Desktop mode (full features)
curl -fsSL https://raw.githubusercontent.com/Pakrohk-DotFiles/ziro-shell/refs/heads/main/install.sh | bash -s -- --desktop

# Non-interactive
curl -fsSL https://raw.githubusercontent.com/Pakrohk-DotFiles/ziro-shell/refs/heads/main/install.sh | bash -s -- --non-interactive --skip-deps
```

### Windows (PowerShell)

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/Pakrohk-DotFiles/ziro-shell/refs/heads/main/install.ps1'))
```

The PowerShell launcher finds Python and delegates to the same engine. Use WSL for the full experience; native Windows supports `ziro doctor` but `install` requires a Unix environment.

### From a local clone

```bash
git clone https://github.com/Pakrohk-DotFiles/ziro-shell.git ~/.ziro
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
ziro theme list       # list available theme packages
ziro theme apply lambda  # apply a theme package
ziro --version        # show version
```

Requires Python 3.11 or later (the engine uses `tomllib` and PEP 604 unions). Uses only the standard library (no pip dependencies).

## What the installer does

The installer replaces your zsh config, so it never touches an existing setup
without asking first. It lists every file it would back up (`.zshrc`,
`.zprofile`, `.zshenv`, `.zimrc`, `.zpreztorc`, plus oh-my-zsh / prezto / zim
directories) and aborts unless you confirm. Backups land beside the originals
as `<file>.bak.<timestamp>`. Flags skip the prompt: `--overwrite` (or
`--force`) backs up and continues, `--no-overwrite` aborts. `--non-interactive`
defaults to back up and continue, so pair it with `--no-overwrite` if you would
rather a scripted run fail than move your files.

1. Detects your OS, distro, and package manager
2. Installs system packages (zsh, git, curl, fzf, starship, and optionally rustup, go, node)
3. Clones or pulls the Ziro repository into `~/.ziro`
4. Migrates `~/.zsh_config` to `~/.ziro` if found (legacy support)
5. Confirms, then backs up existing zsh config files and framework directories
6. Symlinks `~/.zshrc` to `~/.ziro/.zshrc`
7. Creates `.zshrc.local` with sensible defaults (preserves existing)
8. Optionally changes the default shell to Zsh
9. Compiles Zsh files for faster startup
10. Installs the `ziro` launcher into `~/.local/bin` and puts that directory on
    PATH via `~/.zshenv`, so a brand-new terminal can run it
11. Verifies the installation: zsh loads without errors, plugins are present,
    and `ziro` resolves in a fresh interactive shell
12. Prints `Installation Completed Successfully!` only when every check passes;
    otherwise it exits non-zero and points you at `ziro doctor`

After a successful install, open a new terminal window or run `exec zsh -l`.
Plain `source ~/.zshrc` does not reload `~/.zshenv` or `chsh`, so the new shell
setup will look half-applied if you use it.

## Security

Server mode disables SSH agent management, installs only essential plugins, and skips GUI-related tools. The installer uses subprocess argument arrays throughout (no shell injection vectors). The only remote execution is the official Homebrew installer on macOS (documented and unavoidable for bootstrap).

## Configuration

### Files in `~/.ziro`

| File | Purpose |
|---|---|
| `.zshrc` | Main entry point. Handles znap bootstrap, options, and sources all other files. Symlinked from `~/.zshrc`. |
| `.prompt.local` | Loads Starship into the shell via znap. Starship itself comes from your package manager. |
| `themes/` | Theme packages. Each is a directory with `theme.toml` (metadata) and `starship.toml` (prompt config). |
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

The installer never modifies `.zshrc.local` if it already exists. The same
ownership rule applies to `~/.config/starship.toml`: once you edit it, ziro
never overwrites it. An untouched managed copy is refreshed on update so
upstream theme fixes reach you.

### Theme packages

Prompt configs live in `themes/<name>/` as self-contained packages:

```
themes/
└── lambda/
    ├── theme.toml      # name + description
    └── starship.toml   # the prompt config
```

- `ziro install` copies the default theme (`themes/lambda/Starship.toml`) to
  `~/.config/starship.toml` on first install; `--theme <name>` picks another.
  `ziro update` refreshes that copy only while it still matches what ziro wrote.
- `ziro theme apply <name>` switches themes. It refuses to overwrite a config that differs from the target theme; add `--force` to overwrite anyway.
- `ziro theme list` shows available packages.

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
