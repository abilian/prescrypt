from __future__ import annotations

from prescrypt.codegen import CodeGen
from prescrypt.codegen.utils import flatten
from prescrypt.front import ast
from prescrypt.front.passes.desugar import desugar


def check_gen(code, expected):
    module = desugar(ast.parse(code))
    codegen = CodeGen(module)
    expr_node = module.body[0].value
    js_code = flatten(codegen.gen_expr(expr_node))
    if expected:
        assert js_code == expected, f"Expected: {expected!r}\nGot: {js_code!r}"
