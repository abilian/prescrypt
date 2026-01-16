from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_expr
from prescrypt.codegen.type_utils import get_type, is_primitive
from prescrypt.codegen.utils import js_repr, unify
from prescrypt.exceptions import JSError
from prescrypt.front import ast


@gen_expr.register
def gen_joinstr(node: ast.JoinedStr, codegen: CodeGen) -> str:
    """Generate code for f-strings (JoinedStr).

    Optimizes to direct concatenation when all interpolated values are primitives
    without format specs or conversions. Otherwise falls back to _pymeth_format.

    f"Hello {name}!" with name: str -> 'Hello ' + name + '!'
    f"Value: {x:.2f}" -> _pymeth_format.call("Value: {:.2f}", x)
    """
    values = node.values

    # Try optimization: direct concatenation for simple cases
    optimized = _try_optimize_fstring(node, codegen)
    if optimized is not None:
        return optimized

    # Fall back to format method
    parts, value_nodes = [], []
    for n in values:
        match n:
            case ast.Constant(str(s)):
                parts.append(s)
            case ast.FormattedValue(value, conversion, format_spec):
                parts.append(
                    "{" + _format_spec_to_string(conversion, format_spec) + "}"
                )
                value_nodes.append(value)
            case _:
                raise JSError("Unknown JoinedStr part: " + str(n))

    thestring = js_repr("".join(parts))
    return codegen.call_std_method(thestring, "format", value_nodes)


def _try_optimize_fstring(node: ast.JoinedStr, codegen: CodeGen) -> str | None:
    """Try to optimize f-string to direct concatenation.

    Returns optimized code if possible, None otherwise.

    Optimization is possible when:
    - All interpolated values have primitive types (Int, Float, String, Bool)
    - No format specs are used
    - No conversions are used (!r, !s, !a)
    """
    parts = []

    for n in node.values:
        match n:
            case ast.Constant(str(s)):
                # String literal part - include if non-empty
                if s:
                    parts.append(js_repr(s))

            case ast.FormattedValue(value, conversion, format_spec):
                # Check if this can be optimized
                # No conversion allowed (-1 means no conversion)
                if conversion != -1:
                    return None

                # No format spec allowed
                if format_spec is not None:
                    return None

                # Value must have a primitive type
                val_type = get_type(value)
                if not is_primitive(val_type):
                    return None

                # Generate the value expression
                js_value = unify(codegen.gen_expr(value))
                parts.append(js_value)

            case _:
                # Unknown node type - can't optimize
                return None

    # Build concatenation expression
    if not parts:
        return "''"
    elif len(parts) == 1:
        return parts[0]
    else:
        return "(" + " + ".join(parts) + ")"


def _format_spec_to_string(conversion: int, format_spec: ast.expr | None) -> str:
    """Convert FormattedValue conversion and format_spec to a format string.

    Args:
        conversion: -1 for none, 115 for !s, 114 for !r, 97 for !a
        format_spec: Optional format specification (can be JoinedStr)

    Returns:
        Format string like "", "!r", ":.2f", "!r:.2f"
    """
    result = ""

    # Handle conversion (!s, !r, !a)
    if conversion == 115:  # ord('s')
        result += "!s"
    elif conversion == 114:  # ord('r')
        result += "!r"
    elif conversion == 97:  # ord('a')
        result += "!a"
    # -1 means no conversion

    # Handle format spec
    if format_spec is not None:
        spec_str = _extract_format_spec(format_spec)
        if spec_str:
            result += ":" + spec_str

    return result


def _extract_format_spec(format_spec: ast.expr) -> str:
    """Extract format specification string from AST node.

    The format_spec can be a JoinedStr (for dynamic specs) or Constant.
    """
    match format_spec:
        case ast.JoinedStr(values):
            # Format spec is itself an f-string (e.g., f"{x:.{precision}f}")
            # For now, only support simple constant specs
            parts = []
            for v in values:
                match v:
                    case ast.Constant(str(s)):
                        parts.append(s)
                    case _:
                        # Dynamic format specs are complex - fall back to empty
                        return ""
            return "".join(parts)
        case ast.Constant(str(s)):
            return s
        case _:
            return ""
