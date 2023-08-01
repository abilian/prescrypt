import dukpy
import pytest

from prescrypt import py2js
from prescrypt.testing.data import EXPRESSIONS


@pytest.mark.parametrize("expression", EXPRESSIONS)
def test_expressions(expression: str):
    expected = eval(expression)

    jscode = py2js(expression)
    interpreter = dukpy.JSInterpreter()
    js_result = interpreter.evaljs(jscode)

    assert js_result == expected, f"{expression} != {js_result} != {expected}"
