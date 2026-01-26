from __future__ import annotations

import pytest

from .utils import check


def test_primes():
    expr = "all([eratosthene(n) == gries_misra(n)[0] for n in range(3, 100)])"
    check("primes", expr, True)
