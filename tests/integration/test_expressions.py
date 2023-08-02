import pytest
from devtools import debug

from prescrypt import py2js
from prescrypt.testing import EXPRESSIONS, js_eq
from prescrypt.testing import js_eval


@pytest.mark.parametrize("expression", EXPRESSIONS)
def test_expressions(expression: str):
    expected = eval(expression)

    js_code = py2js(expression)
    js_result = js_eval(js_code)

    short_code = py2js(expression, include_stdlib=False)
    debug(short_code)

    assert js_eq(js_result, expected), f"{expression} != {js_result} != {expected}"
