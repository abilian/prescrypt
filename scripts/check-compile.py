#!/usr/bin/env python3
"""Check if Python modules compile with py2js.

Usage:
    scripts/check-compile.py module1.py module2.py ...
    scripts/check-compile.py -v module1.py module2.py ...
    scripts/check-compile.py src/**/*.py
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from prescrypt import py2js

# Ad-hoc
DENY_LIST = {"range_minimum_query.py", "skip_list.py", "union_rectangles.py"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check if Python modules compile with py2js"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show error messages"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Show what's happening"
    )
    parser.add_argument("modules", nargs="+", type=Path, help="Python files to check")
    args = parser.parse_args()

    failed_modules: list[tuple[Path, str]] = []
    total = 0

    for path in args.modules:
        if not path.exists():
            print(f"{path}: file not found", file=sys.stderr)
            continue
        if path.suffix != ".py":
            continue
        if path.name in DENY_LIST:
            continue

        if args.debug:
            t0 = time.time()
            print(f"compiling {path}...", end="", flush=True)

        total += 1
        try:
            source = path.read_text()
            py2js(source, include_stdlib=False)
        except Exception as e:
            msg = str(e).split("\n")[0]
            failed_modules.append((path, msg))

        if args.debug:
            t1 = time.time()
            lines_per_sec = len(source.split("\n")) / (t1 - t0)
            print(f" ({t1 - t0:.2f}s, {lines_per_sec:.0f} lines/s)", flush=True)

    for path, msg in failed_modules:
        if args.verbose:
            print(f"{path}: {msg}")
        else:
            print(path)

    if failed_modules:
        sys.stdout.flush()
        print(
            f"\n{len(failed_modules)}/{total} modules failed to compile",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
