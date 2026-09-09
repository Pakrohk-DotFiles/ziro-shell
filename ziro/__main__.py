"""Allow `python3 -m ziro`."""

import sys

if __package__ in (None, ""):
    # Executed as a file path (python3 ziro/__main__.py): fix up package context
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from ziro.cli import main
else:
    from .cli import main

if __name__ == "__main__":
    sys.exit(main())
