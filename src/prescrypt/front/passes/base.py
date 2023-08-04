from prescrypt.front import ast


class Visitor(ast.NodeVisitor):
    """
    Base class for visitors.
    """

    def visit(self, node: None | ast.AST | ast.expr | ast.stmt | ast.arguments):
        """
        Override the default visit method and add a type sugnature.

        `node` should be os type `AST` but we have to add other types because
        of a bug in PyCharm.
        """
        return super().visit(node)

    def visit_list(self, node_list: list[ast.AST | ast.expr]):
        for node in node_list:
            self.visit(node)


class Transformer(ast.NodeTransformer):
    """
    Base class for transformers.
    """

    def visit(self, node: None | ast.AST | ast.expr | ast.stmt | ast.arguments):
        """
        Override the default visit method and add a type sugnature.

        `node` should be os type `AST` but we have to add other types because
        of a bug in PyCharm.
        """
        return super().visit(node)

    def visit_list(self, node_list: list[ast.AST | ast.expr]):
        return [self.visit(node) for node in node_list]
