from __future__ import annotations

import re
from collections.abc import Iterator
from functools import singledispatch
from pathlib import Path
from typing import TYPE_CHECKING

from prescrypt.constants import RETURNING_BOOL
from prescrypt.exceptions import JSError
from prescrypt.front import Scope, ast
from prescrypt.front.passes.resolver import ModuleResolver
from prescrypt.stdlib_js import FUNCTION_PREFIX, METHOD_PREFIX

from .utils import flatten, unify

if TYPE_CHECKING:
    from prescrypt.sourcemap import SourceMapGenerator


@singledispatch
def gen_expr(node: ast.expr, gen: CodeGen) -> str | None:
    msg = f"gen_expr not implemented for {node!r}"
    raise NotImplementedError(msg)


@singledispatch
def gen_stmt(node: ast.stmt, gen: CodeGen) -> str:
    msg = f"gen_stmt not implemented for {node!r}"
    raise NotImplementedError(msg)


class CodeGen:
    module: ast.Module
    ns: NameSpace

    def __init__(
        self,
        module: ast.Module,
        function_prefix: str = FUNCTION_PREFIX,
        method_prefix: str = METHOD_PREFIX,
        module_mode: bool = False,
        source_dir: Path | None = None,
        module_paths: list[Path] | None = None,
        source_map: SourceMapGenerator | None = None,
    ):
        self.module = module
        self._stack = []
        self.push_ns("module", "module")

        assert isinstance(self.module, ast.Module)

        self._indent = 0
        self._dummy_counter = 0

        self._methods = {}
        self._functions = {}

        # Configurable namespace prefixes
        self.function_prefix = function_prefix
        self.method_prefix = method_prefix

        # ES6 module mode - emit exports for module-level definitions
        self.module_mode = module_mode

        # __all__ support - if defined, only export these names
        self._module_all: set[str] | None = self._extract_module_all(module)

        # Module resolution settings
        self._source_dir = source_dir or Path.cwd()
        self._module_paths = module_paths or []

        # Track used stdlib functions/methods for tree-shaking
        self._used_std_functions: set[str] = set()
        self._used_std_methods: set[str] = set()
        self._seen_func_names = set()
        self._seen_class_names = set()
        self._std_methods = set()

        # Track binding scope from Binder (if available)
        self._binding_scope: Scope | None = getattr(module, "_scope", None)

        # Track JS FFI module names (e.g., 'js' or aliases like 'import js as javascript')
        self._js_ffi_names: set[str] = set()

        # Source map generation
        self._source_map = source_map
        self._output_line = 0  # Current line in generated output (0-indexed)

        # Track exception variable for bare raise support
        self._exception_var_stack: list[str] = []

        # Pending variable declarations (for walrus operator in expressions)
        self._pending_declarations: list[str] = []

        self._init_dispatch()

    @property
    def binding_scope(self) -> Scope | None:
        """Get the current binding scope from the Binder pass."""
        return self._binding_scope

    @property
    def used_std_functions(self) -> set[str]:
        """Get the set of stdlib functions used during code generation."""
        return self._used_std_functions

    @property
    def used_std_methods(self) -> set[str]:
        """Get the set of stdlib methods used during code generation."""
        return self._used_std_methods

    def _push_exception_var(self, name: str) -> None:
        """Enter an except block with this exception variable."""
        self._exception_var_stack.append(name)

    def _pop_exception_var(self) -> None:
        """Exit an except block."""
        if self._exception_var_stack:
            self._exception_var_stack.pop()

    def _get_exception_var(self) -> str | None:
        """Get the current exception variable name, if in an except block."""
        return self._exception_var_stack[-1] if self._exception_var_stack else None

    def is_known_in_any_scope(self, name: str) -> bool:
        """Check if a variable is known in any enclosing scope.

        Used for walrus operator to avoid redeclaring variables that
        exist in parent scopes (e.g., module-level variables used in
        comprehensions).
        """
        return any(ns.is_known(name) for ns in self._stack)

    def add_pending_declaration(self, name: str) -> None:
        """Add a variable to be declared before the current statement.

        Used for walrus operator where the variable needs to be declared
        before the expression containing it is evaluated.
        """
        if name not in self._pending_declarations:
            self._pending_declarations.append(name)

    def flush_pending_declarations(self) -> str:
        """Emit and clear any pending variable declarations.

        Returns the declaration statements as a string (may be empty).
        """
        if not self._pending_declarations:
            return ""
        decls = [f"let {name};" for name in self._pending_declarations]
        self._pending_declarations.clear()
        return self.lf("") + self.lf("".join(decls))

    def get_declaration_kind(self, name: str) -> str:
        """Get the JS declaration keyword for a variable.

        Returns "const", "let", or "" (empty for no declaration needed).
        """
        if self._binding_scope is None:
            # No Binder info available, default to "let"
            return "let"

        var = self._binding_scope.vars.get(name)
        if var is None:
            # Variable not found in scope, default to "let"
            return "let"

        kind = var.declaration_kind
        return kind if kind != "none" else ""

    #
    # JS FFI (Foreign Function Interface)
    #
    def add_js_ffi_name(self, name: str) -> None:
        """Register a name as a JS FFI module reference.

        This is called when processing 'import js' or 'import js as name'.
        Access to attributes of these names will emit raw JS without the prefix.
        """
        self._js_ffi_names.add(name)

    def is_js_ffi_name(self, name: str) -> bool:
        """Check if a name is a JS FFI module reference."""
        return name in self._js_ffi_names

    #
    # Module Resolution
    #
    def get_resolver(self) -> ModuleResolver:
        """Get a module resolver for this compilation context."""
        return ModuleResolver(
            source_dir=self._source_dir,
            module_paths=self._module_paths,
            verify_exists=True,  # Verify module paths to distinguish packages from modules
        )

    def resolve_module(self, module: str, level: int = 0) -> str:
        """Resolve a Python module name to a JavaScript import path.

        Args:
            module: Python module name (e.g., 'foo.bar.baz')
            level: Number of dots for relative import (0=absolute, 1=current, 2=parent)

        Returns:
            JavaScript import path (e.g., './foo/bar/baz.js')
        """
        resolver = self.get_resolver()
        result = resolver.resolve(module, level)
        return result.js_path

    def resolve_import_name(self, name: str, level: int = 0) -> str:
        """Resolve a single import name (for 'from . import name').

        Args:
            name: The name being imported
            level: Number of dots for relative import

        Returns:
            JavaScript import path
        """
        resolver = self.get_resolver()
        result = resolver.resolve_import_name(name, level)
        return result.js_path

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
            # Add source map mapping before generating statement
            self._add_statement_mapping(statement)
            stmt_code = self.gen_stmt(statement)
            code += [stmt_code]
            # Update output line count
            self._update_output_line(stmt_code)

        return flatten(code, sep="\n")

    def _add_statement_mapping(self, node: ast.stmt) -> None:
        """Add a source map mapping for a statement."""
        if self._source_map is None:
            return
        if not hasattr(node, "lineno"):
            return

        # Map current output line to source line (both 0-indexed in source map)
        self._source_map.add_mapping(
            gen_line=self._output_line,
            gen_column=0,
            src_line=node.lineno - 1,  # AST uses 1-indexed lines
            src_column=getattr(node, "col_offset", 0),
        )

    def _update_output_line(self, code) -> None:
        """Update output line counter based on generated code."""
        if self._source_map is None:
            return
        # Count newlines in the generated code
        if isinstance(code, str):
            self._output_line += code.count("\n")
        elif isinstance(code, list):
            for item in code:
                self._update_output_line(item)

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
        # Track usage for tree-shaking
        self._used_std_functions.add(name)

        mangled_name = self.function_prefix + name
        js_args = list(self.gen_js_args(args))
        return f"{mangled_name}({', '.join(js_args)})"

    def call_std_method(self, base, name: str, args: list) -> str:
        """Generate a method call from the Prescrypt standard library.

        Uses Function.prototype.call() to invoke the method with `base` as `this`.
        """
        # Track usage for tree-shaking
        self._used_std_methods.add(name)

        mangled_name = self.method_prefix + name
        js_args = list(self.gen_js_args(args))
        # First argument to .call() is the `this` value (the object to call method on)
        all_args = [base] + js_args
        return f"{mangled_name}.call({', '.join(all_args)})"

    def gen_js_args(self, args) -> Iterator[str]:
        for arg in args:
            if isinstance(arg, str):
                yield arg
            else:
                yield unify(self.gen_expr(arg))

    #
    # Utility functions
    #
    def gen_truthy(self, node: ast.expr) -> str | list:
        """Wraps an operation in a truthy call, unless it's not necessary."""
        eq_name = self.function_prefix + "op_equals"
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
        """Format a string using the old-school `%` operator.

        Uses the runtime string_mod function for consistent Python-compatible
        formatting including proper boolean-to-int conversion for numeric formats.
        """
        assert isinstance(left, ast.Constant) and isinstance(left.value, str)
        js_left = "".join(self.gen_expr(left))

        # For tuples, generate array that will be unpacked at runtime
        # For lists and other values, wrap in a marker array to prevent unpacking
        if isinstance(right, ast.Tuple):
            # Tuple - transpile normally, runtime will unpack
            js_right = unify(self.gen_expr(right))
        elif isinstance(right, ast.List):
            # List - mark as non-tuple so runtime won't unpack
            js_right = unify(self.gen_expr(right))
            js_right = f"Object.assign({js_right}, {{_is_list: true}})"
        else:
            # Other value - runtime will handle based on type
            js_right = unify(self.gen_expr(right))

        return self.call_std_function("string_mod", [js_left, js_right])

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
        from prescrypt.constants import escape_js_name

        # Escape JavaScript reserved words
        name = escape_js_name(name)

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
        self._stack.pop()  # Remove current namespace
        self.ns = self._stack[-1]  # Set to new top of stack

    def get_enclosing_class(self) -> str | None:
        """Get the name of the enclosing class, if any.

        Walks up the namespace stack to find the closest class namespace.
        Returns None if not inside a class.
        """
        for ns in reversed(self._stack):
            if ns.type == "class":
                return ns.name
        return None

    def is_module_level(self) -> bool:
        """Check if we're currently at module level (not inside a function or class)."""
        return len(self._stack) == 1 and self._stack[0].type == "module"

    def should_export(self, name: str | None = None) -> bool:
        """Check if the current definition should be exported.

        Returns True if module_mode is enabled and we're at module level.
        If __all__ is defined, only names in __all__ are exported.

        Args:
            name: Optional name to check against __all__. If None, just checks
                  if we're in export context (for backward compatibility).
        """
        if not self.module_mode or not self.is_module_level():
            return False

        # If __all__ is defined and name is provided, check if name is in __all__
        if self._module_all is not None and name is not None:
            return name in self._module_all

        return True

    @staticmethod
    def _extract_module_all(module: ast.Module) -> set[str] | None:
        """Extract __all__ from module if defined.

        Scans module-level statements for `__all__ = [...]` and returns
        the set of names. Returns None if __all__ is not defined.
        """
        for stmt in module.body:
            if isinstance(stmt, ast.Assign):
                # Check for __all__ = [...]
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(stmt.value, ast.List):
                            names = set()
                            for elt in stmt.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(
                                    elt.value, str
                                ):
                                    names.add(elt.value)
                            return names
        return None


class NameSpace:
    def __init__(self, type, name):
        self.type = type
        self.name = name
        self._vars = set()

    def add(self, var):
        self._vars.add(var)

    def is_known(self, var):
        return var in self._vars
