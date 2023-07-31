from prescrypt.ast import ast

from ...utils import flatten
from .. import gen_stmt


@gen_stmt.register
def gen_module(module: ast.Module):
    statements = module.body
    code = []
    for statement in statements:
        code += [gen_stmt(statement)]

    return flatten(code)
