from __future__ import annotations

import pytest

from .utils import check_gen

COMPREHENSIONS = [
    # Ignore results as the compiled code is a bit complex (other tests will catch errors)
    ("[x for x in [1, 2, 3]]", None),
    ("[x + y for x in [1, 2] for y in [3, 4]]", None),
]


@pytest.mark.parametrize(("code", "expected"), COMPREHENSIONS)
def test_comprehensions(code, expected):
    check_gen(code, expected)
