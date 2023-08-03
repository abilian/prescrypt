#
# The rest
#

from prescrypt.ast import ast

from ..main import CodeGen, gen_expr


@gen_expr.register
def gen_if_exp(node: ast.IfExp, codegen: CodeGen) -> str:
    # in "a if b else c"
    body_node, test_node, orelse_node = node.body, node.test, node.orelse

    js_body = codegen.gen_expr(body_node)
    js_test = codegen.gen_truthy(test_node)
    js_else = codegen.gen_expr(orelse_node)

    return f"({js_test}) ? ({js_body}) : ({js_else})"
