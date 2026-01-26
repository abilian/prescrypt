from __future__ import annotations

from .utils import check


def test_inv():
    check("arithm", "inv(8, 17)", 15)


def test_pgcd():
    check("arithm", "pgcd(12, 18)", 6)


def test_binom():
    check("arithm", "binom(4, 2)", 6)


def test_binom_modulo():
    check("arithm", "binom_modulo(5, 2, 3)", 1)
