from pathlib import Path

from .ast import ast
from .codegen import CodeGen
from .passes.desugar import desugar
from .passes.scope import get_top_scope


class Compiler:
    def compile(self, source: str, include_stdlib=True) -> str:
        tree = ast.parse(source)
        tree = desugar(tree)
        top_scope = get_top_scope(tree)
        codegen = CodeGen(tree, top_scope)
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
