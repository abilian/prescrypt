from __future__ import annotations

from pathlib import Path

import pytest

from prescrypt import py2js
from prescrypt.testing import js_eval

DENY_LIST = {
    "__init__",
    "arithm_expr_eval",
    "closest_values",
    "fft",
    "gauss_jordan",
    "graph",
    "kuhn_munkres",
    "kuhn_munkres_n4",
    "longest_common_subsequence",
    "majority",
    "manacher",
    "matrix_chain_mult",
    "next_permutation",
    "our_heap",
    "our_queue",
    "partition_refinement",
    "scalar",
    "strongly_connected_components",
    "subsetsum_divide",
    "windows_k_distinct",
}


def get_files():
    files = sorted((Path(__file__).parent / "tryalgo").glob("*.py"))
    for path in files:
        code = path.read_text()
        if " import " in code:
            continue
        if path.stem in DENY_LIST:
            continue
        yield path.name


FILES = list(get_files())


@pytest.mark.parametrize("name", FILES)
def test_program_compiles(name):
    path = Path(__file__).parent / "tryalgo" / name
    code = Path(path).read_text()

    jscode = py2js(code)
    assert jscode != ""


@pytest.mark.parametrize("name", FILES)
def test_program_evaluates(name):
    if name in {"dancing_links.py", "fenwick.py", "trie.py"}:
        return

    path = Path(__file__).parent / "tryalgo" / name
    code = Path(path).read_text()

    js_result = js_eval(py2js(code))
    assert js_result != ""
