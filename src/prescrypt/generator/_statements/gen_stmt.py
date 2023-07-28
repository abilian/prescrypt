from functools import singledispatch

from prescrypt.ast import ast


@singledispatch
def gen_stmt(node: ast.stmt) -> str:
    raise NotImplementedError(f"gen_stmt not implemented for {node!r}")
