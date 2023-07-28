from buildstr import Builder

from prescrypt.ast import ast
from prescrypt.constants import ATTRIBUTE_MAP, JS_RESERVED_NAMES, NAME_MAP
from prescrypt.exceptions import JSError
from prescrypt.utils import unify

from .expr import gen_expr


@gen_expr.register
def gen_joinstr(node: ast.JoinedStr):
    values = node.values

    parts, value_nodes = [], []
    for n in values:
        match n:
            case ast.Str(s):
                parts.append(s)
            case ast.FormattedValue(value, conversion, format_spec):
                parts.append("{" + _parse_FormattedValue_fmt(n) + "}")
                value_nodes.append(n.value_node)
            case _:
                raise JSError("Unknown JoinedStr part: " + str(n))

    thestring = js_repr("".join(parts))
    return self.call_std_method(thestring, "format", value_nodes)
