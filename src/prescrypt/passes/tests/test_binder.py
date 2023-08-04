from textwrap import dedent

import pytest

from prescrypt.ast import ast
from prescrypt.ast.scope import Variable
from prescrypt.testing.data import EXPRESSIONS as _EXPRESSIONS

from ..binder import Binder
from ..desugar import desugar

EXPRESSIONS = _EXPRESSIONS + [
    # "f = lambda x: x",
]


@pytest.mark.parametrize("expression", EXPRESSIONS)
def test_expressions(expression: str):
    tree, binder = parse(expression)


def test_globals():
    prog = dedent(
        """
        x = 1
        def f(y):
            pass
        class C:
            pass
    """
    )
    tree, binder = parse(prog)

    # Global scope
    g_scope = binder.scope
    assert sorted(g_scope.vars.keys()) == ["C", "f", "x"]
    assert g_scope.vars["C"] == Variable(name="C", type="class")
    assert g_scope.vars["x"] == Variable(name="x", type="variable")
    assert g_scope.vars["f"] == Variable(name="f", type="function")


def test_function():
    prog = dedent(
        """
        x = 1
        def f():
            a = 1
            b = a
        class C:
            pass
    """
    )
    tree, binder = parse(prog)

    # Global scope
    g_scope = binder.scope
    assert sorted(g_scope.vars.keys()) == ["C", "f", "x"]

    # Function scope
    fun_def_node = tree.body[1]
    l_scope = fun_def_node._scope

    assert sorted(l_scope.vars.keys()) == ["a", "b"]
    assert l_scope.vars["a"] == Variable(name="a", type="variable")
    assert l_scope.vars["b"] == Variable(name="b", type="variable")


def parse(prog: str):
    tree = ast.parse(prog)
    desugar(tree)
    binder = Binder()
    binder.visit(tree)
    return tree, binder
