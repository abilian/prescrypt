import pytest

from .utils import check_gen

STRINGS = [
    # FIXME
    # ("f''", "''"),
    # ("f'abc'", "'abc'"),
    # ("f'{1}'", "1"),
]


@pytest.mark.parametrize("code,expected", STRINGS)
def test_f_strings(code, expected):
    check_gen(code, expected)
