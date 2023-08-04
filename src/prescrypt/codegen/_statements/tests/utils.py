from prescrypt.codegen import CodeGen
from prescrypt.codegen.utils import flatten
from prescrypt.front import ast, to_ast


def check_gen(code, expected):
    module = to_ast(code)
    codegen = CodeGen(module)
    js_code = flatten(codegen.gen())
    if expected:
        assert js_code == expected, f"Expected: {expected!r}\nGot: {js_code!r}"
