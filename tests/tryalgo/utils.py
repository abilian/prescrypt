from pathlib import Path
from textwrap import dedent

import dukpy
from devtools import debug

from prescrypt import py2js


def check(name, expr, expected):
    path = Path(__file__).parent / "tryalgo" / f"{name}.py"
    code = path.read_text()

    code += dedent(f"""
        result = {expr}
        check = (result == {repr(expected)})
    """)

    py_ctx = {}
    exec(code, py_ctx)
    py_result = py_ctx["result"]
    py_check = py_ctx["check"]

    jscode = py2js(code)
    js_env = dukpy.JSInterpreter()
    js_env.evaljs(jscode)
    debug(jscode)

    js_result = js_env.evaljs("result")
    js_check = js_env.evaljs("check")

    debug(py_result, js_result, py_check, js_check)

    assert check
    assert js_result == py_result
