from pathlib import Path

import dukpy
import pytest
from devtools import debug
from dukpy import JSRuntimeError

from prescrypt.compiler import py2js
from prescrypt.testing.data import EXPRESSIONS

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

    js_code = py2js(py_code)

    debug(py_code, js_code)

    interpreter = dukpy.JSInterpreter()

    full_code = preamble_js + "\n" + js_code
    try:
        js_result = interpreter.evaljs(full_code)
    except JSRuntimeError:
        print(full_code)
        raise

    assert js_eq(js_result, py_result), f"{expression} : {js_result} != {py_result}"
