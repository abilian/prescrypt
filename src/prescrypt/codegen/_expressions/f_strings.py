from prescrypt.exceptions import JSError
from prescrypt.front import ast

from ..main import CodeGen, gen_expr
from ..utils import js_repr


@gen_expr.register
def gen_joinstr(node: ast.JoinedStr, codegen: CodeGen):
    values = node.values

    parts, value_nodes = [], []
    for n in values:
        match n:
            case ast.Constant(str(s)):
                parts.append(s)
            case ast.FormattedValue(value, conversion, format_spec):
                parts.append("{" + c_parse_FormattedValue_fmt(n) + "}")
                value_nodes.append(value)
            case _:
                raise JSError("Unknown JoinedStr part: " + str(n))

    thestring = js_repr("".join(parts))
    return codegen.call_std_method(thestring, "format", value_nodes)
