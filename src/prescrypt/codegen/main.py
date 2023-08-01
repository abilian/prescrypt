from __future__ import annotations

import re
from functools import singledispatch
from typing import Iterator

from devtools import debug

from prescrypt.ast import ast
from prescrypt.constants import RETURNING_BOOL
from prescrypt.exceptions import JSError
from prescrypt.passes.scope import Scope
from prescrypt.stdlib_js import FUNCTION_PREFIX, METHOD_PREFIX

from .utils import flatten, unify


@singledispatch
def gen_expr(node: ast.expr, gen: CodeGen) -> str | None:
    raise NotImplementedError(f"gen_expr not implemented for {node!r}")


@singledispatch
def gen_stmt(node: ast.stmt, gen: CodeGen) -> str:
    raise NotImplementedError(f"gen_stmt not implemented for {node!r}")


class CodeGen:
    module: ast.Module
    scope: Scope
    ns: NameSpace

    def __init__(self, module: ast.Module, scope: Scope):
        self.module = module
        self.scope = scope
        self._stack = []
        self.push_ns("module", "module")

        assert isinstance(self.module, ast.Module)

        self._indent = 0
        self._dummy_counter = 0

        self._pscript_overload = False
        self._methods = {}
        self._functions = {}
        self._seen_func_names = set()
        self._seen_class_names = set()
        self._std_methods = set()

        self._init_dispatch()

    #
    # Deferred initialization of dispatched functions
    #
    def _init_dispatch(self):
        import prescrypt.codegen._expressions  # noqa: F401
        import prescrypt.codegen._statements  # noqa: F401

    # Modules are not statements
    def gen(self):
        """Main entry point for code generation."""
        statements = self.module.body
        code = []
        for statement in statements:
            code += [self.gen_stmt(statement)]

        return flatten(code, sep="\n")

    def gen_expr(self, node: ast.expr):
        return gen_expr(node, self)

    def gen_stmt(self, node: ast.stmt):
        return gen_stmt(node, self)

    #
    # Output control
    #
    def indent(self):
        """Increase indentation."""
        self._indent += 1

    def dedent(self):
        """Decrease indentation."""
        self._indent -= 1

    def lf(self, code=""):
        """Line feed - create a new line with the correct indentation."""
        return "\n" + self._indent * "    " + code

    #
    # Stdlib
    #
    def call_std_function(self, name: str, args: list[str | ast.expr]) -> str:
        """Generate a function call from the Prescrypt standard library."""
        mangled_name = FUNCTION_PREFIX + name
        return f"{mangled_name}({', '.join(self.gen_js_args(args))})"

    def call_std_method(self, base, name: str, args: list) -> str:
        """Generate a method call from the Prescrypt standard library."""
        mangled_name = METHOD_PREFIX + name
        js_args = list(self.gen_js_args(args))
        # FIXME: what does this do?
        # args.insert(0, base)
        return f"{mangled_name}.call({', '.join(js_args)})"

    def gen_js_args(self, args) -> Iterator[str]:
        for arg in args:
            if isinstance(arg, str):
                yield arg
            else:
                debug(arg, self.gen_expr(arg))
                yield unify(self.gen_expr(arg))

    #
    # Utility functions
    #
    def gen_truthy(self, node: ast.expr) -> str | list:
        """Wraps an operation in a truthy call, unless it's not necessary."""
        eq_name = FUNCTION_PREFIX + "op_equals"
        test = flatten(self.gen_expr(node))
        if (
            test.endswith(".length")
            or test.startswith("!")
            or test.isnumeric()
            or test == "true"
            or test == "false"
            or test.count("==")
            or test.count(">")
            or test.count("<")
            or test.count(eq_name)
            or test == '"this_is_js()"'
            or test.startswith("Array.isArray(")
            or (test.startswith(RETURNING_BOOL) and "||" not in test)
        ):
            return unify(test)
        else:
            return self.call_std_function("truthy", [test])

    def _format_string(self, left: ast.expr, right: ast.expr) -> str:
        """Format a string using the old-school `%` operator."""

        # Get value_nodes
        if isinstance(right, (ast.Tuple, ast.List)):
            value_nodes = right.elts
        else:
            value_nodes = [right]

        # Is the left side a string? If not, exit early
        # This works, but we cannot know whether the left was a string or number :P
        # if not isinstance(node.left_node, ast.Str):
        #     thestring = unify(self.parse(node.left_node))
        #     thestring += ".replace(/%([0-9\.\+\-\#]*[srdeEfgGioxXc])/g, '{:$1}')"
        #     return self.use_std_method(thestring, 'format', value_nodes)

        assert isinstance(left, ast.Constant) and isinstance(left.value, str)
        js_left = "".join(self.gen_expr(left))
        sep, js_left = js_left[0], js_left[1:-1]

        # Get matches
        matches = list(re.finditer(r"%[0-9.+#-]*[srdeEfgGioxXc]", js_left))
        if len(matches) != len(value_nodes):
            raise JSError(
                "In string formatting, number of placeholders "
                "does not match number of replacements"
            )
        # Format
        parts = []
        start = 0
        for m in matches:
            fmt = m.group(0)
            fmt = {"%r": "!r", "%s": ""}.get(fmt, ":" + fmt[1:])
            # Add the part in front of the match (and after prev match)
            parts.append(left[start : m.start()])
            parts.append(f"{fmt}")
            start = m.end()
        parts.append(left[start:])
        thestring = sep + flatten(parts) + sep

        return self.call_std_method(thestring, "format", value_nodes)

    def dummy(self, name=""):
        """Get a unique name.

        The name is added to vars.
        """
        self._dummy_counter += 1
        name = f"_pytmp_{self._dummy_counter:d}_{name}"
        self.add_var(name)
        return name

    #
    # Namespace management
    #
    def add_var(self, var):
        """Add a variable to the current scope."""
        self.ns.add(var)

    def with_prefix(self, name, new=False):
        """Add class prefix to a variable name if necessary."""
        if self.ns.type == "class":
            ns_name = self.ns.name
            if name.startswith("__") and not name.endswith("__"):
                name = "_" + ns_name + name  # Double underscore name mangling
            return ns_name + ".prototype." + name

        else:
            return name

    def push_ns(self, type, name):
        """Push new namespace on stack.

        Match a call to this with a call to pop_ns() and process the
        resulting line to declare the used variables.
        `type` must be 'module', 'class' or 'function'.
        """
        assert type in ("module", "class", "function")
        new_ns = NameSpace(type, name)
        self._stack.append(new_ns)
        self.ns = new_ns

    def pop_ns(self):
        self.ns = self._stack.pop()


class NameSpace:
    def __init__(self, type, name):
        self.type = type
        self.name = name
        self._vars = set()

    def add(self, var):
        self._vars.add(var)

    def is_known(self, var):
        return var in self._vars
