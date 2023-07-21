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
    "tuple()",
    "dict()",
    # Other builtin functions
    "chr(35)",
    "ord('a')",
    "len('abc')",
    "len([1, 2])",
    "len([])",
    "max([1, 2])",
    "min([1, 2])",
    "range(1)",
    "range(0, 1)",
    "range(0, 10, 2)",
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
    # Subscripts
    "[1][0] == 1",
    "{'a': 1}['a']",
    # Fail
    # "{1: 1}",
    # "list({'a': 1}.items())",
    # Ellipsis
    # "str(...) == 'Ellipsis'",
    "%d" % 1,
]

# Syntactically correct but will fail at runtime
simple_expressions2 = [
    "a.a"
]


# simple_expressions = [
#     "ord('a')",
# ]


# language=JavaScript
preamble_js = """
const _pyfunc_op_equals = function (a, b) {
  // nargs: 2
  var a_type = typeof a;
  // If a (or b actually) is of type string, number or boolean, we don't need
  // to do all the other type checking below.
  if (a_type === "string" || a_type === "boolean" || a_type === "number") {
    return a == b;
  }

  if (a == null || b == null) {
  } else if (Array.isArray(a) && Array.isArray(b)) {
    var i = 0,
      iseq = a.length == b.length;
    while (iseq && i < a.length) {
      iseq = _pyfunc_op_contains(a[i], b[i]);
      i += 1;
    }
    return iseq;
  } else if (a.constructor === Object && b.constructor === Object) {
    var akeys = Object.keys(a),
      bkeys = Object.keys(b);
    akeys.sort();
    bkeys.sort();
    var i = 0,
      k,
      iseq = _pyfunc_op_contains(akeys, bkeys);
    while (iseq && i < akeys.length) {
      k = akeys[i];
      iseq = _pyfunc_op_contains(a[k], b[k]);
      i += 1;
    }
    return iseq;
  }
  return a == b;
};

const _pyfunc_op_contains = function (a, b) {
  // nargs: 2
  if (b == null) {
  } else if (Array.isArray(b)) {
    for (var i = 0; i < b.length; i++) {
      if (_pyfunc_op_equals(a, b[i])) return true;
    }
    return false;
  } else if (b.constructor === Object) {
    for (var k in b) {
      if (a == k) return true;
    }
    return false;
  } else if (b.constructor == String) {
    return b.indexOf(a) >= 0;
  }
  var e = Error("Not a container: " + b);
  e.name = "TypeError";
  throw e;
};
"""


@pytest.mark.parametrize("expression", simple_expressions)
def test_expressions(expression: str):
    expected = eval(expression)

    compiler = Compiler()
    js_code = compiler.compile(expression)

    debug(expression, js_code)

    interpreter = dukpy.JSInterpreter()

    # stdlibjs = Path(__file__).parent / ".." / ".." / "src" / "prescrypt" / "stdlibjs"
    # functions_js = (stdlibjs / "functions.js").read_text()
    # methods_js = (stdlibjs / "methods.js").read_text()
    #
    # interpreter.evaljs(functions_js)
    # interpreter.evaljs(methods_js)

    # interpreter.evaljs(preamble_js)

    # try:
    #     interpreter.evaljs(preamble_js)
    # except JSRuntimeError as err:
    #     debug(vars(interpreter))
    #     debug(err, vars(err))

    full_code = preamble_js + "\n" + js_code
    try:
        js_result = interpreter.evaljs(full_code)
    except JSRuntimeError:
        print(full_code)
        raise

    assert js_result == expected, f"{expression} != {js_result} != {expected}"


@pytest.mark.parametrize("expression", simple_expressions2)
def test_expressions2(expression: str):
    compiler = Compiler()
    js_code = compiler.compile(expression)

    debug(expression, js_code)
