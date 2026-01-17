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


@gen_expr.register
def gen_namedexpr(node: ast.NamedExpr, codegen: CodeGen) -> str:
    """Generate walrus operator: x := value -> (x = value)

    The walrus operator assigns and returns the value.
    In JavaScript, assignment is also an expression.
    """
    # Get the target name
    target = node.target
    if not isinstance(target, ast.Name):
        from prescrypt.exceptions import JSError

        msg = "Walrus operator target must be a simple name"
        raise JSError(msg)

    name = target.id
    js_value = flatten(codegen.gen_expr(node.value))

    # Check if variable needs declaration
    needs_decl = not codegen.ns.is_known(name)
    if needs_decl:
        codegen.add_var(name)
        # Use 'var' because it's hoisted - declaration will be moved to top of scope
        # Emit as separate statement (with newline) followed by the expression
        return f"var {name};\n({name} = {js_value})"

    return f"({name} = {js_value})"


@gen_expr.register
def gen_yield(node: ast.Yield, codegen: CodeGen) -> str:
    """Generate yield expression.

    Python: yield value, x = yield
    JS: yield value

    JavaScript generators use the same 'yield' keyword, so this is a direct mapping.
    The value passed to .next(value) becomes the result of the yield expression.
    """
    if node.value is None:
        return "yield"

    value = flatten(codegen.gen_expr(node.value))
    return f"yield {value}"


@gen_expr.register
def gen_yield_from(node: ast.YieldFrom, codegen: CodeGen) -> str:
    """Generate yield from expression.

    Python: yield from iterable
    JS: yield* iterable

    The yield* expression delegates to another iterator/generator.
    The return value of yield from is the value passed to the final StopIteration.
    """
    value = flatten(codegen.gen_expr(node.value))
    return f"yield* {value}"
