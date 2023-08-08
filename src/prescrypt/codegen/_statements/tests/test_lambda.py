import pytest

from .utils import check_gen

LAMBDAS = [
    # ("f = lambda: 1", "f = () => 1;"),
]


@pytest.mark.parametrize("code,expected", LAMBDAS)
def test_lambda(code, expected):
    check_gen(code, expected)
