from buildstr import Builder

from prescrypt.ast import ast
from prescrypt.constants import isidentifier1
from prescrypt.exceptions import JSError
from prescrypt.stdlib_js import FUNCTION_PREFIX
from prescrypt.utils import unify

from .expr import gen_expr


@gen_expr.register
def gen_list(node: ast.List):
    code = Builder()
    with code(surround=("[", "]"), separator=", "):
        code << [gen_expr(el) for el in node.elts]
    return code.build()


@gen_expr.register
def gen_tuple(node: ast.Tuple):
    code = Builder()
    with code(surround=("[", "]"), separator=", "):
        code << [gen_expr(el) for el in node.elts]
    return code.build()


@gen_expr.register
def gen_set(node: ast.Set):
    raise JSError("No Set in JS")


@gen_expr.register
def gen_dict(node: ast.Dict):
    # Oh JS; without the outer braces, it would only be an Object if used
    # in an assignment ...
    code = ["({"]
    for key, val in zip(node.keys, node.values):
        if isinstance(key, (ast.Num, ast.NameConstant)):
            code += gen_expr(key)
        elif (
            isinstance(key, ast.Str)
            and isidentifier1.match(key.value)
            and key.value[0] not in "0123456789"
        ):
            code += key.value
        else:
            return _gen_dict_fallback(node.keys, node.values)

        code.append(": ")
        code += gen_expr(val)
        code.append(", ")
    if node.keys:
        code.pop(-1)  # skip last comma
    code.append("})")

    return code


def _gen_dict_fallback(keys: list[ast.expr], values: list[ast.expr]) -> str:
    func_args = []
    for key, val in zip(keys, values):
        func_args += [
            unify(gen_expr(key)),
            unify(gen_expr(val)),
        ]
    # self.call_std_function("create_dict", [])
    return FUNCTION_PREFIX + "create_dict(" + ", ".join(func_args) + ")"
