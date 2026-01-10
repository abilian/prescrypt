from pathlib import Path
from unittest import skip

import dukpy
import pytest

from prescrypt import py2js


def get_files():
    files = sorted((Path(__file__).parent / "tryalgo").glob("*.py"))
    for path in files:
        code = path.read_text()
        if " import " in code:
            continue
        yield path.name


FILES = list(get_files())


@skip
@pytest.mark.parametrize("name", FILES)
def test_program_compiles(name):
    path = Path(__file__).parent / "tryalgo" / name
    code = Path(path).read_text()

    jscode = py2js(code)


@pytest.mark.skip(reason="Tryalgo programs need various codegen fixes")
@pytest.mark.parametrize("name", FILES)
def test_program_evaluates(name):
    path = Path(__file__).parent / "tryalgo" / name
    code = Path(path).read_text()

    try:
        jscode = py2js(code)
    except:
        return

    js_result = dukpy.evaljs(jscode)
