from prescrypt.ast import ast
from prescrypt.utils import flatten

from ..context import Context
from .stmt import gen_stmt


@gen_stmt.register
def gen_module(module: ast.Module, ctx: Context):
    statements = module.body
    code = []
    for statement in statements:
        code += [ctx.gen_stmt(statement)]

    return flatten(code)
