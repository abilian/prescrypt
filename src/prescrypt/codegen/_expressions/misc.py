#
# The rest
#
from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_expr
from prescrypt.codegen.utils import flatten
from prescrypt.front import ast


@gen_expr.register
def gen_if_exp(node: ast.IfExp, codegen: CodeGen) -> str:
    # in "a if b else c"
    body_node, test_node, orelse_node = node.body, node.test, node.orelse

    js_body = codegen.gen_expr(body_node)
    js_test = codegen.gen_truthy(test_node)
    js_else = codegen.gen_expr(orelse_node)

    return f"({js_test}) ? ({js_body}) : ({js_else})"


@gen_expr.register
def gen_starred(node: ast.Starred, codegen: CodeGen) -> str:
    """Generate starred expression: *args -> ...args

    Used for spread in function calls, list literals, etc.
    """
    value = flatten(codegen.gen_expr(node.value))
    return f"...{value}"
