import ast

from .converter import convert
from . import ast as my_ast


def test_converter():
    expression = "1 + 2"
    tree = ast.parse(expression)
    new_tree = convert(tree)
    assert isinstance(new_tree, my_ast.Module)

    body = new_tree.body
    assert isinstance(body, list)

    expr = body[0]
    assert isinstance(expr, my_ast.Expr)

    value = expr.value
    assert isinstance(value, my_ast.BinOp)

    left = value.left
    assert isinstance(left, my_ast.Constant)
    assert left.value == 1

    op = value.op
    assert isinstance(op, my_ast.Add)

    right = value.right
    assert isinstance(right, my_ast.Constant)
    assert right.value == 2

    assert ast.unparse(tree) == "1 + 2"
    assert ast.unparse(new_tree) == "1 + 2"
