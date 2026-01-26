"""Prescrypt CLI - Python to JavaScript transpiler."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .bundler import bundle_files
from .compiler import py2js
from .exceptions import PrescryptError
from .sourcemap import SourceMapGenerator, get_sourcemap_comment

# Optional watchdog support for efficient file watching
try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


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
  py2js src/ -o dist/ --watch       Watch for changes and recompile
  py2js input.py -v                 Show compilation stages with timing
  py2js input.py -vv                Also show AST after each pass
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
        "-b",
        "--bundle",
        action="store_true",
        default=False,
        help="Bundle imported modules into a single output file with combined tree-shaking",
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
        "-w",
        "--watch",
        action="store_true",
        default=False,
        help="Watch for changes and recompile automatically",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for stages, -vv for AST, -vvv for full debug)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable full debug output (equivalent to -vvv)",
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
    verbosity: int = 0,
    quiet: bool = False,
) -> bool:
    """Compile a single Python file to JavaScript.

    Args:
        src_path: Path to the Python source file
        dst_path: Path to the output JavaScript file
        module_mode: Whether to emit ES6 module exports
        module_paths: Additional directories to search for modules
        include_stdlib: Whether to include the stdlib preamble
        tree_shake: Whether to only include used stdlib functions
        optimize: Whether to apply compile-time optimizations
        source_maps: Whether to generate source maps
        verbosity: Verbosity level (0=normal, 1=stages, 2=AST, 3=debug)
        quiet: Suppress all output except errors

    Returns:
        True on success, False on error.
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
            verbosity=verbosity,
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

    if verbosity >= 1:
        if source_maps:
            print(f"Compiled {src_path} -> {dst_path} + {dst_path.name}.map")
        else:
            print(f"Compiled {src_path} -> {dst_path}")
    elif not quiet:
        print(f"{src_path} -> {dst_path}")

    return True


def bundle_file(
    src_path: Path,
    dst_path: Path,
    *,
    module_paths: list[Path] | None = None,
    optimize: bool = True,
    verbosity: int = 0,
    quiet: bool = False,
) -> bool:
    """Bundle a Python file and all its imports into a single JavaScript file.

    Args:
        src_path: Path to the entry Python source file
        dst_path: Path to the output JavaScript file
        module_paths: Additional directories to search for modules
        optimize: Whether to apply compile-time optimizations
        verbosity: Verbosity level (0=normal, 1=stages, 2=AST, 3=debug)
        quiet: Suppress all output except errors

    Returns:
        True on success, False on error.
    """
    try:
        dst = bundle_files(
            entry_file=src_path,
            module_paths=module_paths,
            optimize=optimize,
            verbosity=verbosity,
        ).strip()
    except PrescryptError as e:
        print(e.format_with_context(""), file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error bundling {src_path}: {e}", file=sys.stderr)
        if verbosity >= 2:
            import traceback

            traceback.print_exc()
        return False

    # Ensure output directory exists
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output
    try:
        dst_path.write_text(dst + "\n")
    except OSError as e:
        print(f"Error writing {dst_path}: {e}", file=sys.stderr)
        return False

    if not quiet:
        print(f"Bundled {src_path} -> {dst_path}")

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
    verbosity: int = 0,
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

    if verbosity >= 1:
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
            verbosity=verbosity,
            quiet=quiet,
        )

        if success:
            success_count += 1
        else:
            error_count += 1

    return success_count, error_count


def _get_output_path_for_file(
    src_path: Path, src_dir: Path | None, dst_dir: Path | None
) -> Path:
    """Calculate output path for a source file."""
    if src_dir is None or dst_dir is None:
        # Single file mode
        return src_path.with_suffix(".js")

    # Directory mode
    rel_path = src_path.relative_to(src_dir)
    if rel_path.name == "__init__.py":
        js_rel_path = rel_path.parent / "index.js"
    else:
        js_rel_path = rel_path.with_suffix(".js")
    return dst_dir / js_rel_path


def _should_watch_file(path: Path) -> bool:
    """Check if a file should be watched."""
    if path.suffix != ".py":
        return False
    if "__pycache__" in path.parts:
        return False
    return not any(part.startswith(".") for part in path.parts)


