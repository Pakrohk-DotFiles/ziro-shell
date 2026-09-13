# Lambda

Ziro's default Starship prompt theme — minimal, informative, fast.

## Layout

```
user@host ~/project (git_branch git_status) cmd_duration
λ
```

- `user@host` — bold gray
- current directory — bold blue
- git branch — bold yellow (truncated to 8 chars)
- git status — bold purple (untracked★, modified✏️, staged✔, ahead↑, etc.)
- success `λ` — bold green; error — bold red; vi-mode — bold yellow
- language overlays when active: Python, Rust, Go, Node.js

## Theme.toml

Required metadata in `Theme.toml`:

```toml
[theme]
name = "lambda"            # must match directory name
version = "1.0.0"          # semver
description = "..."
author = "Pakrohk"
license = "MIT"
```

## Starship.toml

`Starship.toml` is the Starship prompt configuration that gets copied to
`~/.config/starship.toml` on `ziro install`. User edits survive subsequent
installs and updates — Ziro never overwrites an existing file.

To reset to the default prompt:

```sh
ziro theme apply lambda --force
```

## Usage

```sh
ziro theme list           # show available packages
ziro theme current        # show which theme is active
ziro theme apply lambda   # apply this theme
```
