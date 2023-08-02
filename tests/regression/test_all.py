import os
import subprocess
from pathlib import Path

import pytest

from prescrypt.compiler import py2js


def get_source_files():
    parent_dir = Path(__file__).parent
    for src in parent_dir.glob("*.py"):
        if src.name.startswith("test_"):
            continue
        yield str(src.name)


@pytest.mark.parametrize("source_file", get_source_files())
def test_module(source_file):
    src = Path(__file__).parent / source_file
    dst = src.with_suffix(".js")

    js_code = py2js(src.read_text())
    dst.write_text(js_code)

    p1 = subprocess.Popen(["node", dst], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["python", src], stdout=subprocess.PIPE)
    stdout1, _ = p1.communicate()
    stdout2, _ = p2.communicate()
    if stdout1 != stdout2:
        print()
        print()
        print("node result:", stdout1)
        print("python result", stdout2)
    assert stdout1 == stdout2

    os.unlink(dst)
