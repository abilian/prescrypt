from __future__ import annotations

from ..symbol import Symbol


def test_symbols():
    sym_a = Symbol("a")
    sym_b = Symbol("b")

    assert sym_a == sym_a
    assert sym_a != sym_b

    assert sym_a.name == "a"
    assert sym_b.name == "b"

    assert sym_a.definition is None
    assert sym_b.definition is None

    assert str(sym_a) == "a"
    assert str(sym_b) == "b"
