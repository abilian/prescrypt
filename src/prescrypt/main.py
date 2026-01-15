"""Prescrypt CLI - Python to JavaScript transpiler."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .compiler import py2js
from .exceptions import PrescryptError
from .sourcemap import SourceMapGenerator, get_sourcemap_comment


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="py2js",
        description="Compile Python to JavaScript",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  py2js input.py                    Compile input.py to input.js
  py2js input.py -o output.js       Compile to specific output file
  py2js src/ -o dist/               Compile all .py files in src/ to dist/
  py2js src/ -o dist/ --module-mode Compile as ES6 modules with exports
  py2js input.py --module-path lib/ Add lib/ to module search path
        """,
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input Python file or directory",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output file or directory (default: same as input with .js extension)",
    )

    parser.add_argument(
        "-m",
        "--module-mode",
        action="store_true",
        default=False,
        help="Enable ES6 module mode (emit exports and ES6 imports)",
    )

    parser.add_argument(
        "-M",
        "--module-path",
        type=Path,
        action="append",
        default=[],
        dest="module_paths",
        help="Additional directory to search for modules (can be specified multiple times)",
    )

    parser.add_argument(
        "--no-stdlib",
        action="store_true",
        default=False,
        help="Don't include the standard library preamble",
    )

    parser.add_argument(
        "--no-tree-shake",
        action="store_true",
        default=False,
        help="Include full stdlib instead of only used functions",
    )

    parser.add_argument(
        "--no-optimize",
        action="store_true",
        default=False,
        help="Disable compile-time optimizations (constant folding, etc.)",
    )

    parser.add_argument(
        "-s",
        "--source-maps",
        action="store_true",
        default=False,
        help="Generate source map files (.js.map) for debugging",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Print verbose output",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress all output except errors",
    )

    return parser


def compile_file(
    src_path: Path,
    dst_path: Path,
    *,
    module_mode: bool = False,
    module_paths: list[Path] | None = None,
    include_stdlib: bool = True,
    tree_shake: bool = True,
    optimize: bool = True,
    source_maps: bool = False,
    verbose: bool = False,
    quiet: bool = False,
) -> bool:
    """Compile a single Python file to JavaScript.

    Returns True on success, False on error.
    """
    # Read source
    try:
        src = src_path.read_text()
    except OSError as e:
        print(f"Error reading {src_path}: {e}", file=sys.stderr)
        return False

    # Create source map generator if enabled
    source_map = None
    if source_maps:
        source_map = SourceMapGenerator(file=dst_path.name)
        # Add the source file (use relative path from output dir)
        try:
            rel_src = src_path.relative_to(dst_path.parent)
        except ValueError:
            # Source not under output dir, use absolute path
            rel_src = src_path
        source_map.add_source(str(rel_src), src)

    # Compile
    try:
        dst = py2js(
            src,
            include_stdlib=include_stdlib,
            tree_shake=tree_shake,
            optimize=optimize,
            module_mode=module_mode,
            source_dir=src_path.parent,
            module_paths=module_paths,
            source_map=source_map,
        ).strip()
    except PrescryptError as e:
        # Update error location with filename
        if e.location:
            e.location.file = str(src_path)
        # Print error with source context
        print(e.format_with_context(src), file=sys.stderr)
        return False
    except Exception as e:
        print(f"Internal error compiling {src_path}: {e}", file=sys.stderr)
        return False

    # Ensure output directory exists
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    # Append source map comment if enabled
    if source_maps and source_map is not None:
        map_filename = dst_path.name + ".map"
        dst = dst + "\n" + get_sourcemap_comment(map_filename)

    # Write output
    try:
        dst_path.write_text(dst + "\n")
    except OSError as e:
        print(f"Error writing {dst_path}: {e}", file=sys.stderr)
        return False

    # Write source map
    if source_maps and source_map is not None:
        map_path = dst_path.with_suffix(".js.map")
        try:
            source_map.write(map_path)
        except OSError as e:
            print(f"Error writing {map_path}: {e}", file=sys.stderr)
            return False

    if verbose:
        if source_maps:
            print(f"Compiled {src_path} -> {dst_path} + {dst_path.name}.map")
        else:
            print(f"Compiled {src_path} -> {dst_path}")
    elif not quiet:
        print(f"{src_path} -> {dst_path}")

    return True


