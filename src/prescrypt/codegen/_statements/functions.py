from __future__ import annotations

from textwrap import dedent

from prescrypt.codegen.main import CodeGen, gen_stmt
from prescrypt.codegen.utils import flatten
from prescrypt.front import ast


def _is_generator_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Check if function contains yield/yield from (making it a generator).

    Only checks direct children, not nested functions/classes.
    """

    class YieldFinder(ast.NodeVisitor):
        def __init__(self):
            self.has_yield = False

        def visit_Yield(self, node):
            self.has_yield = True

        def visit_YieldFrom(self, node):
            self.has_yield = True

        # Don't descend into nested functions/classes
        def visit_FunctionDef(self, node):
            pass

        def visit_AsyncFunctionDef(self, node):
            pass

        def visit_ClassDef(self, node):
            pass

    finder = YieldFinder()
    for stmt in node.body:
        finder.visit(stmt)
    return finder.has_yield


@gen_stmt.register
def gen_functiondef(node: ast.FunctionDef, codegen: CodeGen):
    fun_def = FunDef(node, codegen)
    return fun_def.gen()


@gen_stmt.register
def gen_asyncfunctiondef(node: ast.AsyncFunctionDef, codegen: CodeGen):
    fun_def = AsyncFunDef(node, codegen)
    return fun_def.gen()


class BaseFunDef:
    _async = ""

    def __init__(self, node: ast.AST, codegen: CodeGen):
        assert isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        self.node = node
        self.codegen = codegen
        self._is_generator = _is_generator_function(node)

    @property
    def _func_keyword(self) -> str:
        """Return 'function' or 'function*' depending on generator status."""
        if self._is_generator:
            return f"{self._async}function*"
        return f"{self._async}function"

    def gen(self):
        name = self.node.name
        _func = self._func_keyword

        # Check for special decorators
        decorator_type = self._get_decorator_type()

        if self.codegen.ns.type == "class":
            return self._gen_class_method(name, _func, decorator_type)
        elif self.codegen.ns.type == "function":
            return self._gen_nested_function(name, _func)
        else:
            return self._gen_module_function(name, _func)

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

    def _gen_class_method(self, name: str, _func: str, decorator_type: str | None):
        """Generate a method inside a class."""
        class_name = self.codegen.ns.name

        if decorator_type == "staticmethod":
            # Static method: attach to both constructor and prototype
            # Don't convert first param, mark as nobind
            js_args = self._gen_args_no_self_conversion()
            js_body = self.gen_body()
            return dedent(
                f"""
                {class_name}.{name} = {class_name}.prototype.{name} = {_func} ({js_args}) {{
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
                {class_name}.{name} = {class_name}.prototype.{name} = {_func} ({js_args}) {{
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
                {full_name} = {_func} ({js_args}) {{
                {js_body}
                }};
                """
            )

    def _gen_nested_function(self, name: str, _func: str):
        """Generate a nested function inside another function."""
        args = self.node.args.args
        has_self = args and args[0].arg in ("self", "this")

        if not has_self:
            # Bind to parent's this
            # Note: generators cannot use .bind(), so we skip binding for generators
            js_args = self.gen_args()
            js_body = self.gen_body()
            self.codegen.add_var(name)
            if self._is_generator:
                # Generators don't need binding since they create their own context
                return dedent(
                    f"""
                    let {name} = {_func} {name}({js_args}) {{
                    {js_body}
                    }};
                    """
                )
            else:
                return dedent(
                    f"""
                    let {name} = ({_func} {name}({js_args}) {{
                    {js_body}
                    }}).bind(this);
                    """
                )
        else:
            js_args = self.gen_args()
            js_body = self.gen_body()
            return dedent(
                f"""
                {_func} {name}({js_args}) {{
                {js_body}
                }}
                """
            )

    def _gen_module_function(self, name: str, _func: str):
        """Generate a module-level function."""
        js_args = self.gen_args()
        js_body = self.gen_body()
        export_prefix = "export " if self.codegen.should_export() else ""

        # Generate function definition
        func_def = dedent(
            f"""
            {export_prefix}{_func} {name}({js_args}) {{
            {js_body}
            }}
            """
        )

        # Apply decorators (in reverse order, innermost first)
        decorators = getattr(self.node, "decorator_list", [])
        if decorators:
            # Filter out staticmethod/classmethod which are only for class methods
            applicable = [
                d
                for d in decorators
                if not (
                    isinstance(d, ast.Name) and d.id in ("staticmethod", "classmethod")
                )
            ]
            if applicable:
                code = [func_def]
                # Apply decorators in reverse order
                for dec in reversed(applicable):
                    dec_name = flatten(self.codegen.gen_expr(dec))
                    code.append(f"{name} = {dec_name}({name});\n")
                return "".join(code)

        return func_def

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

        args_node = self.node.args
        args = args_node.args
        code = []

        # Calculate default value positions
        num_defaults = len(args_node.defaults)
        num_args = len(args)

        # Collect args
        argnames = []
        for i, arg in enumerate(args):
            name = arg.arg
            if name == "self":
                name = "this"
            if name != "this":
                argnames.append(name)
                # Check for default value
                default_idx = i - (num_args - num_defaults)
                if default_idx >= 0:
                    default = flatten(
                        self.codegen.gen_expr(args_node.defaults[default_idx])
                    )
                    code.append(f"{name} = {default}")
                else:
                    code.append(name)
                code.append(", ")

        # Handle *args (vararg) - convert to JS rest parameter
        if args_node.vararg:
            vararg_name = args_node.vararg.arg
            code.append(f"...{vararg_name}")
            code.append(", ")

        if code and code[-1] == ", ":
            code.pop(-1)  # pop last comma
        return "".join(code)

    def gen_body(self):
        # Push function namespace to isolate local variables
        self.codegen.push_ns("function", self.node.name)

        # Register function parameters in the namespace so they're recognized as defined
        args_node = self.node.args
        for arg in args_node.args:
            name = arg.arg
            if name not in ("self", "this"):
                self.codegen.add_var(name)
        # Also register *args parameter if present
        if args_node.vararg:
            self.codegen.add_var(args_node.vararg.arg)

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
