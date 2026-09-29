# Installing Ziro-Shell

## Requirements

- **Zsh** >= 5.8
- **Python** >= 3.11 (for cold-path analyzer)
- **git** (for znap clone)
- **OS**: Linux, macOS, WSL, or Termux

## Quick install

```bash
git clone https://github.com/Pakrohk-DotFiles/ziro-shell.git ~/.ziro
cd ~/.ziro
python3 -m core install
```

Then add to `~/.zshrc`:

```zsh
source ~/.ziro/integration.zsh
```

## Interactive install

`ziro install` asks one question:

```
[1] Default — install with pre-configured defaults
[2] Custom — choose each component manually
```

Press Enter for Default. Use `--default` for CI (no prompts).

## Adding plugins

```bash
ziro plugin add zsh-users/zsh-autosuggestions
ziro plugin add zsh-users/zsh-completions @compdef
```

## Verifying

```bash
ziro doctor   # health check
ziro bench    # hot-path measurement
```

## Uninstalling

```bash
rm -rf ~/.ziro ~/.config/ziro ~/.cache/ziro
```

Remove the `source ~/.ziro/integration.zsh` line from `~/.zshrc`.
