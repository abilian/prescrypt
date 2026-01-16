from __future__ import annotations

import builtins
from pathlib import Path

from prescrypt.front import Scope, Variable, ast

from .base import Visitor

builtin_names = {name for name in dir(builtins)}


class Binder(Visitor):
    """
    First visitor to run. Builds scope hierarchy and validates variable usage.

    Attaches `_scope` to scope-creating nodes (FunctionDef, ClassDef, etc.)
    and tracks variables with their constness.
    """

    def __init__(self):
        self.scope = Scope()
        # Loop we're currently in (needed for break and continue)
        self.loop = None

    # Scope management
    def push_scope(self, scope_type: str, node: ast.AST):
        new_scope = Scope(scope_type, parent=self.scope)
        node._scope = new_scope
        self.scope = new_scope

    def pop_scope(self):
        self.scope = self.scope.parent

    def add_var(self, name: str, var_type: str = "variable"):
        """Add a variable to the current scope."""
        if name in self.scope.vars:
            self.scope.vars[name].is_const = False
        else:
            self.scope.vars[name] = Variable(name=name, type=var_type)

    def visit_list(self, li):
        for instr in li:
            self.visit(instr)

    def visit_Module(self, node: ast.Module):
        """Attach the module scope to the Module node."""
        node._scope = self.scope
        self.visit_list(node.body)

    #
    # Scope-creating nodes
    #
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Register function name in current scope, then process its body in new scope."""
        self.add_var(node.name, "function")

        self.push_scope("function", node)
        self.visit(node.args)
        self.visit_list(node.body)
        self.pop_scope()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Same as FunctionDef but for async functions."""
        self.add_var(node.name, "function")

        self.push_scope("function", node)
        self.visit(node.args)
        self.visit_list(node.body)
        self.pop_scope()

    def visit_ClassDef(self, node: ast.ClassDef):
        """Register class name in current scope, then process its body in new scope."""
        self.add_var(node.name, "class")

        self.push_scope("class", node)
        # Visit base classes in the outer scope (they're looked up, not defined)
        for base in node.bases:
            self.visit(base)
        self.visit_list(node.body)
        self.pop_scope()

    def visit_Lambda(self, node: ast.Lambda):
        """Lambda creates a new function scope."""
        self.push_scope("function", node)
        self.visit(node.args)
        self.visit(node.body)
        self.pop_scope()

    def visit_ListComp(self, node: ast.ListComp):
        """List comprehension has its own scope in Python 3."""
        self.push_scope("comprehension", node)
        self.visit_list(node.generators)
        self.visit(node.elt)
        self.pop_scope()

    def visit_SetComp(self, node: ast.SetComp):
        """Set comprehension has its own scope."""
        self.push_scope("comprehension", node)
        self.visit_list(node.generators)
        self.visit(node.elt)
        self.pop_scope()

    def visit_DictComp(self, node: ast.DictComp):
        """Dict comprehension has its own scope."""
        self.push_scope("comprehension", node)
        self.visit_list(node.generators)
        self.visit(node.key)
        self.visit(node.value)
        self.pop_scope()

    def visit_GeneratorExp(self, node: ast.GeneratorExp):
        """Generator expression has its own scope."""
        self.push_scope("comprehension", node)
        self.visit_list(node.generators)
        self.visit(node.elt)
        self.pop_scope()

    #
    # Variables
    #
    def visit_Name(self, node: ast.Name):
        """Handle variable references based on context (Load, Store, Del)."""
        name = node.id

        match node.ctx:
            case ast.Load():
                # Reading a variable - just validate if it's a builtin or known
                # Don't raise for undefined names - they might be defined elsewhere
                # (in another module, as a JS global, etc.)
                pass

            case ast.Store():
                # Assigning to a variable
                if name in builtin_names:
                    msg = f"cannot assign to '{name}'"
                    raise ValueError(msg)
                self.add_var(name)

            case ast.Del():
                # Deleting a variable
                if name in builtin_names:
                    msg = f"cannot delete '{name}'"
                    raise ValueError(msg)

    def visit_arg(self, node: ast.arg):
        """Register function argument as a variable."""
        self.add_var(node.arg)

    def visit_NamedExpr(self, node: ast.NamedExpr):
        """Walrus operator (:=) - assigns and returns value."""
        # The target is always a Name with Store context
        self.visit(node.target)
        self.visit(node.value)

    #
    # Imports
    #
    def visit_Import(self, node: ast.Import):
        """Import statement registers module names."""
        for alias in node.names:
            # Use the alias if provided, otherwise the module name
            name = alias.asname if alias.asname else alias.name
            # For "import a.b.c", only "a" is bound
            name = name.split(".")[0]
            self.add_var(name, "module")

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """From-import registers the imported names."""
        for alias in node.names:
            if alias.name == "*":
                # "from x import *" - we can't know what's imported
                # Just skip validation for this module
                continue
            name = alias.asname if alias.asname else alias.name
            self.add_var(name, "module")

    #
    # Global/Nonlocal declarations
    #
    def visit_Global(self, node: ast.Global):
        """Mark names as global (looked up in module scope)."""
        for name in node.names:
            # Register in current scope as a marker
            # The actual variable lives in the module scope
            self.scope.vars[name] = Variable(name=name, type="global")

            # Mark the module-level variable as mutable since it can be modified
            # via the global declaration
            module_scope = self._get_module_scope()
            if module_scope and name in module_scope.vars:
                module_scope.vars[name].is_const = False

    def _get_module_scope(self) -> Scope | None:
        """Find the module (root) scope."""
        scope = self.scope
        while scope.parent is not None:
            scope = scope.parent
        return scope

    def visit_Nonlocal(self, node: ast.Nonlocal):
        """Mark names as nonlocal (looked up in enclosing scope)."""
        for name in node.names:
            # Verify the name exists in an enclosing scope
            if self.scope.parent is None:
                msg = "nonlocal declaration not allowed at module level"
                raise SyntaxError(msg)
            enclosing_var = self.scope.parent.search(name)
            if enclosing_var is None:
                msg = f"no binding for nonlocal '{name}' found"
                raise SyntaxError(msg)
            self.scope.vars[name] = Variable(name=name, type="nonlocal")

            # Mark the enclosing variable as mutable since it can be modified
            # via the nonlocal declaration
            enclosing_var.is_const = False

    #
    # Loops
    #
    def visit_For(self, node: ast.For):
        """For loop - target variable(s) and iteration."""
        node._definition = node

        save = self.loop
        self.loop = node

        # Visit the iterable first (it's evaluated in outer scope)
        self.visit(node.iter)
        # Then the target (this defines variables)
        self.visit(node.target)
        # Then the body
        self.visit_list(node.body)
        self.visit_list(node.orelse)

        self.loop = save

    def visit_AsyncFor(self, node: ast.AsyncFor):
        """Async for loop - same as For."""
        node._definition = node

        save = self.loop
        self.loop = node

        self.visit(node.iter)
        self.visit(node.target)
        self.visit_list(node.body)
        self.visit_list(node.orelse)

        self.loop = save

    def visit_While(self, node: ast.While):
        """While loop."""
        node._definition = node

        save = self.loop
        self.loop = node

        self.visit(node.test)
        self.visit_list(node.body)
        self.visit_list(node.orelse)

        self.loop = save

    def visit_Continue(self, node: ast.Continue):
        """Continue must be inside a loop."""
        if self.loop is None:
            msg = "'continue' not properly in loop"
            raise SyntaxError(msg)
        node._definition = self.loop

    def visit_Break(self, node: ast.Break):
        """Break must be inside a loop."""
        if self.loop is None:
            msg = "'break' not properly in loop"
            raise SyntaxError(msg)
        node._definition = self.loop

    #
    # Exception handling
    #
    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        """Exception handler - binds the exception to a name."""
        if node.type:
            self.visit(node.type)
        if node.name:
            self.add_var(node.name)
        self.visit_list(node.body)

    #
    # With statements
    #
    def visit_With(self, node: ast.With):
        """With statement - context manager with optional 'as' binding."""
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars:
                self.visit(item.optional_vars)
        self.visit_list(node.body)

    def visit_AsyncWith(self, node: ast.AsyncWith):
        """Async with statement - same as With."""
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars:
                self.visit(item.optional_vars)
        self.visit_list(node.body)

    #
    # Comprehension generators
    #
    def visit_comprehension(self, node: ast.comprehension):
        """Generator in a comprehension - defines the iteration variable."""
        # Visit iter first (evaluated in outer scope for first generator)
        self.visit(node.iter)
        # Target defines variables in the comprehension scope
        self.visit(node.target)
        # Conditions are evaluated in comprehension scope
        for if_clause in node.ifs:
            self.visit(if_clause)


if __name__ == "__main__":
    import sys

    code = Path(sys.argv[1]).read_text()
    tree = ast.parse(code)
    Binder().visit(tree)
    print(tree)
