from __future__ import annotations

from unittest import skip

import pytest

from .utils import check


@skip
def test_inv():
    check("arithm", "inv(8, 17)", 15)


@pytest.mark.skip(reason="Tuple unpacking in assignment not yet supported")
def test_pgcd():
    check("arithm", "pgcd(12, 18)", 6)


@pytest.mark.skip(reason="Tuple unpacking in assignment not yet supported")
def test_binom():
    check("arithm", "binom(4, 2)", 6)


@skip
def test_binom_modulo():
    check("arithm", "binom_modulo(5, 2, 3)", 1)
