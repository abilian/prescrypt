from __future__ import annotations

from prescrypt.front import ast

from .base import Visitor
from .types import Bool, Dict, Float, Int, List, String, Tuple, Unknown, Void

TYPE_MAP = {
    "int": Int,
    "str": String,
    "float": Float,
    "bool": Bool,
    "NoneType": Void,
    "list": List,
    "dict": Dict,
    "tuple": Tuple,
}


class TypeInference(Visitor):
    """
    Visitor that adds a `_type` attribute into nodes, holding the type.

    This is a best-effort type inference pass. When types cannot be
    determined, it assigns Unknown instead of failing.
    """

    def visit_list(self, li):
        for node in li:
            self.visit(node)

    def update_node(self, node, typ):
        type_cls = TYPE_MAP.get(typ, Unknown)
        setattr(node, "_type", type_cls)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Adds the `typ` attribute to the node, using annotation.
        """
        if node.returns and hasattr(node.returns, "id"):
            self.update_node(node, node.returns.id)
        else:
            node._type = Unknown

        self.visit(node.args)
        self.visit_list(node.body)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """
        Adds the `typ` attribute to async functions.
        """
        if node.returns and hasattr(node.returns, "id"):
            self.update_node(node, node.returns.id)
        else:
            node._type = Unknown

        self.visit(node.args)
        self.visit_list(node.body)

    def visit_arg(self, node: ast.arg):
        """
        Sets the node's typ to its annotation.
        """
        if node.annotation and hasattr(node.annotation, "id"):
            typ = node.annotation.id
            node._type = TYPE_MAP.get(typ, Unknown)
        else:
            node._type = Unknown

    def visit_Call(self, node: ast.Call):
        """
        Sets the node's type to its definition's type, if available.
        For built-in functions without definitions, type is Unknown.
        """
        # Visit the function being called
        self.visit(node.func)
        # Visit arguments
        self.visit_list(node.args)
        for kw in node.keywords:
            self.visit(kw.value)

        # Try to get type from definition
        if hasattr(node, "_definition") and node._definition is not None:
            if hasattr(node._definition, "_type"):
                node._type = node._definition._type
                return

        # Fallback: Unknown type for built-ins or undefined functions
        node._type = Unknown

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """
        Sets the node's type to its annotation.
        """
        if node.value:
            self.visit(node.value)

        if node.annotation and hasattr(node.annotation, "id"):
            typ = node.annotation.id
            node.target._type = TYPE_MAP.get(typ, Unknown)
        else:
            node.target._type = Unknown

    def visit_Assign(self, node: ast.Assign):
        """
        Sets the targets's `typ` to the value's.
        """
        self.visit(node.value)
        typ = getattr(node.value, "_type", Unknown)

        for t in node.targets:
            t._type = typ

    def visit_Name(self, node: ast.Name):
        """
        If the context is ast.Load, sets the node's typ to its definition's.
        If the context is an ast.Store, pass, as the type will be set somewhere else.
        """
        match node.ctx:
            case ast.Load():
                if hasattr(node, "_definition") and node._definition is not None:
                    if hasattr(node._definition, "_type"):
                        node._type = node._definition._type
                        return
                node._type = Unknown
            case ast.Store():
                pass  # Means we're in left side of an assign, will be set by caller
            case _:
                node._type = Unknown  # Del context

    def visit_Constant(self, node):
        """
        Sets the constant's type to the type of its value.
        """
        type_name = type(node.value).__name__
        node._type = TYPE_MAP.get(type_name, Unknown)

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
                node._type = getattr(node.left, "_type", Unknown)

    def visit_UnaryOp(self, node: ast.UnaryOp):
        self.visit(node.operand)
        node._type = getattr(node.operand, "_type", Unknown)

    def visit_BoolOp(self, node: ast.BoolOp):
        node._type = Bool
        self.visit_list(node.values)

    def visit_Compare(self, node: ast.Compare):
        node._type = Bool
        self.visit(node.left)
        self.visit_list(node.comparators)

    # Container literals
    def visit_List(self, node: ast.List):
        """List literal."""
        self.visit_list(node.elts)
        node._type = List

    def visit_Tuple(self, node: ast.Tuple):
        """Tuple literal."""
        self.visit_list(node.elts)
        node._type = Tuple

    def visit_Dict(self, node: ast.Dict):
        """Dict literal."""
        for key in node.keys:
            if key is not None:
                self.visit(key)
        self.visit_list(node.values)
        node._type = Dict

    def visit_Set(self, node: ast.Set):
        """Set literal."""
        self.visit_list(node.elts)
        node._type = Unknown  # Could add a Set type

    # Subscript and Attribute access
    def visit_Subscript(self, node: ast.Subscript):
        """Subscript access like a[0] or d['key']."""
        self.visit(node.value)
        self.visit(node.slice)
        node._type = Unknown  # Would need element type tracking

    def visit_Attribute(self, node: ast.Attribute):
        """Attribute access like obj.attr."""
        self.visit(node.value)
        node._type = Unknown  # Would need object type tracking

    # Comprehensions
    def visit_ListComp(self, node: ast.ListComp):
        """List comprehension."""
        self.visit_list(node.generators)
        self.visit(node.elt)
        node._type = List

    def visit_SetComp(self, node: ast.SetComp):
        """Set comprehension."""
        self.visit_list(node.generators)
        self.visit(node.elt)
        node._type = Unknown  # Could add Set type

    def visit_DictComp(self, node: ast.DictComp):
        """Dict comprehension."""
        self.visit_list(node.generators)
        self.visit(node.key)
        self.visit(node.value)
        node._type = Dict

    def visit_GeneratorExp(self, node: ast.GeneratorExp):
        """Generator expression."""
        self.visit_list(node.generators)
        self.visit(node.elt)
        node._type = Unknown  # Could add Generator type

    def visit_comprehension(self, node: ast.comprehension):
        """Generator in a comprehension."""
        self.visit(node.iter)
        self.visit(node.target)
        for if_clause in node.ifs:
            self.visit(if_clause)

    # Conditional expression
    def visit_IfExp(self, node: ast.IfExp):
        """Ternary expression: x if cond else y."""
        self.visit(node.test)
        self.visit(node.body)
        self.visit(node.orelse)
        # Type is the type of the body (could be union of body/orelse)
        node._type = getattr(node.body, "_type", Unknown)

    # Slices
    def visit_Slice(self, node: ast.Slice):
        """Slice object."""
        if node.lower:
            self.visit(node.lower)
        if node.upper:
            self.visit(node.upper)
        if node.step:
            self.visit(node.step)
        node._type = Unknown

    # Starred expression
    def visit_Starred(self, node: ast.Starred):
        """Starred expression *args."""
        self.visit(node.value)
        node._type = Unknown

    # Lambda
    def visit_Lambda(self, node: ast.Lambda):
        """Lambda expression."""
        self.visit(node.args)
        self.visit(node.body)
        node._type = Unknown  # Could add Function type

    # Formatted value (f-string component)
    def visit_FormattedValue(self, node: ast.FormattedValue):
        """Formatted value in f-string."""
        self.visit(node.value)
        if node.format_spec:
            self.visit(node.format_spec)
        node._type = String

    def visit_JoinedStr(self, node: ast.JoinedStr):
        """f-string."""
        self.visit_list(node.values)
        node._type = String

    # Named expression (walrus operator)
    def visit_NamedExpr(self, node: ast.NamedExpr):
        """Walrus operator :=."""
        self.visit(node.value)
        self.visit(node.target)
        node._type = getattr(node.value, "_type", Unknown)
