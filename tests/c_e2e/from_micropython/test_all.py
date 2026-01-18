from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from prescrypt.compiler import py2js

from .denylist import DENY_LIST

PROGRAMS_DIR = Path(__file__).parent / "programs"


def get_source_files():
    for src in sorted(PROGRAMS_DIR.glob("*.py")):
        if src.name in DENY_LIST:
            continue
        yield str(src.name)


@pytest.mark.parametrize("source_file", get_source_files())
def test_module(source_file):
    assert source_file not in DENY_LIST
    src = PROGRAMS_DIR / source_file
    js_code = py2js(src.read_text())

    dst = (Path(tempfile.gettempdir()) / src.name).with_suffix(".js")
    dst.write_text(js_code)

    try:
        p1 = subprocess.run(["node", str(dst)], stdout=subprocess.PIPE, check=True)
        p2 = subprocess.run(["python", str(src)], stdout=subprocess.PIPE, check=True)

        stdout1 = p1.stdout.decode("utf-8").strip()
        stdout2 = p2.stdout.decode("utf-8").strip()

        if stdout1 != stdout2:
            print()
            print()
            print("node result:", stdout1)
            print("python result", stdout2)
            print()
            print(py2js(src.read_text(), include_stdlib=False))

        assert stdout1 == stdout2
    finally:
        os.unlink(dst)
