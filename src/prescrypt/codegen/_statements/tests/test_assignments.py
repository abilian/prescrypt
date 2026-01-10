from __future__ import annotations

import pytest

from .utils import check_gen

LAMBDA_CALLS = [
    ("a = 1", "let a = 1;"),
    ("a = 1; b = 2", "let a = 1;\nlet b = 2;"),
    # ("a, b = 1, 2", "let [a, b] = [1, 2];"),
]


@pytest.mark.parametrize("code,expected", LAMBDA_CALLS)
def test_lambda(code, expected):
    check_gen(code, expected)
