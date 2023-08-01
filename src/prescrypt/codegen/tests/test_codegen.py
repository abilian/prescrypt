import ast

import pytest
from devtools import debug

from prescrypt.ast import ast
from prescrypt.codegen.main import CodeGen
from prescrypt.passes.desugar import desugar
from prescrypt.passes.scope import get_top_scope
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
    expected = "let a = 1;"
    assert _py2js(prog) == expected


def test_assignment_subscript():
    prog = "a = [0]; a[0] = 1"
    expected = "let a = [0];\na[0] = 1;"
    assert _py2js(prog) == expected


@pytest.mark.skip("TODO")
def test_multiple_assignment():
    prog = "a, b = 1, 2"
    expected = "let a = 1;"
    debug(_py2js(prog))
    assert _py2js(prog) == expected


def _py2js(prog):
    tree = ast.parse(prog)
    tree = desugar(tree)
    top_scope = get_top_scope(tree)
    codegen = CodeGen(tree, top_scope)
    return codegen.gen().strip()
