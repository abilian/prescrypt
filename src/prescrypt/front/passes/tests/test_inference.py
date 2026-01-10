from __future__ import annotations

import pytest

from prescrypt.front import ast
from prescrypt.testing.data import EXPRESSIONS

from ..binder import Binder
from ..desugar import desugar
from ..type_inference import TypeInference


@pytest.mark.skip("TODO")
@pytest.mark.parametrize("expression", EXPRESSIONS)
def test_expressions(expression: str):
    tree = ast.parse(expression)
    desugar(tree)

    binder = Binder()
    binder.visit(tree)

    inferer = TypeInference()
    inferer.visit(tree)
