from __future__ import annotations

from pathlib import Path

from .codegen import CodeGen
from .front import ast
from .front.passes.binder import Binder
from .front.passes.desugar import desugar
from .stdlib_js import StdlibJs

# Singleton stdlib instance
_stdlib_js: StdlibJs | None = None


def get_stdlib_js() -> StdlibJs:
    """Get the singleton StdlibJs instance."""
    global _stdlib_js
    if _stdlib_js is None:
        _stdlib_js = StdlibJs()
    return _stdlib_js


class Compiler:
    def compile(
        self,
        source: str,
        include_stdlib: bool = True,
        tree_shake: bool = True,
    ) -> str:
        """Compile Python source to JavaScript.

        Args:
            source: Python source code
            include_stdlib: Whether to include the stdlib preamble
            tree_shake: Whether to only include used stdlib functions (default True)

        Returns:
            JavaScript code
        """
        tree = ast.parse(source)
        tree = desugar(tree)
        Binder().visit(tree)
        codegen = CodeGen(tree)
        js_code = codegen.gen()

        if not include_stdlib:
            return js_code

        if tree_shake:
            # Generate only the used stdlib functions
            preamble = self.get_partial_preamble(
                codegen.used_std_functions,
                codegen.used_std_methods,
            )
        else:
            # Include the full stdlib
            preamble = self.get_full_preamble()

        return preamble + "\n" + js_code

    def get_full_preamble(self) -> str:
        """Get the full stdlib preamble (all functions)."""
        stdlib_js = Path(__file__).parent / "stdlibjs"
        return (stdlib_js / "_stdlib.js").read_text()

    def get_partial_preamble(
        self, used_functions: set[str], used_methods: set[str]
    ) -> str:
        """Get a partial stdlib preamble with only the used functions and their dependencies."""
        stdlib = get_stdlib_js()

        # Resolve all dependencies
        all_funcs, all_methods = stdlib.resolve_dependencies(
            used_functions, used_methods
        )

        # Generate the partial stdlib
        return stdlib.get_partial_std_lib(all_funcs, all_methods)


def py2js(code: str, include_stdlib: bool = True, tree_shake: bool = True) -> str:
    """Compile Python code to JavaScript.

    Args:
        code: Python source code
        include_stdlib: Whether to include the stdlib preamble
        tree_shake: Whether to only include used stdlib functions

    Returns:
        JavaScript code
    """
    compiler = Compiler()
    return compiler.compile(code, include_stdlib=include_stdlib, tree_shake=tree_shake)
