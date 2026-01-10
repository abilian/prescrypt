from __future__ import annotations

from unittest import skip

import pytest

from .utils import check

EXAMPLES = [
    ("13 + A47 * ZZ22", 37),
    ("( 12 - 2 ) * 5", 50),
    ("4 / 7 + 4 / 7", 0),
    ("3 * 3 / 7", 1),
    ("12", 12),
]


@skip
@pytest.mark.parametrize("str_expr, value", EXAMPLES)
def test_arithm_expr_eval(str_expr, value):
    cell = {"ZZ22": 3, "A47": 8}
    expr = f"arithm_expr_parse({str_expr.split()})"
    expr_ = f"arithm_expr_eval({cell}, {expr})"
    check("arithm_expr_eval", expr_, value)
