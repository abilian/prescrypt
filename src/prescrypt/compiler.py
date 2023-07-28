from pathlib import Path
from typing import cast

from .ast import ast
from .passes.desugar import desugar
from .stmt_compiler import StatementCompiler
from .utils import flatten


# Temp compiler class
class Compiler(StatementCompiler):
    def compile(self, statement: str) -> str:
        tree = ast.parse(statement)
        tree = cast(ast.Module, desugar(tree))
        js_code = flatten(self.gen_module(tree))
        full_code = self.get_preamble() + "\n" + js_code
        return full_code

    # def compile(self, expression: str) -> str:
    #     tree = ast.parse(expression)
    #     assert isinstance(tree, ast.Module)
    #     # tree = cast(ast.Module, desugar(tree))
    #     expr = cast(ast.expr, tree.body[0].value)
    #     js_code = self.gen_expr(expr)
    #     return flatten(js_code)

    def get_preamble(self) -> str:
        stdlib_js = Path(__file__).parent / "stdlibjs"
        preamble_js = (stdlib_js / "_stdlib.js").read_text()
        return preamble_js


def py2js(code) -> str:
    compiler = Compiler()
    return compiler.compile(code)
