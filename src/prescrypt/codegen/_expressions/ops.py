from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_expr
from prescrypt.codegen.type_utils import get_type, is_numeric, is_primitive, is_string
from prescrypt.codegen.utils import flatten, unify
from prescrypt.constants import ATTRIBUTE_MAP, BINARY_OP, BOOL_OP, COMP_OP, UNARY_OP
from prescrypt.front import ast


@gen_expr.register
def gen_attribute(node: ast.Attribute, codegen: CodeGen) -> str:
    value_node, attr = node.value, node.attr

    # Check for JS FFI access: js.X -> X (strip the 'js.' prefix)
    if isinstance(value_node, ast.Name) and codegen.is_js_ffi_name(value_node.id):
        # Direct access: js.console -> console
        return attr

    # Check for chained JS FFI access: js.console.log -> console.log
    if _is_js_ffi_chain(value_node, codegen):
        base_name = _strip_js_ffi_prefix(value_node, codegen)
        return f"{base_name}.{attr}"

    # Generate the base expression
    base_name = unify(codegen.gen_expr(value_node))

    # Wrap numeric literals in parentheses for method calls: 10.to_bytes() -> (10).to_bytes()
    if isinstance(value_node, ast.Constant) and isinstance(
        value_node.value, (int, float)
    ):
        base_name = f"({base_name})"

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


def _is_js_ffi_chain(node: ast.AST, codegen: CodeGen) -> bool:
    """Check if an AST node is part of a js.X.Y.Z chain."""
    if isinstance(node, ast.Name):
        return codegen.is_js_ffi_name(node.id)
    if isinstance(node, ast.Attribute):
        return _is_js_ffi_chain(node.value, codegen)
    return False


def _strip_js_ffi_prefix(node: ast.AST, codegen: CodeGen) -> str:
    """Convert js.X.Y to X.Y (strip the FFI module prefix)."""
    if isinstance(node, ast.Name):
        # This is the 'js' name itself - don't include it
        return ""
    if isinstance(node, ast.Attribute):
        base = _strip_js_ffi_prefix(node.value, codegen)
        if base:
            return f"{base}.{node.attr}"
        else:
            return node.attr
    return ""


@gen_expr.register
def gen_subscript(node: ast.Subscript, codegen: CodeGen):
    value, slice_node = node.value, node.slice
    js_value = flatten(codegen.gen_expr(value))

    # Handle slice expressions: a[1:5], a[:], a[::2]
    if isinstance(slice_node, ast.Slice):
        return gen_slice_expr(js_value, slice_node, codegen)

    # Handle regular index access
    js_slice = flatten(codegen.gen_expr(slice_node))

    # Check context: Load (reading) vs Store (writing) vs Del (deleting)
    if isinstance(node.ctx, ast.Store):
        # For Store context, return the raw subscript expression
        # The assignment handler will use op_setitem
        return f"{js_value}[{js_slice}]"
    else:
        # For Load (and Del) context, use op_getitem for __getitem__ support
        return codegen.call_std_function("op_getitem", [js_value, js_slice])


