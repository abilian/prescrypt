from buildstr import Builder

from prescrypt.ast import ast
from prescrypt.constants import ATTRIBUTE_MAP, JS_RESERVED_NAMES, NAME_MAP
from prescrypt.exceptions import JSError

from ..main import CodeGen, gen_expr
from ..utils import js_repr, unify


@gen_expr.register
def gen_joinstr(node: ast.JoinedStr, codegen: CodeGen):
    values = node.values

    parts, value_nodes = [], []
    for n in values:
        match n:
            case ast.Str(s):
                parts.append(s)
            case ast.FormattedValue(value, conversion, format_spec):
                parts.append("{" + _parse_FormattedValue_fmt(n) + "}")
                value_nodes.append(value)
            case _:
                raise JSError("Unknown JoinedStr part: " + str(n))

    thestring = js_repr("".join(parts))
    return codegen.call_std_method(thestring, "format", value_nodes)


@gen_expr.register
def gen_name(node: ast.Name, codegen: CodeGen) -> str:
    name = node.id
    # ctx can be Load, Store, Del -> can be of use somewhere?
    if name in JS_RESERVED_NAMES:
        raise JSError(f"Cannot use reserved name {name} as a variable name!")

    if self.vars.is_known(name):
        return self.with_prefix(name)

    if self._scope_prefix:
        for stackitem in reversed(self._stack):
            scope = stackitem[2]
            for prefix in reversed(self._scope_prefix):
                prefixed_name = prefix + name
                if prefixed_name in scope:
                    return prefixed_name

    if name in NAME_MAP:
        return NAME_MAP[name]

    # Else ...
    if not (name in self._functions or name in ("undefined", "window")):
        # mark as used (not defined)
        used_name = (name + "." + fullname) if fullname else name
        self.vars.use(name, used_name)

    return name


@gen_expr.register
def gen_attribute(node: ast.Attribute, codegen: CodeGen) -> str:
    value, attr, ctx = node.value, node.attr, node.ctx

    fullname = attr + "." + fullname if fullname else attr
    match value:
        case ast.Name():
            base_name = gen_expr(value)
        case ast.Attribute():
            base_name = self.gen_attribute(value, ctx, fullname)
        case _:
            base_name = unify(codegen.gen_expr(value))

    # Double underscore name mangling
    if attr.startswith("__") and not attr.endswith("__") and base_name == "this":
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == "class":
                classname = self._stack[i][1]
                attr = "_" + classname + attr
                break

    if attr in ATTRIBUTE_MAP:
        return ATTRIBUTE_MAP[attr].format(base_name)
    else:
        return f"{base_name}.{attr}"
