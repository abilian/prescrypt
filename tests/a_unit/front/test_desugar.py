from __future__ import annotations

import pytest

from prescrypt.front import ast
from prescrypt.front.passes.desugar import desugar
from prescrypt.testing.data import EXPRESSIONS


def test_desugar_addition():
    code = "1 + 1 + 1"
    tree = ast.parse(code)
    tree = desugar(tree)
    assert ast.unparse(tree) == "1 + 1 + 1"


def test_desugar_comparison():
    code = "1 < 2 < 3"
    tree = ast.parse(code)
    tree = desugar(tree)
    assert ast.unparse(tree) == "1 < 2 and 2 < 3"


def test_desugar_aug_ass():
    code = "a += 1"
    tree = ast.parse(code)
    tree = desugar(tree)
    assert ast.unparse(tree) == "a = a + 1"


@pytest.mark.parametrize("code", ["a += 1", "obj.attr += 1", "a[i] += 1"])
def test_desugar_aug_assign_contexts(code: str):
    """The target is read on the right and written on the left.

    `unparse` does not show `ctx`, so `test_desugar_aug_ass` above passes even
    when the read copy is left in Store context. Codegen does read it: a
    Subscript in Store context compiles to a raw index instead of op_getitem.
    """
    stmt = desugar(ast.parse(code)).body[0]
    assert isinstance(stmt.targets[0].ctx, ast.Store)
    assert isinstance(stmt.value.left.ctx, ast.Load)


def test_desugar_bool_op():
    code = "a and b and c"
    tree = ast.parse(code)
    tree = desugar(tree)
    assert ast.unparse(tree) == "a and (b and c)"


@pytest.mark.parametrize("expression", EXPRESSIONS)
def test_expressions(expression: str):
    tree = ast.parse(expression)
    desugar(tree)
