import pytest
from devtools import debug

from prescrypt.compiler import py2js

ONE_LINE_STATEMENTS = [
    "pass",
    "if 1: pass",
    "while 0: pass",
    "while 1: break",
    "while 0: continue",
    "assert 1",
    "raise Exception()",
    "a = 1",
    "del a",
    "global a",
    "for i in range(10): pass",
    "def f(): pass",
    "def f(a): return a",
    "class A: pass",
    "class A: a = 1",
]

# language=Python
_MULTINE_STATEMENTS = """
pass
###
try:
    1
except:
    pass
###
def f():
    pass
###
class A:
    pass
###
class B:
    a = 1
###
class C:
    def __init__(self):
        pass
###
class D(A):
    pass
###
a = 1
if a == 1:
    print("hello")
"""


def get_statements():
    for stmt in ONE_LINE_STATEMENTS:
        yield stmt

    for stmt in _MULTINE_STATEMENTS.split("###"):
        yield stmt.strip()


@pytest.mark.parametrize("statement", get_statements())
def test_statement(statement: str):
    js_code = py2js(statement, include_stdlib=False)
    debug(statement, js_code)
