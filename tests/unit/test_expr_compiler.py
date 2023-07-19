import ast
from typing import cast

import dukpy
import pytest
from devtools import debug
from dukpy import JSRuntimeError

from prescrypt.expr_compiler import ExpressionCompiler


class Compiler(ExpressionCompiler):

    def compile(self, expression: str) -> str:
        tree = ast.parse(expression).body[0].value
        expr = cast(ast.expr, tree)
        js_code = self.gen_expr(expr)
        return self.flatten(js_code)

    def flatten(self, js_code) -> str:
        match js_code:
            case str(s):
                return s
            case [*x]:
                return " ".join(self.flatten(s) for s in x)
            case _:
                raise ValueError(f"Unexpected type: {type(js_code)}")


simple_expressions = [
    # Literals
    "1",
    "1.0",
    "1e3",
    "1e-3",
    "True",
    "False",
    "'a'",
    '"a"',
    "f'a'",
    # Arithmetic
    "1+1",
    "2 * 3 + 5 * 6",
    "'a' + 'b'",
    "3 * 'a'",
    '"a" + "b"',
    "1 // 2",
    "1 % 2",
    # Constructors
    "str(1)",
    "int('1')",
    "float('1.0')",
    "bool(1)",
    "bool(0)",
    "bool(1.0)",
    "bool(0.0)",
    "bool('a')",
    "bool('')",
    "bool([1])",
    "bool([])",
    # Lambda
    "(lambda x: x)(3)",
    # Boolean expressions
    "True or False",
    "True and False",
    # Bitwise expressions
    "1 | 2",
    "1 & 2",
    "1 ^ 2",
    "1 << 2",
    "1 >> 2",
    # Comparison expressions
    "1 == 2",
    "1 != 2",
    "1 < 2",
    "1 <= 2",
    "1 > 2",
    "1 >= 2",
    # In expressions
    "1 in [1, 2]",
    "1 not in [1, 2]",
    "1 in (1, 2)",
    "1 not in (1, 2)",
    "1 in {1: 1}",
    "1 not in {1: 1}",
    "'a' in 'abc'",
    "'a' not in 'abc'",
    "'a' in ['a', 'b']",
    "'a' not in ['a', 'b']",
    "'a' in ('a', 'b')",
    "'a' not in ('a', 'b')",
    # If expressions
    "1 if True else 2",
    "1 if False else 2",
    # List and tuples expressions
    "[1, 2] == [2, 1]",
    "[1, 2] == list([1, 2])",
    "[1, 2] == [x for x in [1, 2]]",
    "[1, 2] == [x for x in (1, 2)]",
    "[1, 2] == sorted([2, 1])",
    # "{k: k for k in 'abc'}",
    # Str
    "str(1.0) == '1.'",
    "str(1e3) == '1000.'",
    # Lists
    "[]",
    "[1]",
    "[1, 2]",
    "{'a': 1}",
    # Str (nope)
    # "str(True)",
    # "str(False)",
    # "str(True) == 'True'",
    # "str(False) == 'False'",
    # Tupes (nope)
    # "(1, 2)",
    # Set expressions (nope)
    # "1 in {1}",
    # "1 not in {1}",
    # "{1, 2} == {2, 1}",
    # Dict
    "{}",
    "{'a': 1}",
    "list({'a': 1})",
    "list({'a': 1}.keys())",
    "list({'a': 1}.values())",
    "{'a': 1} == {'a': 1}",
    "dict(a=1) == {'a': 1}",
    "dict([('a', 1)]) == {'a': 1}",
    # Fail
    # "{1: 1}",
    # "list({'a': 1}.items())",
    # Ellipsis
    # "str(...) == 'Ellipsis'",
    "%d" % 1,
]


@pytest.mark.parametrize("expression", simple_expressions)
def test_expressions(expression: str):
    expected = eval(expression)

    compiler = Compiler()
    js_code = compiler.compile(expression)

    debug(expression, js_code)

    # interpreter = dukpy.JSInterpreter()
    # try:
    #     js_result = interpreter.evaljs(js_code)
    # except JSRuntimeError:
    #     debug(js_code)
    #     raise
    #
    # assert js_result == expected, f"{expression} != {js_result} != {expected}"
