from prescrypt.ast import ast
from prescrypt.ast.ast import Function


def get_top_scope(tree):
    top = Scope(tree, ())
    top.visit(tree)
    top.analyze(set())
    return top


class Scope(ast.NodeVisitor):
    def __init__(self, node, defs):
        self.t = node
        self.children = {}  # Enclosed sub-scopes
        self.defs = set(defs)  # Variables defined
        self.uses = set()  # Variables referenced

    def visit_ClassDef(self, node: ast.ClassDef):
        self.defs.add(node.name)
        for expr in node.bases:
            self.visit(expr)
        subscope = Scope(node, ())
        self.children[node] = subscope
        for stmt in node.body:
            subscope.visit(stmt)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.defs.add(node.name)
        all_args = list(node.args.args) + [node.args.vararg, node.args.kwarg]
        subscope = Scope(node, [arg.arg for arg in all_args if arg])
        self.children[node] = subscope
        for stmt in node.body:
            subscope.visit(stmt)

    def visit_Lambda(self, node: ast.Lambda):
        all_args = list(node.args.args) + [node.args.vararg, node.args.kwarg]
        subscope = Scope(node, [arg.arg for arg in all_args if arg])
        self.children[node] = subscope
        subscope.visit(node.body)

    def visit_Import(self, t: ast.Import):
        for alias in t.names:
            self.defs.add(alias.asname or alias.name.split(".")[0])

    def visit_ImportFrom(self, node: ast.ImportFrom):
        for alias in node.names:
            self.defs.add(alias.asname or alias.name)

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load):
            self.uses.add(node.id)
        elif isinstance(node.ctx, ast.Store):
            self.defs.add(node.id)
        else:
            assert False

    def analyze(self, parent_defs):
        self.local_defs = self.defs if isinstance(self.t, Function) else set()
        for child in self.children.values():
            child.analyze(parent_defs | self.local_defs)
        child_uses = set(
            [var for child in self.children.values() for var in child.freevars]
        )
        uses = self.uses | child_uses
        self.cellvars = tuple(child_uses & self.local_defs)
        self.freevars = tuple(uses & (parent_defs - self.local_defs))
        self.derefvars = self.cellvars + self.freevars

    def access(self, name):
        if name in self.derefvars:
            return "deref"
        elif name in self.local_defs:
            return "fast"
        else:
            return "name"
