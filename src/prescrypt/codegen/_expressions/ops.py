from __future__ import annotations

from prescrypt.constants import ATTRIBUTE_MAP, BINARY_OP, BOOL_OP, COMP_OP, UNARY_OP
from prescrypt.front import ast

from prescrypt.codegen.main import CodeGen, gen_expr
from prescrypt.codegen.utils import flatten, unify


@gen_expr.register
def gen_attribute(node: ast.Attribute, codegen: CodeGen) -> str:
    value_node, attr = node.value, node.attr

    # Generate the base expression
    base_name = unify(codegen.gen_expr(value_node))

    # Double underscore name mangling (for private attributes)
    if attr.startswith("__") and not attr.endswith("__") and base_name == "this":
        # Find enclosing class in the namespace stack
        for ns in reversed(codegen._stack):
            if ns.type == "class":
                attr = "_" + ns.name + attr
                break

    if attr in ATTRIBUTE_MAP:
        return ATTRIBUTE_MAP[attr].format(base_name)
    else:
        return f"{base_name}.{attr}"


@gen_expr.register
def gen_subscript(node: ast.Subscript, codegen: CodeGen):
    # TODO: handle slice
    value, slice_node = node.value, node.slice
    js_value = flatten(codegen.gen_expr(value))
    js_slice = flatten(codegen.gen_expr(slice_node))

    # Check context: Load (reading) vs Store (writing) vs Del (deleting)
    if isinstance(node.ctx, ast.Store):
        # For Store context, return the raw subscript expression
        # The assignment handler will use op_setitem
        return f"{js_value}[{js_slice}]"
    else:
        # For Load (and Del) context, use op_getitem for __getitem__ support
        return codegen.call_std_function("op_getitem", [js_value, js_slice])


@gen_expr.register
def gen_unary_op(node: ast.UnaryOp, codegen: CodeGen) -> str | list:
    # We've desugared all unary ops except Not and Invert (is it safe?)
    op = node.op
    operand = node.operand

    match op:
        case ast.Not():
            return ["!", codegen.gen_truthy(operand)]
        case ast.Invert():
            js_op = UNARY_OP[op]
            right = unify(codegen.gen_expr(operand))
            return [js_op, right]
        case _:  # pragma: no cover
            raise ValueError(f"Unknown unary operator {op!r} (should not happen)")


@gen_expr.register
def gen_bool_op(node: ast.BoolOp, codegen: CodeGen) -> str | list:
    op = node.op
    values = node.values

    js_op = f" {BOOL_OP[op]} "
    if type(op) == ast.Or:  # allow foo = bar or []
        js_values = [unify(codegen.gen_truthy(val)) for val in values[:-1]]
        js_values += [unify(codegen.gen_expr(values[-1]))]
    else:
        js_values = [unify(codegen.gen_truthy(val)) for val in values]
    return js_op.join(js_values)


@gen_expr.register
def gen_bin_op(node: ast.BinOp, codegen: CodeGen) -> str | list:
    left_node, op, right_node = node.left, node.op, node.right

    match op, left_node:
        case ast.Mod(), ast.Constant(str(s)):
            # Modulo on a string is string formatting in Python
            return codegen._format_string(left_node, right_node)

    js_left = unify(codegen.gen_expr(left_node))
    js_right = unify(codegen.gen_expr(right_node))

    match op:
        case ast.Add():
            # TODO: type inference
            return codegen.call_std_function("op_add", [js_left, js_right])

        case ast.Mult():
            # TODO: type inference
            return codegen.call_std_function("op_mul", [js_left, js_right])

        case ast.Pow():
            return ["Math.pow(", js_left, ", ", js_right, ")"]

        case ast.FloorDiv():
            return ["Math.floor(", js_left, "/", js_right, ")"]

        case _:
            # Default
            js_op = f" {BINARY_OP[op]} "
            return [js_left, js_op, js_right]


@gen_expr.register
def gen_compare(node: ast.Compare, codegen: CodeGen) -> str | list:
    left_node, ops, comparator_nodes = node.left, node.ops, node.comparators

    js_left = unify(codegen.gen_expr(left_node))
    js_right = unify(codegen.gen_expr(comparator_nodes[0]))

    # We've desugar'd chained comparisons, so we only have one op
    assert len(ops) == 1
    op = ops[0]

    if type(op) in (ast.Eq, ast.NotEq) and not js_left.endswith(".length"):
        code = codegen.call_std_function("op_equals", [js_left, js_right])
        if type(op) == ast.NotEq:
            code = "!" + code

        # TODO: type inference
        # if type(op) == ast.NotEq:
        #     code = [js_left, "!=", js_right]
        # else:
        #     code = [js_left, "==", js_right]
        return code

    elif type(op) in (ast.In, ast.NotIn):
        codegen.call_std_function("op_equals", [])  # trigger use of equals
        code = codegen.call_std_function("op_contains", [js_left, js_right])
        if type(op) == ast.NotIn:
            code = "!" + code
        return code

    else:
        js_op = COMP_OP[op]
        return f"{js_left} {js_op} {js_right}"
