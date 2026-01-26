from __future__ import annotations

import pytest

from prescrypt.codegen.main import CodeGen
from prescrypt.front import ast
from prescrypt.front.passes.binder import Binder
from prescrypt.front.passes.desugar import desugar
from prescrypt.testing.data import EXPRESSIONS


@pytest.mark.parametrize("expression", EXPRESSIONS)
def test_expressions(expression: str):
    code = _py2js(expression)
    assert code


def test_pass():
    prog = "pass"
    expected = "/* pass */"
    assert _py2js(prog) == expected


def test_int():
    prog = "1"
    expected = "1;"
    assert _py2js(prog) == expected


def test_assignment():
    prog = "a = 1"
    expected = "const a = 1;"  # Single assignment -> const
    assert _py2js(prog) == expected


def test_assignment_subscript():
    prog = "a = [0]; a[0] = 1"
    # Uses op_setitem for __setitem__ support
    # List is marked with _is_list for proper repr()
    expected = (
        "const a = Object.assign([0], {_is_list: true});\n_pyfunc_op_setitem(a, 0, 1);"
    )
    assert _py2js(prog) == expected


def test_multiple_assignment():
    prog = "a, b = 1, 2"
    expected = "let [a, b] = [1, 2];"  # Tuple unpacking
    assert _py2js(prog) == expected


def _py2js(prog):
    tree = ast.parse(prog)
    tree = desugar(tree)
    Binder().visit(tree)  # Run Binder to get scope info
    codegen = CodeGen(tree)
    return codegen.gen().strip()
