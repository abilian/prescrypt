from __future__ import annotations

import pytest

from .utils import check_gen

IFS = [
    ("if True: pass", ""),
    ("if True: pass\nelse: pass", ""),
    ("if False: pass", ""),
    ("if False: pass\nelse: pass", ""),
    ("if True: print(1)", ""),
]


@pytest.mark.parametrize(("code", "expected"), IFS)
def test_if(code, expected):
    check_gen(code, expected)
