from __future__ import annotations

import builtins
from pathlib import Path

from prescrypt.front import Scope, Variable, ast

from .base import Visitor

builtin_names = {name for name in dir(builtins)}


class Binder(Visitor):
    """
    First visitor to run. Adds an attribute `definition` to ast nodes.
    """

    def __init__(self):
        self.scope = Scope()
        # Loop we're curently in (needed for break and continue)
        self.loop = None

    # Scope management
    def push_scope(self, type, node: ast.AST):
        new_scope = Scope(type, parent=self.scope)
        node._scope = new_scope
        self.scope = new_scope

    def pop_scope(self):
        self.scope = self.scope.parent

    def visit_list(self, li):
        for instr in li:
            self.visit(instr)

    #
    # Scope-creating nodes
    #
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Creates a symbol for the function and sets the node's definition to itself.
        """
        self.scope.vars[node.name] = Variable(name=node.name, type="function")

        self.push_scope("function", node)
        self.visit(node.args)
        self.visit_list(node.body)
        self.pop_scope()

    def visit_ClassDef(self, node: ast.ClassDef):
        """
        Creates a symbol for the class and sets the node's definition to itself.
        """
        self.scope.vars[node.name] = Variable(name=node.name, type="class")

        self.push_scope("class", node)
        self.visit_list(node.body)
        # self.visit(node.bases)
        self.pop_scope()

    def visit_Lambda(self, node: ast.Lambda):
        """
        Creates a symbol for the lambda and sets the node's definition to itself.
        """
        self.push_scope("function", node)
        self.visit(node.args)
        self.visit(node.body)
        self.pop_scope()

    def visit_ListComp(self, node: ast.ListComp):
        """
        Creates a symbol for the lambda and sets the node's definition to itself.
        """
        self.push_scope("listcomp", node)
        # Visit generators first
        self.visit_list(node.generators)
        self.visit(node.elt)
        self.pop_scope()

    #
    # Variables
    #
    def visit_Name(self, node: ast.Name):
        """
        If the context is ast.Load, check for the symbol in the
        symbol table, raise UnknownSymbolError if not found,
        else sets the node's definition to the symbol's.
        If the context is ast.Store, creates a new symbol and
        sets the node's definition to itself.
        """
        name = node.id

        match node.ctx:
            case ast.Load():
                if name in builtin_names:
                    return
                if self.scope.search(name) is None:
                    raise NameError(f"name '{name}' is not defined")

            case ast.Store():
                if name in builtin_names:
                    raise ValueError(f"cannot assign to '{name}'")
                if name in self.scope.vars:
                    self.scope.vars[name].is_const = False
                else:
                    self.scope.vars[name] = Variable(name=name, type="variable")
                # sym = Symbol(name, node)
                # self.map.append(sym)
                # node._definition = node

            case _:
                raise NotImplementedError("del instruction not yet implemented")

    def visit_arg(self, node: ast.arg):
        """
        Creates a new symbol for the argument, and sets the node's definition to itself
        """
        name = node.arg
        self.scope.vars[name] = Variable(name=name, type="variable")

    # def visit_Call(self, node: ast.Call):
    #     """
    #     Visits the Call node
    #     """
    #     self.visit(node.func)
    #     self.visit_list(node.args)
    #     node._definition = node.func._definition
    #
    # def visit_AnnAssign(self, node: ast.AnnAssign):
    #     """
    #     Visit the terms of the equality, but not the annotation.
    #
    #     Will likely be removed at some point
    #     """
    #     self.visit(node.target)
    #     self.visit(node.value)

    #
    # Loops
    #
    def visit_While(self, node: ast.While):
        """
        Sets self.loop properly.
        """
        node._definition = node

        save = self.loop
        self.loop = node

        self.visit(node.test)
        self.visit_list(node.body)
        self.visit_list(node.orelse)

        self.loop = save

    def visit_Continue(self, node: ast.Continue):
        """
        Sets definition.
        """
        if self.loop is None:
            raise SyntaxError("'continue' not properly in loop")

        node._definition = self.loop

    def visit_Break(self, node: ast.Break):
        """
        Sets definition
        """
        if self.loop is None:
            raise SyntaxError("'break' not properly in loop")

        node._definition = self.loop


if __name__ == "__main__":
    import sys

    code = Path(sys.argv[1]).read_text()
    tree = ast.parse(code)
    Binder().visit(tree)
    print(tree)
