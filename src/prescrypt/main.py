"""Prescrypt CLI - Python to JavaScript transpiler."""

from __future__ import annotations

import sys
from pathlib import Path

from .compiler import py2js
from .exceptions import PrescryptError


def main():
    """Main entry point for the py2js command."""
    if len(sys.argv) < 2:
        print("Usage: py2js <input.py> [output.js]", file=sys.stderr)
        sys.exit(1)

    src_path = Path(sys.argv[1])
    if not src_path.exists():
        print(f"Error: File not found: {src_path}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if len(sys.argv) >= 3:
        dst_path = Path(sys.argv[2])
    else:
        dst_path = src_path.with_suffix(".js")

    # Read source
    src = src_path.read_text()

    # Compile with error handling
    try:
        dst = py2js(src).strip()
    except PrescryptError as e:
        # Update error location with filename
        if e.location:
            e.location.file = str(src_path)
        # Print error with source context
        print(e.format_with_context(src), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Internal error: {e}", file=sys.stderr)
        sys.exit(1)

    # Write output
    dst_path.write_text(dst + "\n")
    print(f"Compiled {src_path} -> {dst_path}")


if __name__ == "__main__":
    main()
