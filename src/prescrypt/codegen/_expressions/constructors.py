from __future__ import annotations

from buildstr import Builder

from prescrypt.codegen.main import CodeGen, gen_expr
from prescrypt.codegen.utils import flatten, unify
from prescrypt.exceptions import JSError
from prescrypt.front import ast


@gen_expr.register
def gen_list(node: ast.List, codegen: CodeGen):
    code = Builder()
    with code(surround=("[", "]"), separator=", "):
        code << [flatten(codegen.gen_expr(el)) for el in node.elts]
    return code.build()


@gen_expr.register
def gen_tuple(node: ast.Tuple, codegen: CodeGen):
    code = Builder()
    with code(surround=("[", "]"), separator=", "):
        code << [flatten(codegen.gen_expr(el)) for el in node.elts]
    return code.build()


@gen_expr.register
def gen_set(node: ast.Set, codegen: CodeGen):
    raise JSError("No Set in JS")


@gen_expr.register
def gen_dict(node: ast.Dict, codegen: CodeGen):
    return _gen_dict_fallback(codegen, node.keys, node.values)

    # TODO: doesn't work, ast.Num, ast.Str are not used anymore
    # # Oh JS; without the outer braces, it would only be an Object if used
    # # in an assignment ...
    # code = ["({"]
    # for key, val in zip(node.keys, node.values):
    #     if isinstance(key, (ast.Num, ast.NameConstant)):
    #         code += codegen.gen_expr(key)
    #     elif (
    #         isinstance(key, ast.Str)
    #         and isidentifier1.match(key.value)
    #         and key.value[0] not in "0123456789"
    #     ):
    #         code += key.value
    #     else:
    #         return _gen_dict_fallback(codegen, node.keys, node.values)
    #
    #     code.append(": ")
    #     code += codegen.gen_expr(val)
    #     code.append(", ")
    # if node.keys:
    #     code.pop(-1)  # skip last comma
    # code.append("})")
    #
    # return code


def _gen_dict_fallback(codegen: CodeGen, keys: list[ast.expr], values: list[ast.expr]) -> str:
    func_args = []
    for key, val in zip(keys, values):
        func_args += [
            unify(gen_expr(key, codegen)),
            unify(gen_expr(val, codegen)),
        ]
    # Use call_std_function for usage tracking
    return codegen.call_std_function("create_dict", func_args)