def compile_directory(
    src_dir: Path,
    dst_dir: Path,
    *,
    module_mode: bool = False,
    module_paths: list[Path] | None = None,
    include_stdlib: bool = True,
    tree_shake: bool = True,
    optimize: bool = True,
    source_maps: bool = False,
    verbose: bool = False,
    quiet: bool = False,
) -> tuple[int, int]:
    """Compile all Python files in a directory.

    Returns (success_count, error_count).
    """
    success_count = 0
    error_count = 0

    # Find all .py files (excluding __pycache__ and hidden directories)
    py_files = []
    for py_file in src_dir.rglob("*.py"):
        # Skip __pycache__ and hidden directories
        if "__pycache__" in py_file.parts:
            continue
        if any(part.startswith(".") for part in py_file.parts):
            continue
        py_files.append(py_file)

    if not py_files:
        if not quiet:
            print(f"No Python files found in {src_dir}", file=sys.stderr)
        return 0, 0

    if verbose:
        print(f"Found {len(py_files)} Python file(s) in {src_dir}")

    for py_file in sorted(py_files):
        # Calculate relative path and output path
        rel_path = py_file.relative_to(src_dir)

        # Handle __init__.py -> index.js conversion
        if rel_path.name == "__init__.py":
            js_rel_path = rel_path.parent / "index.js"
        else:
            js_rel_path = rel_path.with_suffix(".js")

        dst_path = dst_dir / js_rel_path

        success = compile_file(
            py_file,
            dst_path,
            module_mode=module_mode,
            module_paths=module_paths,
            include_stdlib=include_stdlib,
            tree_shake=tree_shake,
            optimize=optimize,
            source_maps=source_maps,
            verbose=verbose,
            quiet=quiet,
        )

        if success:
            success_count += 1
        else:
            error_count += 1

    return success_count, error_count


def main():
    """Main entry point for the py2js command."""
    parser = create_parser()
    args = parser.parse_args()

    input_path: Path = args.input
    output_path: Path | None = args.output

    # Check input exists
    if not input_path.exists():
        print(f"Error: Path not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Compile settings
    module_mode = args.module_mode
    module_paths = args.module_paths
    include_stdlib = not args.no_stdlib
    tree_shake = not args.no_tree_shake
    optimize = not args.no_optimize
    source_maps = args.source_maps
    verbose = args.verbose
    quiet = args.quiet

    if input_path.is_file():
        # Single file compilation
        if output_path is None:
            output_path = input_path.with_suffix(".js")
        elif output_path.is_dir() or str(output_path).endswith("/"):
            # Output is a directory
            output_path = output_path / input_path.with_suffix(".js").name

        success = compile_file(
            input_path,
            output_path,
            module_mode=module_mode,
            module_paths=module_paths,
            include_stdlib=include_stdlib,
            tree_shake=tree_shake,
            optimize=optimize,
            source_maps=source_maps,
            verbose=verbose,
            quiet=quiet,
        )
        sys.exit(0 if success else 1)

    elif input_path.is_dir():
        # Directory compilation
        if output_path is None:
            print(
                "Error: Output directory (-o) is required when compiling a directory",
                file=sys.stderr,
            )
            sys.exit(1)

        # Enable module mode by default for directory compilation
        if not module_mode and not quiet:
            print("Note: Enabling module mode for directory compilation")
            module_mode = True

        success_count, error_count = compile_directory(
            input_path,
            output_path,
            module_mode=module_mode,
            module_paths=module_paths,
            include_stdlib=include_stdlib,
            tree_shake=tree_shake,
            optimize=optimize,
            source_maps=source_maps,
            verbose=verbose,
            quiet=quiet,
        )

        if not quiet:
            print(f"\nCompiled {success_count} file(s), {error_count} error(s)")

        sys.exit(0 if error_count == 0 else 1)

    else:
        print(f"Error: {input_path} is not a file or directory", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
