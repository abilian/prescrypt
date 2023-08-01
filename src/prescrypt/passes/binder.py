import builtins

from prescrypt.ast import ast

from .base import Visitor
from .errors import UnknownSymbolError
from .scopes import ScopedMap
from .symbol import Symbol

builtin_names = {name for name in dir(builtins)}


class Binder(Visitor):
    """
    First visitor to run. Adds an attribute `definition` to ast nodes.
    """

    def __init__(self):
        # Scopes
        self.map = ScopedMap()  # Scope
        # Loop we're curently in (needed for break and continue)
        self.loop = None

    def visit_list(self, li):
        for instr in li:
            self.visit(instr)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Creates a symbol for the function and sets the node's definition to itself.
        """

        sym = Symbol(node.name, node)
        self.map.append(sym)
        node._definition = node

        self.map.push_scope(sym)
        self.visit(node.args)
        self.visit_list(node.body)

        self.map.pop_scope()

    def visit_arg(self, node: ast.arg):
        """
        Creates a new symbol for the argument, and sets the node's definition to itself
        """
        sym = Symbol(node.arg, node)
        self.map.append(sym)
        node._definition = node

    def visit_Call(self, node: ast.Call):
        """
        Visits the Call node
        """
        self.visit(node.func)
        self.visit_list(node.args)
        node._definition = node.func._definition

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """
        Visit the terms of the equality, but not the annotation.

        Will likely be removed at some point
        """
        self.visit(node.target)
        self.visit(node.value)

    def visit_Name(self, node: ast.Name):
        """
        If the context is ast.Load, check for the symbol in the
        symbol table, raise UnknownSymbolError if not found,
        else sets the node's definition to the symbol's.
        If the context is ast.Store, creates a new symbol and
        sets the node's definition to itself.
        """
        name = node.id
        if name in builtin_names:
            return

        sym = self.map.find(name, False)
        if sym is not None:
            node._definition = sym._definition
            return

        match node.ctx:
            case ast.Load():
                raise UnknownSymbolError(name)
            case ast.Store():
                sym = Symbol(name, node)
                self.map.append(sym)
                node._definition = node
            case _:
                raise NotImplementedError("del instruction not yet implemented")

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
