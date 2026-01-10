from __future__ import annotations

from textwrap import dedent

from prescrypt.front import ast

from prescrypt.codegen.main import CodeGen, gen_stmt
from prescrypt.codegen.utils import flatten


@gen_stmt.register
def gen_functiondef(node: ast.FunctionDef, codegen: CodeGen):
    fun_def = FunDef(node, codegen)
    return fun_def.gen()


# FIXME: should accept an expr.
@gen_stmt.register
def gen_lambda(node: ast.Lambda, codegen: CodeGen):
    fun_def = LambdaDef(node, codegen)
    return fun_def.gen()


@gen_stmt.register
def gen_asyncfunctiondef(node: ast.AsyncFunctionDef, codegen: CodeGen):
    fun_def = AsyncFunDef(node, codegen)
    return fun_def.gen()


@gen_stmt.register
def gen_return(node: ast.Return, codegen: CodeGen):
    if node.value is None:
        return codegen.lf("return null;")
    else:
        js_return_value = flatten(codegen.gen_expr(node.value))
        return codegen.lf(f"return {js_return_value};")


class BaseFunDef:
    _async = ""

    def __init__(self, node: ast.AST, codegen: CodeGen):
        assert isinstance(node, (ast.FunctionDef, ast.Lambda, ast.AsyncFunctionDef))
        self.node = node
        self.codegen = codegen

    def gen(self):
        name = self.node.name
        js_args = self.gen_args()
        js_body = self.gen_body()

        args = self.node.args.args
        has_self = args and args[0].arg in ("self", "this")
        _async = self._async
        if self.codegen.ns.type == "function" and not has_self:
            return dedent(
                f"""
                ({_async}function {name}({js_args}) {{
                {js_body}
                }}).bind(this)
                """
            )

        else:
            return dedent(
                f"""
                {_async}function {name}({js_args}) {{
                {js_body}
                }}
                """
            )

    def gen_args(self):
        # args_node is an ast.arguments node, with attributes:
        # - posonlyargs: list[arg]
        # - args: list[arg]
        # - vararg: None | arg
        # - kwonlyargs: list[arg]
        # - kw_defaults: list[None] | list[expr]
        # - kwarg: None | arg
        # - defaults: list[expr]

        args = self.node.args.args
        code = []

        # Collect args
        argnames = []
        for arg in args:
            name = arg.arg
            if name == "self":
                name = "this"
            if name != "this":
                argnames.append(name)
                # Add code and comma
                code.append(name)
                code.append(", ")
        if argnames:
            code.pop(-1)  # pop last comma
        return "".join(code)

    def gen_body(self):
        code = []
        for child in self.node.body:
            code += [self.codegen.gen_stmt(child)]
        return "\n".join(code)


class FunDef(BaseFunDef):
    def __init__(self, node: ast.FunctionDef, codegen: CodeGen):
        super().__init__(node, codegen)


class AsyncFunDef(BaseFunDef):
    _async = "async "

    def __init__(self, node: ast.AsyncFunctionDef, codegen: CodeGen):
        super().__init__(node, codegen)


class LambdaDef(BaseFunDef):
    def __init__(self, node: ast.Lambda, codegen: CodeGen):
        super().__init__(node, codegen)
