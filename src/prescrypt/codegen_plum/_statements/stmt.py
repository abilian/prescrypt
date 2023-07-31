from functools import singledispatch

from prescrypt.ast import ast
from prescrypt.codegen.main import gen_expr
from prescrypt.codegen.context import Context


@singledispatch
def gen_stmt(node: ast.stmt, ctx: Context) -> str:
    raise NotImplementedError(f"gen_stmt not implemented for {node!r}")


# def gen_stmt(node_or_nodes: ast.stmt | list[ast.stmt]) -> str:
#     match node_or_nodes:
#         case [*stmts]:
#             return flatten([gen_stmt(node) for node in stmts])
#         case ast.stmt():
#             return flatten(_gen_stmt(node_or_nodes))
#         case _:
#             raise JSError(f"Unexpected node type: {type(node_or_nodes)}")


@gen_stmt.register
def gen_pass(node: ast.Pass, ctx: Context):
    return "/* pass */" + "\n"


@gen_stmt.register
def gen_return(node: ast.Return, ctx: Context):
    js_value = gen_expr(node.value)
    return f"return {js_value};\n"
