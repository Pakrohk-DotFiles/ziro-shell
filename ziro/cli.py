"""CLI entry: ziro install | update | doctor | --version"""

import argparse
import sys

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ziro",
        description="Ziro - Zero setup. Just a better shell.",
    )
    parser.add_argument("--version", action="version",
                        version=f"ziro {__version__}")
    sub = parser.add_subparsers(dest="command")

    p_install = sub.add_parser("install", help="install or repair Ziro")
    p_install.add_argument("--desktop", action="store_true",
                           help="force Desktop mode (full features)")
    p_install.add_argument("--server", action="store_true",
                           help="force Server mode (minimal)")
    p_install.add_argument("--skip-deps", action="store_true",
                           help="skip dependency installation")
    p_install.add_argument("--skip-shell", action="store_true",
                           help="do not change the default shell")
    p_install.add_argument("--force", action="store_true",
                           help="overwrite generated config (never user files)")
    p_install.add_argument("--dry-run", action="store_true",
                           help="show what would be done without doing it")
    p_install.add_argument("--non-interactive", action="store_true",
                           help="run without prompts (all languages off)")
    p_install.add_argument("--with-python", dest="enable_python", action="store_true",
                           default=None, help="enable Python tooling (skip prompt)")
    p_install.add_argument("--no-python", dest="enable_python", action="store_false",
                           help="disable Python tooling (skip prompt)")
    p_install.add_argument("--with-rust", dest="enable_rust", action="store_true",
                           default=None, help="enable Rust tooling (skip prompt)")
    p_install.add_argument("--no-rust", dest="enable_rust", action="store_false",
                           help="disable Rust tooling (skip prompt)")
    p_install.add_argument("--with-go", dest="enable_go", action="store_true",
                           default=None, help="enable Go tooling (skip prompt)")
    p_install.add_argument("--no-go", dest="enable_go", action="store_false",
                           help="disable Go tooling (skip prompt)")
    p_install.add_argument("--with-node", dest="enable_node", action="store_true",
                           default=None, help="enable Node tooling (skip prompt)")
    p_install.add_argument("--no-node", dest="enable_node", action="store_false",
                           help="disable Node tooling (skip prompt)")

    # Shell features
    p_install.add_argument("--with-zcolors", dest="enable_zcolors", action="store_true",
                           default=None, help="enable zcolors (skip prompt)")
    p_install.add_argument("--no-zcolors", dest="enable_zcolors", action="store_false",
                           help="disable zcolors (skip prompt)")
    p_install.add_argument("--with-wd", dest="enable_wd", action="store_true",
                           default=None, help="enable wd bookmarks (skip prompt)")
    p_install.add_argument("--no-wd", dest="enable_wd", action="store_false",
                           help="disable wd bookmarks (skip prompt)")
    p_install.add_argument("--with-alias-tips", dest="enable_alias_tips", action="store_true",
                           default=None, help="enable alias-tips (skip prompt)")
    p_install.add_argument("--no-alias-tips", dest="enable_alias_tips", action="store_false",
                           help="disable alias-tips (skip prompt)")
    p_install.add_argument("--with-z", dest="enable_z", action="store_true",
                           default=None, help="enable z directory jumping (skip prompt)")
    p_install.add_argument("--no-z", dest="enable_z", action="store_false",
                           help="disable z directory jumping (skip prompt)")
    p_install.add_argument("--with-pf", dest="enable_pf", action="store_true",
                           default=None, help="enable pf package manager (skip prompt)")
    p_install.add_argument("--no-pf", dest="enable_pf", action="store_false",
                           help="disable pf package manager (skip prompt)")
    p_install.add_argument("--with-ssh-agent", dest="enable_ssh_agent", action="store_true",
                           default=None, help="enable SSH agent (skip prompt)")
    p_install.add_argument("--no-ssh-agent", dest="enable_ssh_agent", action="store_false",
                           help="disable SSH agent (skip prompt)")
    p_install.add_argument("--with-update-check", dest="enable_update_check", action="store_true",
                           default=None, help="enable background update check (skip prompt)")
    p_install.add_argument("--no-update-check", dest="enable_update_check", action="store_false",
                           help="disable background update check (skip prompt)")
    p_install.add_argument("--with-nmap", dest="enable_nmap", action="store_true",
                           default=None, help="enable nmap completions (skip prompt)")
    p_install.add_argument("--no-nmap", dest="enable_nmap", action="store_false",
                           help="disable nmap completions (skip prompt)")

    sub.add_parser("update", help="update Ziro to the latest version")
    sub.add_parser("doctor", help="check installation health")
    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        argv = ["install"]
    args = build_parser().parse_args(argv)

    if args.command == "install":
        from .installer import Options, install
        if args.desktop and args.server:
            print("error: --desktop and --server are mutually exclusive", file=sys.stderr)
            return 2
        opts = Options(
            mode="Desktop" if args.desktop else "Server" if args.server else None,
            skip_deps=args.skip_deps,
            skip_shell=args.skip_shell,
            force=args.force,
            dry_run=args.dry_run,
            non_interactive=args.non_interactive,
            enable_python=args.enable_python,
            enable_rust=args.enable_rust,
            enable_go=args.enable_go,
            enable_node=args.enable_node,
            enable_zcolors=args.enable_zcolors,
            enable_wd=args.enable_wd,
            enable_alias_tips=args.enable_alias_tips,
            enable_z=args.enable_z,
            enable_pf=args.enable_pf,
            enable_ssh_agent=args.enable_ssh_agent,
            enable_update_check=args.enable_update_check,
            enable_nmap=args.enable_nmap,
        )
        return install(opts)

    if args.command == "update":
        from .updater import update
        return update()

    if args.command == "doctor":
        from .doctor import doctor
        return doctor()

    return 2


if __name__ == "__main__":
    sys.exit(main())
