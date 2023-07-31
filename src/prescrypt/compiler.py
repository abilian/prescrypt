# from pathlib import Path
# from typing import cast
#
# from .ast import ast
# # from .codegen import gen_module
# # from .codegen.context import Context
# from .passes.desugar import desugar
# from .passes.scope import get_top_scope
# from .stmt_compiler import StatementCompiler
# from .utils import flatten
#
#
# # Temp compiler class
# # class Compiler(StatementCompiler):
# #     def compile(self, statement: str) -> str:
# #         tree = ast.parse(statement)
# #         tree = cast(ast.Module, desugar(tree))
# #
# #         scope = get_top_scope(tree)
# #         ctx = Context(scope)
# #
# #         js_code = flatten(gen_module(tree, scope))
# #         full_code = self.get_preamble() + "\n" + js_code
# #         return full_code
# #
# #     def get_preamble(self) -> str:
# #         stdlib_js = Path(__file__).parent / "stdlibjs"
# #         preamble_js = (stdlib_js / "_stdlib.js").read_text()
# #         return preamble_js
# #
# #
# # def py2js(code) -> str:
# #     compiler = Compiler()
# #     return compiler.compile(code)
