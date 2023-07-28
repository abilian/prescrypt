import ast

import pytest

from prescrypt.ast import ast
from prescrypt.passes.binder import Binder
from prescrypt.passes.type_inference import TypeInference
from prescrypt.testing.data import EXPRESSIONS

from ..desugar import desugar


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


def test_desugar_bool_op():
    code = "a and b and c"
    tree = ast.parse(code)
    tree = desugar(tree)
    assert ast.unparse(tree) == "a and (b and c)"


@pytest.mark.parametrize("expression", EXPRESSIONS)
def test_expressions(expression: str):
    tree = ast.parse(expression)
    desugar(tree)

    binder = Binder()
    binder.visit(tree)

    inferer = TypeInference()
    inferer.visit(tree)
