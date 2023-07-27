import sys
from pathlib import Path

from .compiler import py2js


def main():
    src_path = Path(sys.argv[1])
    src = src_path.read_text()
    dst = py2js(src).strip()
    dst_path = src_path.with_suffix(".js")
    dst_path.write_text(dst)
