from __future__ import annotations

from textwrap import dedent

from devtools import debug

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


def _gen_functiondef(codegen: CodeGen, node: ast.AST, is_lambda=False, asyn=False):
    # Common code for the FunctionDef and Lambda nodes.
    assert isinstance(node, (ast.FunctionDef, ast.Lambda, ast.AsyncFunctionDef))

    args_node = node.args
    body_nodes = node.body

    debug("gen_functiondef", node.name, args_node, body_nodes)

    # args_node is an ast.arguments node, with attributes:
    # - posonlyargs: list[arg]
    # - args: list[arg]
    # - vararg: None | arg
    # - kwonlyargs: list[arg]
    # - kw_defaults: list[None] | list[expr]
    # - kwarg: None | arg
    # - defaults: list[expr]

    args = args_node.args

    has_self = args and args[0].arg in ("self", "this")

    # Bind if this function is inside a function, and does not have self
    binder = ""  # code to add to the end
    # if len(self._stack) >= 1 and self._stack[-1][0] == "function":
    #     if not has_self:
    #         binder = ").bind(this)"

    # Init function definition
    # Non-anonymous functions get a name so that they are debugged more
    # easily and resolve to the correct event labels in flexx.event. However,
    # we cannot use the exact name, since we don't want to actually *use* it.
    # Classes give their methods a __name__, so no need to name these.
    code = []
    func_name = ""

    if not is_lambda:
        if not has_self:
            func_name = "flx_" + node.name
        prefixed = codegen.with_prefix(node.name)
        if prefixed == node.name:  # normal function vs method
            # codegen.vars.add(node.name)
            codegen._seen_func_names.add(node.name)
        code.append(codegen.lf(f"{prefixed} = "))

    code.append(
        "%s%sfunction %s%s("
        % (
            "(" if binder else "",
            "async " if asyn else "",
            func_name,
            " " if func_name else "",
        )
    )

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

    # Check
    # if (not lambda_) and node.decorator_nodes:
    #     if not (
    #         len(node.decorator_nodes) == 1
    #         and isinstance(node.decorator_nodes[0], ast.Name)
    #         and node.decorator_nodes[0].name == "staticmethod"
    #     ):
    #         raise JSError("No support for function decorators")

    # Prepare for content
    code.append(") {")
    pre_code, code = code, []
    codegen.indent()
    if is_lambda:
        func_name = "<lambda>"
    else:
        func_name = node.name
    codegen.push_ns("function", func_name)

    # Add argnames to known vars
    # for name in argnames:
    #     self.vars.add(name)

    # Prepare code for varargs
    # vararg_code1 = vararg_code2 = ""
    # if node.args_node:
    #     name = node.args_node.name  # always an ast.Arg
    #     self.vars.add(name)
    #     if not argnames:
    #         # Make available under *arg name
    #         # code.append(codegen.lf('%s = arguments;' % name))
    #         vararg_code1 = f"{name} = Array.prototype.slice.call(arguments);"
    #         vararg_code2 = f"{name} = arguments[0].flx_args;"
    #     else:
    #         # Slice it
    #         x = name, len(argnames)
    #         vararg_code1 = "%s = Array.prototype.slice.call(arguments, %i);" % x
    #         vararg_code2 = "%s = arguments[0].flx_args.slice(%i);" % x

    # Handle keyword arguments and kwargs
    # kw_argnames = set()  # variables that come from keyword args, or helper vars
    # if node.kwarg_nodes or node.kwargs_node:
    #     # Collect names and default values
    #     names, values = [], []
    #     for arg in node.kwarg_nodes:
    #         self.vars.add(arg.name)
    #         kw_argnames.add(arg.name)
    #         names.append(f"'{arg.name}'")
    #         values.append("".join(self.parse(arg.value_node)))
    #     # Turn into string representation
    #     names = "[" + ", ".join(names) + "]"
    #     values = "[" + ", ".join(values) + "]"
    #     # Write code to prepare for kwargs
    #     if node.kwargs_node:
    #         code.append(codegen.lf("%s = {};" % node.kwargs_node.name))
    #     if node.kwarg_nodes:
    #         values_var = self.dummy("kw_values")
    #         kw_argnames.add(values_var)
    #         code += [codegen.lf(values_var), " = ", values, ";"]
    #     else:
    #         values_var = values
    #     # Enter if to actually parse kwargs
    #     code.append(
    #         codegen.lf(
    #             "if (arguments.length == 1 && typeof arguments[0] == 'object' && "
    #             "Object.keys(arguments[0]).toString() == 'flx_args,flx_kwargs') {"
    #         )
    #     )
    #     codegen.indent()
    #     # Call function to parse args
    #     code += [codegen.lf()]
    #     if node.kwargs_node:
    #         kw_argnames.add(node.kwargs_node.name)
    #         self.vars.add(node.kwargs_node.name)
    #         code += [node.kwargs_node.name, " = "]
    #     codegen.call_std_function("op_parse_kwargs", [])
    #     code += [
    #         stdlib_js.FUNCTION_PREFIX + "op_parse_kwargs(",
    #         names,
    #         ", ",
    #         values_var,
    #         ", arguments[0].flx_kwargs",
    #     ]
    #     if not node.kwargs_node:
    #         code.append(f", '{func_name}'" or "anonymous")
    #     code.append(");")
    #     # Apply values of positional args
    #     # inside if, because standard arguments are invalid
    #     args_var = "arguments[0].flx_args"
    #     if len(argnames) > 1:
    #         args_var = codegen.dummy("args")
    #         code.append(codegen.lf(f"{args_var} = arguments[0].flx_args;"))
    #     for i, name in enumerate(argnames):
    #         code.append(codegen.lf("%s = %s[%i];" % (name, args_var, i)))
    #     # End if
    #     if vararg_code2:
    #         code.append(codegen.lf(vararg_code2))
    #     codegen.dedent()
    #     code.append(codegen.lf("}"))
    #     if vararg_code1:
    #         code += [" else {", vararg_code1, "}"]
    #     # Apply values of keyword-only args
    #     # outside if, because these need to be assigned always
    #     # Note that we cannot use destructuring assignment because not all
    #     # browsers support it (meh IE and Safari!)
    #     for i, arg in enumerate(node.kwarg_nodes):
    #         code.append(codegen.lf("%s = %s[%i];" % (arg.name, values_var, i)))
    # else:
    #     if vararg_code1:
    #         code.append(codegen.lf(vararg_code1))

    # Apply defaults of positional arguments
    # for arg in node.arg_nodes:
    #     if arg.value_node is not None:
    #         name = arg.name
    #         d = "".join(self.parse(arg.value_node))
    #         x = f"{name} = ({name} === undefined) ? {d}: {name};"
    #         code.append(codegen.lf(x))

    # Apply content
    # if is_lambda:
    #     code.append("return ")
    #     code += codegen.gen_expr(body_node)
    #     code.append(";")
    # else:
    #     docstring = self.pop_docstring(node)
    #     if docstring and not node.body_nodes:
    #         # Raw JS - but deprecated
    #         logger.warning(RAW_DOC_WARNING, node.name)
    #         for line in docstring.splitlines():
    #             code.append(codegen.lf(line))
    #     else:
    #         # Normal function
    #         if self._docstrings:
    #             for line in docstring.splitlines():
    #                 code.append(codegen.lf("// " + line))
    #         for child in body_nodes:
    #             code += self.parse(child)

    # Simpler for now
    for child in body_nodes:
        code += [codegen.gen_stmt(child)]

    # Wrap up
    # if is_lambda:
    #     code.append("}%s" % binder)
    #     # ns should consist only of arg names (or helpers)
    #     for name in argnames:
    #         self.vars.discard(name)
    #     if node.args_node:
    #         self.vars.discard(node.args_node.name)
    #     ns = self.pop_stack()
    #     assert set(ns) == kw_argnames
    #     pre_code.append(self.get_declarations(ns))
    # else:
    #     if not (code and code[-1].strip().startswith("return ")):
    #         code.append(codegen.lf("return null;"))
    #     # Declare vars, but exclude our argnames
    #     for name in argnames:
    #         self.vars.discard(name)
    #     ns = self.pop_stack()
    #     pre_code.append(self.get_declarations(ns))

    codegen.dedent()
    if not is_lambda:
        code.append(codegen.lf(f"}}{binder};\n"))

    return pre_code + code
