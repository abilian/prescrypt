from pathlib import Path
from typing import cast

import dukpy
import pytest
from devtools import debug
from dukpy import JSRuntimeError

from prescrypt.ast import ast
from prescrypt.expr_compiler import ExpressionCompiler
from prescrypt.testing.data import EXPRESSIONS
from prescrypt.utils import flatten


class Compiler(ExpressionCompiler):

    def gen_stmt(self, node) -> str:
        """Not needed"""

    def compile(self, expression: str) -> str:
        tree = ast.parse(expression)
        assert isinstance(tree, ast.Module)
        # tree = cast(ast.Module, desugar(tree))
        expr = cast(ast.expr, tree.body[0].value)
        js_code = self.gen_expr(expr)
        return flatten(js_code)



# Syntactically correct but will fail at runtime
simple_expressions2 = [
    "a.a"
]

stdlib_js = Path(__file__).parent / ".." / ".." / "src" / "prescrypt" / "stdlibjs"
preamble_js = (stdlib_js / "_stdlib.js").read_text()


def js_eq(a, b):
    # TODO: Make this unnecessary
    if isinstance(a, (list, tuple)):
        if not isinstance(b, (list, tuple)):
            return False
        if len(a) != len(b):
            return False
        for i, j in zip(a, b):
            if not js_eq(i, j):
                return False
        return True
    return a == b


@pytest.mark.parametrize("expression", EXPRESSIONS)
def test_expressions(expression: str):
    py_code = expression
    py_result = eval(expression)

    compiler = Compiler()
    js_code = compiler.compile(expression)

    debug(py_code, js_code)

    interpreter = dukpy.JSInterpreter()

    full_code = preamble_js + "\n" + js_code
    try:
        js_result = interpreter.evaljs(full_code)
    except JSRuntimeError:
        print(full_code)
        raise

    assert js_eq(js_result, py_result), f"{expression} : {js_result} != {py_result}"


@pytest.mark.parametrize("expression", simple_expressions2)
def test_expressions2(expression: str):
    compiler = Compiler()
    js_code = compiler.compile(expression)

    debug(expression, js_code)
