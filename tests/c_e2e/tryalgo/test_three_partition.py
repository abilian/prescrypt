from __future__ import annotations

import pytest

from .utils import check


def test_three_partition():
    expr = "three_partition([5, 5, 3, 2]) == (1, 2, 12)"
    check("three_partition", expr, True)

    expr = "three_partition([1, 4, 5, 3, 2]) == (3, 4, 24)"
    check("three_partition", expr, True)

    expr = "three_partition([10, 2, 3]) is None"
    check("three_partition", expr, True)
