import ast
from textwrap import dedent
from typing import cast

import dukpy
import pytest
from devtools import debug
from dukpy import JSRuntimeError

from prescrypt.stmt_compiler import StatementCompiler


class Compiler(StatementCompiler):

    def compile(self, statement: str) -> str:
        tree = ast.parse(statement).body
        js_code = self.gen_stmt(tree)
        return self.flatten(js_code)


simple_statements = [
    "pass",
    "if 1: pass",
    "while 0: pass",
    "while 1: break",
    "while 0: continue",
    "assert 1",
    # dedent("""
    #     try:
    #         1
    #     except:
    #         pass
    # """)
    #
    # "for i in range(10): pass",
]


@pytest.mark.parametrize("statement", simple_statements)
def test_statement(statement: str):
    # expected = eval(expression)

    compiler = Compiler()
    js_code = compiler.compile(statement)

    debug(statement, js_code)

    # interpreter = dukpy.JSInterpreter()
    # try:
    #     js_result = interpreter.evaljs(js_code)
    # except JSRuntimeError:
    #     debug(js_code)
    #     raise
    #
    # assert js_result == expected, f"{expression} != {js_result} != {expected}"
