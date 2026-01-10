from __future__ import annotations

from prescrypt.codegen import CodeGen
from prescrypt.codegen.utils import flatten
from prescrypt.front import ast, to_ast
from prescrypt.testing import js_eq, js_eval
from prescrypt import py2js


def check_gen(code, expected):
    module = to_ast(code)
    codegen = CodeGen(module)
    js_code = flatten(codegen.gen())
    if expected:
        assert js_code == expected, f"Expected: {expected!r}\nGot: {js_code!r}"


def check_gen_exec(code, expected):
    """Compile Python code, execute as JS, and compare result with expected."""
    js_code = py2js(code)
    js_result = js_eval(js_code)
    assert js_eq(js_result, expected), f"Expected: {expected!r}\nGot: {js_result!r}"
