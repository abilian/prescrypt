from __future__ import annotations

from devtools import debug

from prescrypt import py2js
from prescrypt.testing import js_eq, js_eval

from .util import gen_expr


def test_gen():
    for i in range(0, 100):
        expr = gen_expr()

        try:
            py_result = eval(expr)
        except Exception:
            continue

        js_code = py2js(expr)
        js_code_short = py2js(expr, include_stdlib=False)
        js_result = js_eval(js_code)

        debug(expr, js_code_short, py_result, js_result)

        assert js_eq(py_result, js_result), f"{expr} -> {py_result} != {js_result}"
