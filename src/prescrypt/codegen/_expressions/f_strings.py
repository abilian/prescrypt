from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_expr
from prescrypt.codegen.utils import js_repr
from prescrypt.exceptions import JSError
from prescrypt.front import ast


@gen_expr.register
def gen_joinstr(node: ast.JoinedStr, codegen: CodeGen) -> str:
    """Generate code for f-strings (JoinedStr).

    f"Hello {name}!" becomes _pymeth_format.call("Hello {}!", name)
    """
    values = node.values

    parts, value_nodes = [], []
    for n in values:
        match n:
            case ast.Constant(str(s)):
                parts.append(s)
            case ast.FormattedValue(value, conversion, format_spec):
                parts.append("{" + _format_spec_to_string(conversion, format_spec) + "}")
                value_nodes.append(value)
            case _:
                raise JSError("Unknown JoinedStr part: " + str(n))

    thestring = js_repr("".join(parts))
    return codegen.call_std_method(thestring, "format", value_nodes)


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
