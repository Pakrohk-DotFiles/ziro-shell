---
title: znap plugin loading — local vs git
tags: [znap, loading, gotcha, concept]
sourceRefs: ["/home/ali/.ziro/.zshrc", "/home/ali/.ziro/integration.zsh"]
lastReviewed: 2026-09-24
---

`znap source <owner>/<repo>` **only clones git repos**. Local `.zsh` files
cannot be loaded this way — they must be `source`d directly.

## The pattern

`.zshrc`:
```zsh
if [[ "$ZSH_AUTOSUGGEST_DISABLE" == "yes" ]]; then
    source "$ZSH_CONFIG_DIR/ghost/ghost.zsh"
else
    znap source zsh-users/zsh-autosuggestions
fi
```

Upstream plugins (git repos) → `znap source`. Local plugins (files) →
`source`.

## Why

`znap` is a git-clone-and-source tool. It has no concept of "load this local
file." This is a tool capability boundary, not a design choice in ziro — but
it intersects with [[concepts/plugin-sovereignty]]: a sovereign local plugin
is loadable by plain `source` anywhere, so ziro loads it that way rather than
wrapping it in a znap abstraction.

## Consequence

[[entities/ghost-plugin]] is `source`d directly. So is anything under
`$ZIRO_HOME` that is a file rather than a repo.

Related: [[entities/znap-runtime]], [[entities/shell-bootstrap]].
