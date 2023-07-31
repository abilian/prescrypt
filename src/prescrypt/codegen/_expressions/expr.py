from functools import singledispatch

from prescrypt.ast import ast


@singledispatch
def gen_expr(node: ast.expr) -> str | None:
    raise NotImplementedError(f"gen_expr not implemented for {node!r}")
