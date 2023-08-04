from textwrap import dedent

import pytest

from prescrypt.front import ast
from prescrypt.testing.data import EXPRESSIONS

from ..desugar import desugar
from ..scope import get_top_scope


@pytest.mark.parametrize("expression", EXPRESSIONS)
def test_expressions(expression: str):
    tree = ast.parse(expression)
    tree = desugar(tree)
    top_scope = get_top_scope(tree)
    # assert top_scope.defs == set()


def test_asignment():
    prog = "a = 1"
    tree = ast.parse(prog)
    tree = desugar(tree)
    top_scope = get_top_scope(tree)
    assert top_scope.defs == {"a"}


def test_asignment2():
    prog = "a = b"
    tree = ast.parse(prog)
    tree = desugar(tree)
    top_scope = get_top_scope(tree)
    assert top_scope.defs == {"a"}
    assert top_scope.uses == {"b"}


def test_fundef():
    prog = "def f(x): return x"
    tree = ast.parse(prog)
    tree = desugar(tree)
    top_scope = get_top_scope(tree)
    assert top_scope.defs == {"f"}

    fun_scope = top_scope.children[tree.body[0]]
    assert fun_scope.defs == {"x"}
    assert fun_scope.uses == {"x"}
    assert fun_scope.local_defs == set()


def test_lambda():
    prog = "a = lambda x: x"
    tree = ast.parse(prog)
    tree = desugar(tree)
    top_scope = get_top_scope(tree)
    assert top_scope.defs == {"a"}


def test_classdef():
    prog = "class A: pass"
    tree = ast.parse(prog)
    tree = desugar(tree)
    top_scope = get_top_scope(tree)
    assert top_scope.defs == {"A"}

    cls_scope = top_scope.children[tree.body[0]]
    assert cls_scope.defs == set()
    assert cls_scope.uses == set()
    assert cls_scope.local_defs == set()


def test_classdef2():
    prog = dedent(
        """
        class A(B):
            a = 1
            
            def f(self):
                pass
        """
    )
    tree = ast.parse(prog)
    tree = desugar(tree)
    top_scope = get_top_scope(tree)
    assert top_scope.defs == {"A"}

    cls_scope = top_scope.children[tree.body[0]]
    assert cls_scope.defs == {"a", "f"}
    assert cls_scope.uses == set()
    assert cls_scope.local_defs == set()


def test_imports():
    prog = dedent(
        """
        import a
        from b import c
        import d as e
        from f import g as h
        """
    )
    tree = ast.parse(prog)
    tree = desugar(tree)
    top_scope = get_top_scope(tree)
    assert top_scope.defs == {"a", "c", "e", "h"}
