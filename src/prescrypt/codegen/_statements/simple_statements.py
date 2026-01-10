from prescrypt.front import ast

from ..main import CodeGen, gen_stmt
from ..utils import flatten


@gen_stmt.register
def _gen_pass(node: ast.Pass, codegen: CodeGen):
    return "/* pass */" + "\n"


@gen_stmt.register
def _gen_expr(node: ast.Expr, codegen: CodeGen):
    return flatten(codegen.gen_expr(node.value)) + ";\n"


@gen_stmt.register
def _gen_return(node: ast.Return, codegen: CodeGen):
    js_value = codegen.gen_expr(node.value)
    return f"return {js_value};\n"


@gen_stmt.register
def _gen_global(node: ast.Global, codegen: CodeGen):
    # JavaScript doesn't have a global declaration - variables are either
    # local (let/const) or implicitly global. We emit a comment for clarity.
    names = ", ".join(node.names)
    return f"/* global {names} */\n"


@gen_stmt.register
def _gen_nonlocal(node: ast.Nonlocal, codegen: CodeGen):
    # JavaScript closures automatically capture outer variables.
    # We emit a comment for clarity.
    names = ", ".join(node.names)
    return f"/* nonlocal {names} */\n"
