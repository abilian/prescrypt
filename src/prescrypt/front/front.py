from __future__ import annotations

from . import ast
from .passes.binder import Binder
from .passes.desugar import desugar


def to_ast(code: str) -> ast.Module:
    """Parse the given code and return the fully decorated AST."""
    tree = ast.parse(code)
    tree = desugar(tree)
    binder = Binder()
    binder.visit(tree)

    # -------------------------------------------------------------------------
    # FUTURE: Type Inference Pass
    # -------------------------------------------------------------------------
    # A type inference pass would enable significant optimizations:
    #
    # 1. Equality comparisons: Use `===` instead of `op_equals()` when both
    #    operands are known to be primitives (number, string, boolean)
    #
    # 2. Arithmetic: Skip `op_add()`/`op_mul()` runtime dispatch when operands
    #    are known numbers (use direct `+`/`*` operators)
    #
    # 3. Iteration: Use `for..of` directly when iterating known arrays,
    #    skip `iter()` wrapper
    #
    # 4. String operations: Inline `.length` access, avoid method wrappers
    #
    # Implementation approach:
    # - Flow-sensitive analysis tracking types through assignments
    # - Type annotations (Python 3 style) as hints
    # - Literal inference (constants have known types)
    # - Call return type tracking for known functions
    #
    # Example:
    #   inferer = TypeInference()
    #   inferer.visit(tree)
    #   # Now nodes have ._inferred_type attribute
    # -------------------------------------------------------------------------

    return tree
