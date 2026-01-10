from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from prescrypt.compiler import py2js

PROGRAMS_DIR = Path(__file__).parent / "programs"


def get_source_files():
    for src in PROGRAMS_DIR.glob("*.py"):
        if src.name.startswith("test_"):
            continue
        yield str(src.name)


@pytest.mark.parametrize("source_file", get_source_files())
def test_module(source_file):
    if source_file == "class.py":
        pytest.skip("Class codegen needs fixes")

    src = PROGRAMS_DIR / source_file
    dst = src.with_suffix(".js")

    js_code = py2js(src.read_text())
    dst.write_text(js_code)

    # NB: we assume the python script is always correct
    p1 = subprocess.run(["python", str(src)], stdout=subprocess.PIPE, check=True)
    p2 = subprocess.run(["node", str(dst)], stdout=subprocess.PIPE)

    stdout1 = p1.stdout.decode("utf-8")
    stdout2 = p2.stdout.decode("utf-8")

    if p2.returncode != 0 or stdout1 != stdout2:
        print()
        print()
        print("node result:", stdout1)
        print("python result", stdout2)
        print()
        print("source:", py2js(src.read_text(), include_stdlib=False), sep="\n")

    assert p2.returncode == 0 and stdout1 == stdout2

    os.unlink(dst)
