from __future__ import annotations

from textwrap import dedent

from prescrypt.codegen.main import CodeGen, gen_stmt
from prescrypt.codegen.utils import flatten
from prescrypt.front import ast


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




class BaseFunDef:
    _async = ""

    def __init__(self, node: ast.AST, codegen: CodeGen):
        assert isinstance(node, (ast.FunctionDef, ast.Lambda, ast.AsyncFunctionDef))
        self.node = node
        self.codegen = codegen

    def gen(self):
        name = self.node.name
        _async = self._async

        # Check for special decorators
        decorator_type = self._get_decorator_type()

        if self.codegen.ns.type == "class":
            return self._gen_class_method(name, _async, decorator_type)
        elif self.codegen.ns.type == "function":
            return self._gen_nested_function(name, _async)
        else:
            return self._gen_module_function(name, _async)

    def _get_decorator_type(self) -> str | None:
        """Check for @staticmethod or @classmethod decorators."""
        decorators = getattr(self.node, "decorator_list", [])
        for dec in decorators:
            if isinstance(dec, ast.Name):
                if dec.id == "staticmethod":
                    return "staticmethod"
                elif dec.id == "classmethod":
                    return "classmethod"
        return None

    def _gen_class_method(self, name: str, _async: str, decorator_type: str | None):
        """Generate a method inside a class."""
        class_name = self.codegen.ns.name

        if decorator_type == "staticmethod":
            # Static method: attach to both constructor and prototype
            # Don't convert first param, mark as nobind
            js_args = self._gen_args_no_self_conversion()
            js_body = self.gen_body()
            return dedent(
                f"""
                {class_name}.{name} = {class_name}.prototype.{name} = {_async}function ({js_args}) {{
                {js_body}
                }};
                {class_name}.{name}.nobind = true;
                {class_name}.prototype.{name}.nobind = true;
                """
            )
        elif decorator_type == "classmethod":
            # Class method: first param is cls (the constructor's prototype)
            # Put on both constructor and prototype so it works either way
            js_args = self._gen_args_cls_to_name(class_name)
            js_body = self.gen_body()
            return dedent(
                f"""
                {class_name}.{name} = {class_name}.prototype.{name} = {_async}function ({js_args}) {{
                let cls = {class_name}.prototype;
                {js_body}
                }};
                """
            )
        else:
            # Regular method
            js_args = self.gen_args()
            js_body = self.gen_body()
            full_name = self.codegen.with_prefix(name)
            return dedent(
                f"""
                {full_name} = {_async}function ({js_args}) {{
                {js_body}
                }};
                """
            )

    def _gen_nested_function(self, name: str, _async: str):
        """Generate a nested function inside another function."""
        args = self.node.args.args
        has_self = args and args[0].arg in ("self", "this")

        if not has_self:
            # Bind to parent's this
            js_args = self.gen_args()
            js_body = self.gen_body()
            self.codegen.add_var(name)
            return dedent(
                f"""
                let {name} = ({_async}function {name}({js_args}) {{
                {js_body}
                }}).bind(this);
                """
            )
        else:
            js_args = self.gen_args()
            js_body = self.gen_body()
            return dedent(
                f"""
                {_async}function {name}({js_args}) {{
                {js_body}
                }}
                """
            )

    def _gen_module_function(self, name: str, _async: str):
        """Generate a module-level function."""
        js_args = self.gen_args()
        js_body = self.gen_body()
        return dedent(
            f"""
            {_async}function {name}({js_args}) {{
            {js_body}
            }}
            """
        )

    def _gen_args_no_self_conversion(self) -> str:
        """Generate args without self→this conversion (for staticmethod)."""
        args = self.node.args.args
        code = []
        for arg in args:
            name = arg.arg
            code.append(name)
            code.append(", ")
        if code:
            code.pop(-1)  # pop last comma
        return "".join(code)

    def _gen_args_cls_to_name(self, class_name: str) -> str:
        """Generate args, skipping cls parameter (for classmethod)."""
        args = self.node.args.args
        code = []
        for i, arg in enumerate(args):
            name = arg.arg
            if i == 0 and name == "cls":
                # Skip cls - we'll inject it as a local variable
                continue
            code.append(name)
            code.append(", ")
        if code and code[-1] == ", ":
            code.pop(-1)  # pop last comma
        return "".join(code)

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
        # Push function namespace to isolate local variables
        self.codegen.push_ns("function", self.node.name)

        # Use function's binding scope for variable declarations
        old_binding_scope = self.codegen._binding_scope
        self.codegen._binding_scope = getattr(self.node, "_scope", None)

        code = []
        for child in self.node.body:
            result = self.codegen.gen_stmt(child)
            if isinstance(result, list):
                code.append(flatten(result))
            else:
                code.append(result)

        # Restore previous binding scope
        self.codegen._binding_scope = old_binding_scope
        self.codegen.pop_ns()
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
