from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

from .codegen import CodeGen
from .front import ast
from .front.passes.binder import Binder
from .front.passes.constant_folder import fold_constants
from .front.passes.desugar import desugar
from .front.passes.type_inference import TypeInference
from .stdlib_js import FUNCTION_PREFIX, METHOD_PREFIX, StdlibJs

if TYPE_CHECKING:
    from .sourcemap import SourceMapGenerator


def _format_time(seconds: float) -> str:
    """Format time in human-readable units."""
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.0f}µs"
    elif seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    else:
        return f"{seconds:.2f}s"


# Cache stdlib instances by prefix combination
_stdlib_cache: dict[tuple[str, str], StdlibJs] = {}


def get_stdlib_js(
    function_prefix: str = FUNCTION_PREFIX,
    method_prefix: str = METHOD_PREFIX,
) -> StdlibJs:
    """Get a StdlibJs instance for the given prefixes (cached)."""
    key = (function_prefix, method_prefix)
    if key not in _stdlib_cache:
        _stdlib_cache[key] = StdlibJs(function_prefix, method_prefix)
    return _stdlib_cache[key]


class Compiler:
    def compile(
        self,
        source: str,
        include_stdlib: bool = True,
        tree_shake: bool = True,
        optimize: bool = True,
        function_prefix: str = FUNCTION_PREFIX,
        method_prefix: str = METHOD_PREFIX,
        module_mode: bool = False,
        source_dir: Path | None = None,
        module_paths: list[Path] | None = None,
        source_map: SourceMapGenerator | None = None,
        verbosity: int = 0,
    ) -> str:
        """Compile Python source to JavaScript.

        Args:
            source: Python source code
            include_stdlib: Whether to include the stdlib preamble
            tree_shake: Whether to only include used stdlib functions (default True)
            optimize: Whether to apply compile-time optimizations like constant folding (default True)
            function_prefix: Prefix for stdlib functions (default "_pyfunc_")
            method_prefix: Prefix for stdlib methods (default "_pymeth_")
            module_mode: Whether to emit ES6 module exports (default False)
            source_dir: Directory of the source file (for module resolution)
            module_paths: Additional directories to search for modules
            source_map: Optional SourceMapGenerator to populate with mappings
            verbosity: Verbosity level (0=quiet, 1=stages, 2=AST, 3=debug)

        Returns:
            JavaScript code
        """
        total_start = time.perf_counter()
        timings: list[tuple[str, float]] = []

        def stage(name: str):
            """Record timing for a compilation stage."""
            if verbosity >= 1:
                timings.append((name, time.perf_counter()))

        # Stage 1: Parse
        stage("parse")
        tree = ast.parse(source)

        if verbosity >= 2:
            print("=== After parse ===", file=sys.stderr)
            print(ast.dump(tree, indent=2)[:2000], file=sys.stderr)

        # Stage 2: Desugar
        stage("desugar")
        tree = desugar(tree)

        if verbosity >= 2:
            print("=== After desugar ===", file=sys.stderr)
            print(ast.dump(tree, indent=2)[:2000], file=sys.stderr)

        # Stage 3: Optimize
        if optimize:
            stage("optimize")
            tree = fold_constants(tree)

            if verbosity >= 2:
                print("=== After optimize ===", file=sys.stderr)
                print(ast.dump(tree, indent=2)[:2000], file=sys.stderr)

        # Stage 4: Bind
        stage("bind")
        Binder().visit(tree)

        # Stage 5: Type inference
        stage("infer")
        TypeInference().visit(tree)

        # Stage 6: Code generation
        stage("codegen")
        codegen = CodeGen(
            tree,
            function_prefix,
            method_prefix,
            module_mode,
            source_dir,
            module_paths,
            source_map,
        )
        js_code = codegen.gen()
        stage("done")

        # Print timing summary
        if verbosity >= 1 and len(timings) > 1:
            print("Compilation stages:", file=sys.stderr)
            for i in range(len(timings) - 1):
                name, start = timings[i]
                _, end = timings[i + 1]
                duration = end - start
                print(f"  {name:12} {_format_time(duration)}", file=sys.stderr)
            total_time = time.perf_counter() - total_start
            print(f"  {'total':12} {_format_time(total_time)}", file=sys.stderr)

        if not include_stdlib:
            return js_code

        if tree_shake:
            # Generate only the used stdlib functions
            preamble = self.get_partial_preamble(
                codegen.used_std_functions,
                codegen.used_std_methods,
                function_prefix,
                method_prefix,
            )
        else:
            # Include the full stdlib
            preamble = self.get_full_preamble(function_prefix, method_prefix)

        # If source map is being generated, account for preamble lines
        if source_map is not None:
            preamble_lines = preamble.count("\n") + 1
            self._offset_source_map(source_map, preamble_lines)

        return preamble + "\n" + js_code

    def _offset_source_map(self, source_map: SourceMapGenerator, offset: int) -> None:
        """Offset all source map mappings by the given number of lines.

        This is needed when a preamble is prepended to the generated code.
        """
        for mapping in source_map.mappings:
            mapping.gen_line += offset

    def get_full_preamble(
        self,
        function_prefix: str = FUNCTION_PREFIX,
        method_prefix: str = METHOD_PREFIX,
    ) -> str:
        """Get the full stdlib preamble (all functions)."""
        stdlib = get_stdlib_js(function_prefix, method_prefix)
        return stdlib.get_full_std_lib()

    def get_partial_preamble(
        self,
        used_functions: set[str],
        used_methods: set[str],
        function_prefix: str = FUNCTION_PREFIX,
        method_prefix: str = METHOD_PREFIX,
    ) -> str:
        """Get a partial stdlib preamble with only the used functions and their dependencies."""
        stdlib = get_stdlib_js(function_prefix, method_prefix)

        # Resolve all dependencies
        all_funcs, all_methods = stdlib.resolve_dependencies(
            used_functions, used_methods
        )

        # Generate the partial stdlib
        return stdlib.get_partial_std_lib(all_funcs, all_methods)


def py2js(
    code: str,
    include_stdlib: bool = True,
    tree_shake: bool = True,
    optimize: bool = True,
    function_prefix: str = FUNCTION_PREFIX,
    method_prefix: str = METHOD_PREFIX,
    module_mode: bool = False,
    source_dir: Path | None = None,
    module_paths: list[Path] | None = None,
    source_map: SourceMapGenerator | None = None,
    verbosity: int = 0,
) -> str:
    """Compile Python code to JavaScript.

    Args:
        code: Python source code
        include_stdlib: Whether to include the stdlib preamble
        tree_shake: Whether to only include used stdlib functions
        optimize: Whether to apply compile-time optimizations
        function_prefix: Prefix for stdlib functions (default "_pyfunc_")
        method_prefix: Prefix for stdlib methods (default "_pymeth_")
        module_mode: Whether to emit ES6 module exports (default False)
        source_dir: Directory of the source file (for module resolution)
        module_paths: Additional directories to search for modules
        source_map: Optional SourceMapGenerator to populate with mappings
        verbosity: Verbosity level (0=quiet, 1=stages, 2=AST, 3=debug)

    Returns:
        JavaScript code
    """
    compiler = Compiler()
    return compiler.compile(
        code,
        include_stdlib=include_stdlib,
        tree_shake=tree_shake,
        optimize=optimize,
        function_prefix=function_prefix,
        method_prefix=method_prefix,
        module_mode=module_mode,
        source_dir=source_dir,
        module_paths=module_paths,
        source_map=source_map,
        verbosity=verbosity,
    )
