from prescrypt.ast import ast
from prescrypt.constants import BINARY_OP, BOOL_OP, COMP_OP, UNARY_OP
from prescrypt.utils import unify

from ..stdlib import call_std_function
from ..utilities import _format_string, ctx, gen_truthy
from .expr import gen_expr


@gen_expr.register
def gen_subscript(node: ast.Subscript):
    # TODO: handle slice, ctx
    value, slice = node.value, node.slice
    js_value = gen_expr(value)
    js_slice = gen_expr(slice)
    return f"{js_value}[{js_slice}]"


@gen_expr.register
def gen_unary_op(node: ast.UnaryOp) -> str | list:
    op = node.op
    operand = node.operand

    if type(op) is ast.Not:
        return ["!", gen_truthy(operand)]
    else:
        js_op = UNARY_OP[op]
        right = unify(gen_expr(operand))
        return [js_op, right]


@gen_expr.register
def gen_bool_op(node: ast.BoolOp) -> str | list:
    op = node.op
    values = node.values

    js_op = f" {BOOL_OP[op]} "
    if type(op) == ast.Or:  # allow foo = bar or []
        js_values = [unify(gen_truthy(val)) for val in values[:-1]]
        js_values += [unify(gen_expr(values[-1]))]
    else:
        js_values = [unify(gen_truthy(val)) for val in values]
    return js_op.join(js_values)


@gen_expr.register
def gen_bin_op(node: ast.BinOp) -> str | list:
    left, op, right = node.left, node.op, node.right

    if type(op) == ast.Mod and isinstance(left, ast.Str):
        # Modulo on a string is string formatting in Python
        return _format_string(left, right)

    js_left = unify(gen_expr(left))
    js_right = unify(gen_expr(right))

    if type(op) == ast.Add:
        C = ast.Num, ast.Str
        if ctx._pscript_overload and not (
            isinstance(left, C)
            or isinstance(right, C)
            or (
                isinstance(left, ast.BinOp)
                and type(left.op) == ast.Add
                and "op_add" not in left
            )
            or (
                isinstance(right, ast.BinOp)
                and type(right.op) == ast.Add
                and "op_add" not in right
            )
        ):
            return call_std_function("op_add", [js_left, js_right])

    elif type(op) == ast.Mult:
        C = ast.Num
        if ctx._pscript_overload and not (isinstance(left, C) and isinstance(right, C)):
            return call_std_function("op_mult", [js_left, js_right])

    elif type(op) == ast.Pow:
        return ["Math.pow(", js_left, ", ", js_right, ")"]

    elif type(op) == ast.FloorDiv:
        return ["Math.floor(", js_left, "/", js_right, ")"]

    # Default
    js_op = f" {BINARY_OP[op]} "
    return [js_left, js_op, js_right]


@gen_expr.register
def gen_compare(node: ast.Compare) -> str | list:
    left, ops, comparators = node.left, node.ops, node.comparators

    js_left = unify(gen_expr(left))
    js_right = unify(gen_expr(comparators[0]))

    op = ops[0]

    if type(op) in (ast.Eq, ast.NotEq) and not js_left.endswith(".length"):
        if ctx._pscript_overload:
            code = call_std_function("op_equals", [js_left, js_right])
            if type(op) == ast.NotEq:
                code = "!" + code
        else:
            if type(op) == ast.NotEq:
                code = [js_left, "!=", js_right]
            else:
                code = [js_left, "==", js_right]
        return code

    elif type(op) in (ast.In, ast.NotIn):
        call_std_function("op_equals", [])  # trigger use of equals
        code = call_std_function("op_contains", [js_left, js_right])
        if type(op) == ast.NotIn:
            code = "!" + code
        return code

    else:
        js_op = COMP_OP[op]
        return f"{js_left} {js_op} {js_right}"
