from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_expr
from prescrypt.constants import JS_RESERVED_NAMES
from prescrypt.exceptions import JSError
from prescrypt.front import ast


@gen_expr.register
def gen_name(node: ast.Name, codegen: CodeGen) -> str:
    name = node.id

    # Convert Python's self to JavaScript's this
    if name == "self":
        return "this"

    if name in JS_RESERVED_NAMES:
        raise JSError(f"Cannot use reserved name '{name}' as a variable name", node)

    # TODO:
    if codegen.ns.is_known(name):
        return codegen.with_prefix(name)

    # if self._scope_prefix:
    #     for stackitem in reversed(self._stack):
    #         scope = stackitem[2]
    #         for prefix in reversed(self._scope_prefix):
    #             prefixed_name = prefix + name
    #             if prefixed_name in scope:
    #                 return prefixed_name

    # if name in NAME_MAP:
    #     return NAME_MAP[name]

    # if name in self._functions or name in ("undefined", "window"):
    #     return name

    # mark as used (not defined)
    # used_name = (name + "." + fullname) if fullname else name
    # self.vars.use(name, used_name)

    return name
