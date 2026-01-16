from __future__ import annotations

import pytest

from .utils import check_gen

ASSIGNMENTS = [
    # Single assignment -> const
    ("a = 1", "const a = 1;"),
    ("a = 1; b = 2", "const a = 1;\nconst b = 2;"),
    # Multiple assignment -> let
    ("a = 1; a = 2", "let a = 1;\na = 2;"),
    # ("a, b = 1, 2", "let [a, b] = [1, 2];"),
]


@pytest.mark.parametrize("code,expected", ASSIGNMENTS)
def test_assignments(code, expected):
    check_gen(code, expected)
