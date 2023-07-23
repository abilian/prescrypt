import ast
from pathlib import Path
from typing import cast

import dukpy
import pytest
from devtools import debug
from dukpy import JSRuntimeError

from prescrypt.expr_compiler import ExpressionCompiler
from prescrypt.passes.desugar import desugar
from prescrypt.utils import flatten


class Compiler(ExpressionCompiler):

    def gen_stmt(self, node) -> str:
        """Not needed"""

    def compile(self, expression: str) -> str:
        tree = ast.parse(expression)
        tree = cast(ast.Module, desugar(tree))
        expr = cast(ast.expr, tree.body[0].value)
        js_code = self.gen_expr(expr)
        return flatten(js_code)


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
    "str()",
    "str(1)",
    "int(1)",
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
    "list()",
    "list([1])",
    "list((1,))",
    "list((1, 2))",
    "dict()",
    # Tuple is translated to array.
    # "tuple()",
    # Other builtin functions
    "chr(35)",
    "ord('a')",
    "len('abc')",
    "len([1, 2])",
    "len([])",
    "max([1, 2])",
    "min([1, 2])",
    "list(range(1))",
    "list(range(0, 1))",
    "list(range(0, 10, 2))",
    "sorted([2, 1])",
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
    "[]",
    "[1]",
    "[1, 2]",
    "[x for x in [1, 2]]",
    "[x for x in (1, 2)]",
    # "{k: k for k in 'abc'}",
    # Str
    "str(1.0) == '1.'",
    "str(1e3) == '1000.'",
    # Lists
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
    "dict(a=1)",
    "dict([('a', 1)])",
    "list({'a': 1})",
    "list({'a': 1}.keys())",
    "list({'a': 1}.values())",
    # Subscripts
    "[1][0] == 1",
    "{'a': 1}['a']",
    # Fail
    # "{1: 1}",
    # "list({'a': 1}.items())",
    # Ellipsis
    # "str(...) == 'Ellipsis'",
    "%d" % 1,
    # Equality
    "1 == 1",
    "1 != 0",
    # "dict() == {}",
    # "list() == []",
    # "tuple() == ()",
    # "set() == set()",
    # "list([1, 2]) == [1, 2]",
    # "tuple([1, 2]) == (1, 2)",
    # "set([1, 2]) == {1, 2}",
]

# Syntactically correct but will fail at runtime
simple_expressions2 = [
    "a.a"
]


# simple_expressions = [
#     "ord('a')",
# ]


stdlib_js = Path(__file__).parent / ".." / ".." / "src" / "prescrypt" / "stdlibjs"
preamble_js = (stdlib_js / "_stdlib.js").read_text()


@pytest.mark.parametrize("expression", simple_expressions)
def test_expressions(expression: str):
    expected = eval(expression)

    compiler = Compiler()
    js_code = compiler.compile(expression)

    debug(expression, js_code)

    interpreter = dukpy.JSInterpreter()

    full_code = preamble_js + "\n" + js_code
    try:
        js_result = interpreter.evaljs(full_code)
    except JSRuntimeError:
        print(full_code)
        raise

    assert js_result == expected, f"{expression} : {js_result} != {expected}"


@pytest.mark.parametrize("expression", simple_expressions2)
def test_expressions2(expression: str):
    compiler = Compiler()
    js_code = compiler.compile(expression)

    debug(expression, js_code)
