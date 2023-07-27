import ast
import sys
from pathlib import Path
from typing import cast

from prescrypt.expr_compiler import ExpressionCompiler
from prescrypt.passes.desugar import desugar
from prescrypt.utils import flatten


# Temp compiler class
class Compiler(ExpressionCompiler):

    def gen_stmt(self, node) -> str:
        """Not needed"""

    def compile(self, expression: str) -> str:
        tree = ast.parse(expression)
        tree = cast(ast.Module, desugar(tree))
        expr = cast(ast.expr, tree.body[0].value)
        js_code = self.gen_expr(expr)
        return flatten(js_code)


def py2js(code) -> str:
    compiler = Compiler()
    return compiler.compile(code)


def main():
    src_path = Path(sys.argv[1])
    src = src_path.read_text()
    dst = py2js(src).strip()
    dst_path = src_path.with_suffix(".js")
    dst_path.write_text(dst)
