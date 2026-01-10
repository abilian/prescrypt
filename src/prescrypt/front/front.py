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
    # inferer = TypeInference()
    # inferer.visit(tree)
    return tree
