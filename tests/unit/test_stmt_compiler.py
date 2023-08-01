import pytest
from devtools import debug

from prescrypt.compiler import py2js

# language=Python
_MULTINE_STATEMENTS = """
try:
    1
except:
    pass
###
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
    "class A: pass",
    "class A: a = 1",
]


def get_statements():
    for stmt in ONE_LINE_STATEMENTS:
        yield stmt

    for stmt in _MULTINE_STATEMENTS.split("###"):
        yield stmt.strip()


@pytest.mark.parametrize("statement", get_statements())
def test_statement(statement: str):
    js_code = py2js(statement)
    debug(statement, js_code)


PROG = """
a = 10
while a > 0:
    a -= 1
    print("hello")
""".strip()


def test_prog():
    js_code = py2js(PROG, include_stdlib=False)
    debug(js_code)
    assert False
