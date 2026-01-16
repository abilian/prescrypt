from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from prescrypt import py2js
from prescrypt.testing import js_eq, js_eval


def check(name, expr, expected):
    prog_path = Path(__file__).parent / "tryalgo" / f"{name}.py"
    py_code = prog_path.read_text()

    py_code += dedent(f"""
        result = {expr}
        check = (result == {expected!r})
    """)

    py_ctx = {}
    exec(py_code, py_ctx)
    py_result = py_ctx["result"]
    py_check = py_ctx["check"]
    assert py_check

    js_code = py2js(py_code)
    js_result = js_eval(js_code)

    assert js_eq(js_result, py_result)
