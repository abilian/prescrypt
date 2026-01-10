from __future__ import annotations

from pathlib import Path

from .codegen import CodeGen
from .front import ast
from .front.passes.desugar import desugar


class Compiler:
    def compile(self, source: str, include_stdlib=True) -> str:
        tree = ast.parse(source)
        tree = desugar(tree)
        codegen = CodeGen(tree)
        js_code = codegen.gen()
        if not include_stdlib:
            return js_code
        else:
            full_code = self.get_preamble() + "\n" + js_code
            return full_code

    def get_preamble(self) -> str:
        stdlib_js = Path(__file__).parent / "stdlibjs"
        preamble_js = (stdlib_js / "_stdlib.js").read_text()
        return preamble_js


def py2js(code, include_stdlib=True) -> str:
    compiler = Compiler()
    return compiler.compile(code, include_stdlib=include_stdlib)
