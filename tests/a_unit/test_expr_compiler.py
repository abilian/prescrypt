from __future__ import annotations

import json

import pytest
import quickjs
from devtools import debug

from prescrypt.compiler import py2js
from prescrypt.testing.data import EXPRESSIONS


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
    py_result = json.loads(json.dumps(eval(expression)))

    js_code = py2js(py_code, include_stdlib=False)
    full_js_code = py2js(py_code)

    ctx = quickjs.Context()
    js_result = ctx.eval(full_js_code)
    if isinstance(js_result, quickjs.Object):
        js_result = json.loads(js_result.json())

    if not js_eq(js_result, py_result):
        debug(py_code, js_code)

    assert js_eq(js_result, py_result), f"{expression} : {js_result} != {py_result}"