def watch_with_polling(
    src_path: Path,
    dst_path: Path | None,
    *,
    is_directory: bool,
    module_mode: bool = False,
    module_paths: list[Path] | None = None,
    include_stdlib: bool = True,
    tree_shake: bool = True,
    optimize: bool = True,
    source_maps: bool = False,
    verbosity: int = 0,
    quiet: bool = False,
    poll_interval: float = 1.0,
) -> None:
    """Watch for file changes using polling (no external dependencies)."""
    # Track file modification times
    mtimes: dict[Path, float] = {}

    def get_py_files() -> list[Path]:
        if is_directory:
            return [f for f in src_path.rglob("*.py") if _should_watch_file(f)]
        else:
            return [src_path]

    def compile_changed():
        changed = False
        for py_file in get_py_files():
            try:
                mtime = py_file.stat().st_mtime
            except OSError:
                continue

            if py_file not in mtimes or mtime > mtimes[py_file]:
                mtimes[py_file] = mtime
                if py_file in mtimes:  # Only recompile if not first scan
                    changed = True
                    out_path = _get_output_path_for_file(
                        py_file,
                        src_path if is_directory else None,
                        dst_path if is_directory else None,
                    )
                    if not is_directory and dst_path:
                        out_path = dst_path

                    compile_file(
                        py_file,
                        out_path,
                        module_mode=module_mode,
                        module_paths=module_paths,
                        include_stdlib=include_stdlib,
                        tree_shake=tree_shake,
                        optimize=optimize,
                        source_maps=source_maps,
                        verbosity=verbosity,
                        quiet=quiet,
                    )
        return changed

    # Initial scan to populate mtimes
    for py_file in get_py_files():
        try:
            mtimes[py_file] = py_file.stat().st_mtime
        except OSError:
            pass

    if not quiet:
        print(f"Watching {src_path} for changes... (Ctrl+C to stop)")

    try:
        while True:
            compile_changed()
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        if not quiet:
            print("\nStopped watching.")


