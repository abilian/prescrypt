from __future__ import annotations

import pytest

from .utils import check_gen

LAMBDAS = [
    ("f = lambda: 1", "const f = () => (1);"),
    ("f = lambda x: x", "const f = (x) => (x);"),
    ("f = lambda x, y: x + y", "const f = (x, y) => (_pyfunc_op_add(x, y));"),
    ("f = lambda x=1: x", "const f = (x = 1) => (x);"),
]


@pytest.mark.parametrize(("code", "expected"), LAMBDAS)
def test_lambda(code, expected):
    check_gen(code, expected)
