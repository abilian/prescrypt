from __future__ import annotations

import pytest

from .utils import check_gen

CONSTRUCTORS = [
    # Lists
    ("[]", "[]"),
    ("[1]", "[1]"),
    ("[1, 2]", "[1, 2]"),
    # Tuples
    ("()", "[]"),
    ("(1,)", "[1]"),
    ("(1, 2)", "[1, 2]"),
    # Dicts
    ("{}", "_pyfunc_create_dict()"),
    # FIXME ("{1: 2}", "_pyfunc_create_dict([[1, 2]])"),
]


@pytest.mark.parametrize(("code", "expected"), CONSTRUCTORS)
def test_constructors(code, expected):
    check_gen(code, expected)
