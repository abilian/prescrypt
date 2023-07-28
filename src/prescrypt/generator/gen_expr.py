from functools import singledispatch

from prescrypt.ast import ast


@singledispatch
def gen_expr(node: ast.expr) -> str | None:
    return None
