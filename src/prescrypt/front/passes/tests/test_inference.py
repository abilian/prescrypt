from __future__ import annotations

import pytest

from prescrypt.front import ast
from prescrypt.front.passes.binder import Binder
from prescrypt.front.passes.desugar import desugar
from prescrypt.front.passes.type_inference import TypeInference
from prescrypt.testing.data import EXPRESSIONS


@pytest.mark.skip("TODO")
@pytest.mark.parametrize("expression", EXPRESSIONS)
def test_expressions(expression: str):
    tree = ast.parse(expression)
    desugar(tree)

    binder = Binder()
    binder.visit(tree)

    inferer = TypeInference()
    inferer.visit(tree)
