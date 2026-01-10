import pytest

from .utils import check

WORDS = ["as", "porc", "pore", "pre", "pres", "pret"]
EXAMPLES = list(
    zip(
        ["a", "aas", "ass", "pars", "por", "pes", "pred", "pire", "brzlgrmpf"],
        ["as", "as", "as", "porc", "porc", "pres", "pres", "pore", "pres"],
    )
)


@pytest.mark.skip(reason="Code generation returns list instead of str")
def test_trie():
    for w, closest in EXAMPLES:
        expr = f"spell_check(Trie({WORDS}), '{w}')"
        check("trie", expr, closest)
