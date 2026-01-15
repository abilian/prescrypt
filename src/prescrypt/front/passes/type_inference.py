"""Type inference pass.

Adds a `_type` attribute to AST nodes, using annotations and inference.
This is a best-effort pass - when types cannot be determined, it assigns Unknown.
"""

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
    """Visitor that infers and attaches types to AST nodes."""

    def visit_list(self, nodes):
        for node in nodes:
            self.visit(node)

    def _type_from_annotation(self, annotation) -> type:
        """Extract type from an annotation node."""
        match annotation:
            case ast.Name(id=type_name):
                return TYPE_MAP.get(type_name, Unknown)
            case _:
                return Unknown

    def _type_from_definition(self, node) -> type:
        """Get type from a node's definition, if available."""
        match getattr(node, "_definition", None):
            case None:
                return Unknown
            case defn if hasattr(defn, "_type"):
                return defn._type
            case _:
                return Unknown

    # =========================================================================
    # Definitions
    # =========================================================================

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Infer function return type from annotation."""
        node._type = self._type_from_annotation(node.returns)
        self.visit(node.args)
        self.visit_list(node.body)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Infer async function return type from annotation."""
        node._type = self._type_from_annotation(node.returns)
        self.visit(node.args)
        self.visit_list(node.body)

    def visit_arg(self, node: ast.arg):
        """Infer argument type from annotation."""
        node._type = self._type_from_annotation(node.annotation)

    def visit_Lambda(self, node: ast.Lambda):
        """Lambda expression - type unknown without annotation."""
        self.visit(node.args)
        self.visit(node.body)
        node._type = Unknown

    # =========================================================================
    # Assignments
    # =========================================================================

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """Annotated assignment - use the annotation."""
        if node.value:
            self.visit(node.value)
        node.target._type = self._type_from_annotation(node.annotation)

    def visit_Assign(self, node: ast.Assign):
        """Assignment - propagate type from value to targets."""
        self.visit(node.value)
        value_type = getattr(node.value, "_type", Unknown)
        for target in node.targets:
            target._type = value_type

    def visit_NamedExpr(self, node: ast.NamedExpr):
        """Walrus operator := - type is the value's type."""
        self.visit(node.value)
        self.visit(node.target)
        node._type = getattr(node.value, "_type", Unknown)

    # =========================================================================
    # Names and Calls
    # =========================================================================

    def visit_Name(self, node: ast.Name):
        """Name reference - get type from definition if loading."""
        match node.ctx:
            case ast.Load():
                node._type = self._type_from_definition(node)
            case ast.Store():
                pass  # Type set by assignment
            case _:
                node._type = Unknown

    def visit_Call(self, node: ast.Call):
        """Function call - get type from function definition."""
        self.visit(node.func)
        self.visit_list(node.args)
        for keyword in node.keywords:
            self.visit(keyword.value)
        node._type = self._type_from_definition(node)

    # =========================================================================
    # Literals
    # =========================================================================

    def visit_Constant(self, node: ast.Constant):
        """Constant literal - type from Python value type."""
        type_name = type(node.value).__name__
        node._type = TYPE_MAP.get(type_name, Unknown)

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
        node._type = Unknown

    # =========================================================================
    # Operations
    # =========================================================================

    def visit_BinOp(self, node: ast.BinOp):
        """Binary operation - infer from operands."""
        self.visit(node.left)
        self.visit(node.right)
        match node.op:
            case ast.FloorDiv():
                node._type = Float
            case _:
                node._type = getattr(node.left, "_type", Unknown)

    def visit_UnaryOp(self, node: ast.UnaryOp):
        """Unary operation - same type as operand."""
        self.visit(node.operand)
        node._type = getattr(node.operand, "_type", Unknown)

    def visit_BoolOp(self, node: ast.BoolOp):
        """Boolean operation - always bool."""
        self.visit_list(node.values)
        node._type = Bool

    def visit_Compare(self, node: ast.Compare):
        """Comparison - always bool."""
        self.visit(node.left)
        self.visit_list(node.comparators)
        node._type = Bool

    def visit_IfExp(self, node: ast.IfExp):
        """Ternary expression - type of body branch."""
        self.visit(node.test)
        self.visit(node.body)
        self.visit(node.orelse)
        node._type = getattr(node.body, "_type", Unknown)

    # =========================================================================
    # Subscript and Attribute
    # =========================================================================

    def visit_Subscript(self, node: ast.Subscript):
        """Subscript access - would need element type tracking."""
        self.visit(node.value)
        self.visit(node.slice)
        node._type = Unknown

    def visit_Attribute(self, node: ast.Attribute):
        """Attribute access - would need object type tracking."""
        self.visit(node.value)
        node._type = Unknown

    def visit_Slice(self, node: ast.Slice):
        """Slice object."""
        if node.lower:
            self.visit(node.lower)
        if node.upper:
            self.visit(node.upper)
        if node.step:
            self.visit(node.step)
        node._type = Unknown

    def visit_Starred(self, node: ast.Starred):
        """Starred expression *args."""
        self.visit(node.value)
        node._type = Unknown

    # =========================================================================
    # Comprehensions
    # =========================================================================

    def visit_ListComp(self, node: ast.ListComp):
        """List comprehension."""
        self.visit_list(node.generators)
        self.visit(node.elt)
        node._type = List

    def visit_SetComp(self, node: ast.SetComp):
        """Set comprehension."""
        self.visit_list(node.generators)
        self.visit(node.elt)
        node._type = Unknown

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
        node._type = Unknown

    def visit_comprehension(self, node: ast.comprehension):
        """Generator in a comprehension."""
        self.visit(node.iter)
        self.visit(node.target)
        for if_clause in node.ifs:
            self.visit(if_clause)

    # =========================================================================
    # F-strings
    # =========================================================================

    def visit_FormattedValue(self, node: ast.FormattedValue):
        """Formatted value in f-string."""
        self.visit(node.value)
        if node.format_spec:
            self.visit(node.format_spec)
        node._type = String

    def visit_JoinedStr(self, node: ast.JoinedStr):
        """F-string."""
        self.visit_list(node.values)
        node._type = String
