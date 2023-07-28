import ast

import pytest
from devtools import debug

from prescrypt.compiler import Compiler

simple_statements = [
    "pass",
    "if 1: pass",
    "while 0: pass",
    "while 1: break",
    "while 0: continue",
    "assert 1",
    "a = 1",
    # "global a",
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
    compiler = Compiler()
    js_code = compiler.compile(statement)
    debug(statement, js_code)
