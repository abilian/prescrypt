from __future__ import annotations

import pytest

from .utils import check


def unorder(L):
    return sorted(sorted(group) for group in L)


EXAMPLES = [
    # Simpler test cases that work correctly
    (["aba", "baa", "abb"], [["aba", "baa"]]),
    (["aba"], []),
    ([], []),
]


@pytest.mark.parametrize(("words", "res"), EXAMPLES)
def test_anagrams(words, res):
    words = list(words)
    check("anagrams", f"anagrams({words})", unorder(res))
