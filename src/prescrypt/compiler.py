from __future__ import annotations

from .codegen import CodeGen
from .front import ast
from .front.passes.binder import Binder
from .front.passes.constant_folder import fold_constants
from .front.passes.desugar import desugar
from .stdlib_js import FUNCTION_PREFIX, METHOD_PREFIX, StdlibJs

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

        Returns:
            JavaScript code
        """
        tree = ast.parse(source)
        tree = desugar(tree)
        if optimize:
            tree = fold_constants(tree)
        Binder().visit(tree)
        codegen = CodeGen(tree, function_prefix, method_prefix, module_mode)
        js_code = codegen.gen()

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

        return preamble + "\n" + js_code

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
    )
