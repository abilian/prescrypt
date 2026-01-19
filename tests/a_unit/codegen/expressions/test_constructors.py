from __future__ import annotations

import pytest

from .utils import check_gen

CONSTRUCTORS = [
    # Lists - marked with _is_list for proper repr()
    ("[]", "Object.assign([], {_is_list: true})"),
    ("[1]", "Object.assign([1], {_is_list: true})"),
    ("[1, 2]", "Object.assign([1, 2], {_is_list: true})"),
    # Tuples - unmarked arrays display as ()
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
