from prescrypt.front import ast

from .base import Visitor
from .types import Bool, Float, Int, String

TYPE_MAP = {
    "int": Int,
    "str": String,
    "float": Float,
    "bool": Bool,
}


class TypeInference(Visitor):
    """
    Visitor that adds a `_type` attribute into nodes, holding the type
    """

    def visit_list(self, li):
        for node in li:
            self.visit(node)

    def update_node(self, node, typ):
        type = TYPE_MAP.get(typ)
        if not type:
            raise ValueError(f"Unknown type: {typ}")
        # node._type = type
        setattr(node, "_type", type)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Adds the `typ` attribute to the node, using annotation
        """
        self.update_node(node, node.returns.id)

        self.visit(node.args)
        self.visit_list(node.body)

    def visit_arg(self, node: ast.arg):
        """
        Sets the node's typ to its annotation.
        """
        typ = node.annotation.id
        node._type = TYPE_MAP[typ]

    def visit_Call(self, node: ast.Call):
        """
        Sets the node's type to its definition's
        """
        node._type = node._definition._type
        self.visit_list(node.args)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """
        Sets the node's type to its annotation
        """
        self.visit(node.value)
        typ = node.annotation.id

        if not self.__exists(typ):
            raise ValueError(f"Unknown type: {typ}")

        node.target._type = TYPE_MAP[typ]

    def visit_Assign(self, node: ast.Assign):
        """
        Sets the targets's `typ` to the value's
        """
        self.visit(node.value)
        typ = node.value._type

        for t in node.targets:
            t._type = typ

    def visit_Name(self, node: ast.Name):
        """
        If the context is ast.Load, sets the node's typ to its definition's.

        If the context is an ast.Store, pass, as the type will be set somewhere else.
        """
        match node.ctx:
            case ast.Load():
                node._type = node._definition._type
            case ast.Store():
                pass  # Means we're in left side of an assign, will be set by caller
            case _:
                raise NotImplementedError("del operator not yet implemented")

    def visit_Constant(self, node):
        """
        Sets the constant's type to the type of its value.
        """
        node._type = TYPE_MAP[type(node.value).__name__]

    def visit_BinOp(self, node: ast.BinOp):
        """
        Sets the BinOp's type to the one of its left value (arbitrary).
        """
        self.visit(node.left)
        self.visit(node.right)

        match node.op:
            case ast.FloorDiv():
                node._type = Float
            case _:
                node._type = node.left._type

    def visit_UnaryOp(self, node: ast.UnaryOp):
        self.visit(node.operand)
        node._type = node.operand._type

    def visit_BoolOp(self, node: ast.BoolOp):
        node._type = Bool
        self.visit_list(node.values)

    def visit_Compare(self, node: ast.Compare):
        node._type = Bool
        self.visit(node.left)
        self.visit_list(node.comparators)
