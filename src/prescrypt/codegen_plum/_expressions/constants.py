from plum import dispatch

from prescrypt.ast import ast

from ..context import Context


@dispatch
def gen_expr(ctx: Context, node: ast.Constant):
    match node:
        case ast.Constant(bool(value)):
            return "true" if value else "false"

        case ast.Constant(int(n)):
            return str(n)

        case ast.Constant(str(s)):
            return repr(s)

        case ast.Constant(float(s)):
            return str(s)

        case ast.NameConstant(value):
            M = {True: "true", False: "false", None: "null"}
            return M[value]
