from functools import singledispatch

from plum import dispatch

from prescrypt.ast import ast
from prescrypt.codegen_plum.context import Context


@dispatch
def gen_expr(ctx: Context, node: ast.expr) -> str | None:
    raise NotImplementedError(f"gen_expr not implemented for {node!r}")
