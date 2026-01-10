from unittest import skip

import pytest

from .utils import check


def unorder(L):
    return sorted(sorted(group) for group in L)


EXAMPLES = [
    (
        "le chien marche vers sa niche et trouve une "
        "limace de chine nue pleine de malice "
        "qui lui fait du charme".split(),
        [
            ["nue", "une"],
            ["limace", "malice"],
            ["marche", "charme"],
            ["chien", "niche", "chine"],
        ],
    ),
    (["aba", "baa", "abb"], [["aba", "baa"]]),
    (["aba"], []),
    ([], []),
]


@skip
@pytest.mark.parametrize("words, res", EXAMPLES)
def test_anagrams(words, res):
    words = list(words)
    check("anagrams", f"anagrams({words})", unorder(res))