def gen_slice_expr(js_value: str, slice_node: ast.Slice, codegen: CodeGen) -> str:
    """Generate slice expression: a[1:5], a[:], a[::2], etc."""
    lower = slice_node.lower
    upper = slice_node.upper
    step = slice_node.step

    # Optimize: no step, use native .slice()
    if step is None:
        if lower is None and upper is None:
            # a[:] -> a.slice()
            return f"{js_value}.slice()"
        elif lower is None:
            # a[:5] -> a.slice(0, 5)
            js_upper = flatten(codegen.gen_expr(upper))
            return f"{js_value}.slice(0, {js_upper})"
        elif upper is None:
            # a[1:] -> a.slice(1)
            js_lower = flatten(codegen.gen_expr(lower))
            return f"{js_value}.slice({js_lower})"
        else:
            # a[1:5] -> a.slice(1, 5)
            js_lower = flatten(codegen.gen_expr(lower))
            js_upper = flatten(codegen.gen_expr(upper))
            return f"{js_value}.slice({js_lower}, {js_upper})"

    # Step present: use runtime helper
    js_lower = flatten(codegen.gen_expr(lower)) if lower else "null"
    js_upper = flatten(codegen.gen_expr(upper)) if upper else "null"
    js_step = flatten(codegen.gen_expr(step))
    return codegen.call_std_function("slice", [js_value, js_lower, js_upper, js_step])


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
            msg = f"Unknown unary operator {op!r} (should not happen)"
            raise ValueError(msg)


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
            # Modulo on a string constant is string formatting in Python
            return codegen._format_string(left_node, right_node)

    # Get types for optimization decisions
    left_type = get_type(left_node)
    right_type = get_type(right_node)

    # Handle % operator with possible string formatting
    # If left type is known string, or if left type is unknown but could be string,
    # use runtime op_mod which handles both string formatting and numeric modulo
    if isinstance(op, ast.Mod):
        if is_string(left_type) or not is_numeric(left_type):
            js_left = unify(codegen.gen_expr(left_node))
            js_right = unify(codegen.gen_expr(right_node))
            return codegen.call_std_function("op_mod", [js_left, js_right])

    js_left = unify(codegen.gen_expr(left_node))
    js_right = unify(codegen.gen_expr(right_node))

    match op:
        case ast.Add():
            # Optimize when both types are known and compatible
            if is_numeric(left_type) and is_numeric(right_type):
                # Both numeric: safe to use native +
                return f"({js_left} + {js_right})"
            elif is_string(left_type) and is_string(right_type):
                # Both strings: safe to use native +
                return f"({js_left} + {js_right})"
            else:
                # Unknown or mixed types: use helper for Python semantics
                return codegen.call_std_function("op_add", [js_left, js_right])

        case ast.Mult():
            # Optimize when both types are known
            if is_numeric(left_type) and is_numeric(right_type):
                # Both numeric: safe to use native *
                return f"({js_left} * {js_right})"
            elif is_string(left_type) and is_numeric(right_type):
                # String repeat: "x" * 3 -> "x".repeat(3)
                return f"{js_left}.repeat({js_right})"
            elif is_numeric(left_type) and is_string(right_type):
                # String repeat: 3 * "x" -> "x".repeat(3)
                return f"{js_right}.repeat({js_left})"
            else:
                # Unknown or mixed types: use helper
                return codegen.call_std_function("op_mul", [js_left, js_right])

        case ast.Pow():
            return ["Math.pow(", js_left, ", ", js_right, ")"]

        case ast.FloorDiv():
            return ["Math.floor(", js_left, "/", js_right, ")"]

        case ast.MatMult():
            # Matrix multiplication operator @
            return codegen.call_std_function("op_matmul", [js_left, js_right])

        case _:
            # Default
            js_op = f" {BINARY_OP[op]} "
            return [js_left, js_op, js_right]


@gen_expr.register
def gen_compare(node: ast.Compare, codegen: CodeGen) -> str | list:
    left_node, ops, comparator_nodes = node.left, node.ops, node.comparators

    # Get types for optimization decisions
    left_type = get_type(left_node)
    right_type = get_type(comparator_nodes[0])

    js_left = unify(codegen.gen_expr(left_node))
    js_right = unify(codegen.gen_expr(comparator_nodes[0]))

    # We've desugar'd chained comparisons, so we only have one op
    assert len(ops) == 1
    op = ops[0]

    if type(op) in (ast.Eq, ast.NotEq) and not js_left.endswith(".length"):
        # Optimize when both types are primitives: use === instead of helper
        if is_primitive(left_type) and is_primitive(right_type):
            if type(op) == ast.NotEq:
                return f"({js_left} !== {js_right})"
            else:
                return f"({js_left} === {js_right})"
        else:
            # Unknown or non-primitive types: use helper for deep comparison
            code = codegen.call_std_function("op_equals", [js_left, js_right])
            if type(op) == ast.NotEq:
                code = "!" + code
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
