"""Backwards-compatible entry point.

`python generate.py` still works, but the CLI has more to offer:

    uv run interdot            # same as `generate`
    uv run interdot --help     # check, list, preview, switch, link, ...
"""

import sys

from interdotensional.cli import main

if __name__ == "__main__":
    sys.exit(main(["generate", *sys.argv[1:]]))
