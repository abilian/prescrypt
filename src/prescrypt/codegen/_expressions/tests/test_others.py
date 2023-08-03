import pytest

from .utils import check_gen

EXPRS = [
    # Int
    ("True if True else False", "(true) ? (true) : (false)"),
]


@pytest.mark.parametrize("code,expected", EXPRS)
def test_ops(code, expected):
    check_gen(code, expected)