def watch_with_watchdog(
    src_path: Path,
    dst_path: Path | None,
    *,
    is_directory: bool,
    module_mode: bool = False,
    module_paths: list[Path] | None = None,
    include_stdlib: bool = True,
    tree_shake: bool = True,
    optimize: bool = True,
    source_maps: bool = False,
    verbosity: int = 0,
    quiet: bool = False,
) -> None:
    """Watch for file changes using watchdog (efficient, requires watchdog package)."""
    if not WATCHDOG_AVAILABLE:
        msg = "watchdog package not available"
        raise RuntimeError(msg)

    class RecompileHandler(FileSystemEventHandler):
        def __init__(self):
            self._last_compile: dict[Path, float] = {}
            self._debounce_delay = 0.1  # 100ms debounce

        def on_modified(self, event):
            if event.is_directory:
                return
            self._handle_change(Path(event.src_path))

        def on_created(self, event):
            if event.is_directory:
                return
            self._handle_change(Path(event.src_path))

        def _handle_change(self, path: Path):
            if not _should_watch_file(path):
                return

            # Debounce: skip if we compiled this file very recently
            now = time.time()
            if path in self._last_compile:
                if now - self._last_compile[path] < self._debounce_delay:
                    return
            self._last_compile[path] = now

            out_path = _get_output_path_for_file(
                path,
                src_path if is_directory else None,
                dst_path if is_directory else None,
            )
            if not is_directory and dst_path:
                out_path = dst_path

            compile_file(
                path,
                out_path,
                module_mode=module_mode,
                module_paths=module_paths,
                include_stdlib=include_stdlib,
                tree_shake=tree_shake,
                optimize=optimize,
                source_maps=source_maps,
                verbosity=verbosity,
                quiet=quiet,
            )

    handler = RecompileHandler()
    observer = Observer()
    observer.schedule(handler, str(src_path), recursive=is_directory)
    observer.start()

    if not quiet:
        print(f"Watching {src_path} for changes... (Ctrl+C to stop)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if not quiet:
            print("\nStopped watching.")

    observer.join()


def watch_files(
    src_path: Path,
    dst_path: Path | None,
    *,
    is_directory: bool,
    module_mode: bool = False,
    module_paths: list[Path] | None = None,
    include_stdlib: bool = True,
    tree_shake: bool = True,
    optimize: bool = True,
    source_maps: bool = False,
    verbosity: int = 0,
    quiet: bool = False,
) -> None:
    """Watch for file changes and recompile.

    Uses watchdog if available, otherwise falls back to polling.
    """
    if WATCHDOG_AVAILABLE:
        if verbosity >= 1:
            print("Using watchdog for file watching")
        watch_with_watchdog(
            src_path,
            dst_path,
            is_directory=is_directory,
            module_mode=module_mode,
            module_paths=module_paths,
            include_stdlib=include_stdlib,
            tree_shake=tree_shake,
            optimize=optimize,
            source_maps=source_maps,
            verbosity=verbosity,
            quiet=quiet,
        )
    else:
        if verbosity >= 1:
            print("Using polling for file watching (install watchdog for efficiency)")
        watch_with_polling(
            src_path,
            dst_path,
            is_directory=is_directory,
            module_mode=module_mode,
            module_paths=module_paths,
            include_stdlib=include_stdlib,
            tree_shake=tree_shake,
            optimize=optimize,
            source_maps=source_maps,
            verbosity=verbosity,
            quiet=quiet,
        )


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
    watch = args.watch
    quiet = args.quiet
    bundle = args.bundle

    # Determine verbosity level
    # --debug is equivalent to -vvv (level 3)
    verbosity = args.verbose or 0
    if args.debug:
        verbosity = 3

    if input_path.is_file():
        # Single file compilation
        if output_path is None:
            output_path = input_path.with_suffix(".js")
        elif output_path.is_dir() or str(output_path).endswith("/"):
            # Output is a directory
            output_path = output_path / input_path.with_suffix(".js").name

        # Initial compilation
        if bundle:
            # Bundle mode - compile entry file with all imports
            if watch:
                print(
                    "Error: Watch mode is not supported with --bundle",
                    file=sys.stderr,
                )
                sys.exit(1)
            if source_maps:
                print(
                    "Warning: Source maps not yet supported with --bundle",
                    file=sys.stderr,
                )
            success = bundle_file(
                input_path,
                output_path,
                module_paths=module_paths,
                optimize=optimize,
                verbosity=verbosity,
                quiet=quiet,
            )
            sys.exit(0 if success else 1)

        # Normal single-file compilation
        success = compile_file(
            input_path,
            output_path,
            module_mode=module_mode,
            module_paths=module_paths,
            include_stdlib=include_stdlib,
            tree_shake=tree_shake,
            optimize=optimize,
            source_maps=source_maps,
            verbosity=verbosity,
            quiet=quiet,
        )

        if watch:
            # Watch mode for single file
            watch_files(
                input_path,
                output_path,
                is_directory=False,
                module_mode=module_mode,
                module_paths=module_paths,
                include_stdlib=include_stdlib,
                tree_shake=tree_shake,
                optimize=optimize,
                source_maps=source_maps,
                verbosity=verbosity,
                quiet=quiet,
            )
        else:
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

        # Initial compilation
        success_count, error_count = compile_directory(
            input_path,
            output_path,
            module_mode=module_mode,
            module_paths=module_paths,
            include_stdlib=include_stdlib,
            tree_shake=tree_shake,
            optimize=optimize,
            source_maps=source_maps,
            verbosity=verbosity,
            quiet=quiet,
        )

        if not quiet:
            print(f"\nCompiled {success_count} file(s), {error_count} error(s)")

        if watch:
            # Watch mode for directory
            watch_files(
                input_path,
                output_path,
                is_directory=True,
                module_mode=module_mode,
                module_paths=module_paths,
                include_stdlib=include_stdlib,
                tree_shake=tree_shake,
                optimize=optimize,
                source_maps=source_maps,
                verbosity=verbosity,
                quiet=quiet,
            )
        else:
            sys.exit(0 if error_count == 0 else 1)

    else:
        print(f"Error: {input_path} is not a file or directory", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
