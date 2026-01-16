from __future__ import annotations

import pytest

from .utils import check_gen

CONSTANTS = [
    # Constants
    ("True", "true"),
    ("False", "false"),
    ("None", "null"),
    ("1", "1"),
    ("1.0", "1.0"),
    ("'a'", "'a'"),
]


@pytest.mark.parametrize("code,expected", CONSTANTS)
def test_constants(code, expected):
    check_gen(code, expected)
