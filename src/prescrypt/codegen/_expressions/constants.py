from prescrypt.front import ast

from ..main import CodeGen, gen_expr

MAP = {True: "true", False: "false", None: "null"}


@gen_expr.register
def gen_constant(node: ast.Constant, codegen: CodeGen):
    match node:
        case ast.Constant(bool(value)):
            return str(value).lower()

        case ast.Constant(int(n)):
            return str(n)

        case ast.Constant(str(s)):
            return repr(s)

        case ast.Constant(float(s)):
            return str(s)

        case ast.Constant(None):
            return "null"

        case _:  # pragma: no cover
            raise ValueError(f"Unknown Constant: {node}")
