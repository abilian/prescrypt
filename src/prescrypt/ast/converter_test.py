import ast as native_ast

import pytest

from ..testing.data import EXPRESSIONS
from . import ast
from .converter import convert


def test_converter():
    expression = "1 + 2"
    tree = native_ast.parse(expression)
    new_tree = convert(tree)
    assert isinstance(new_tree, ast.Module)

    body = new_tree.body
    assert isinstance(body, list)

    expr = body[0]
    assert isinstance(expr, ast.Expr)

    value = expr.value
    assert isinstance(value, ast.BinOp)

    left = value.left
    assert isinstance(left, ast.Constant)
    assert left.value == 1

    op = value.op
    assert isinstance(op, ast.Add)

    right = value.right
    assert isinstance(right, ast.Constant)
    assert right.value == 2

    assert native_ast.unparse(tree) == "1 + 2"
    assert native_ast.unparse(new_tree) == "1 + 2"


@pytest.mark.parametrize("expression", EXPRESSIONS)
def test_converter2(expression):
    tree = native_ast.parse(expression)
    new_tree = convert(tree)
    check_tree(new_tree)


def check_tree(tree: ast.AST):
    for k in tree._fields:
        v = getattr(tree, k)
        if isinstance(v, list):
            for x in v:
                check_tree(x)
        elif isinstance(v, ast.AST):
            check_tree(v)
        elif isinstance(v, (int, float, str, bool, type(None))):
            pass
        else:
            raise ValueError(f"Unknown type: {type(v)}")
