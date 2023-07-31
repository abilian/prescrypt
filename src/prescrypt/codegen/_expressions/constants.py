from prescrypt.ast import ast

from ..main import CodeGen, gen_expr


@gen_expr.register
def gen_constant(node: ast.Constant, codegen: CodeGen):
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
