"""Type inference pass.

Adds a `_type` attribute to AST nodes, using annotations and inference.
This is a best-effort pass - when types cannot be determined, it assigns Unknown.
"""

from __future__ import annotations

from prescrypt.front import ast

from .base import Visitor
from .types import Bool, Dict, Float, Int, JSObject, List, String, Tuple, Unknown, Void

TYPE_MAP = {
    "int": Int,
    "str": String,
    "float": Float,
    "bool": Bool,
    "NoneType": Void,
    "list": List,
    "dict": Dict,
    "tuple": Tuple,
    "JS": JSObject,
    "JSObject": JSObject,
}

# Return types for built-in functions
BUILTIN_RETURN_TYPES = {
    # Type constructors
    "int": Int,
    "float": Float,
    "str": String,
    "bool": Bool,
    "list": List,
    "dict": Dict,
    "tuple": Tuple,
    # Numeric functions
    "len": Int,
    "abs": Float,  # Could be Int but Float is safe
    "round": Int,
    "sum": Float,  # Could be Int but Float is safe
    "ord": Int,
    "chr": String,
    "hex": String,
    "oct": String,
    "bin": String,
    # Sequence functions
    "range": List,
    "enumerate": List,
    "zip": List,
    "map": List,
    "filter": List,
    "sorted": List,
    "reversed": List,
    # I/O
    "input": String,
    "repr": String,
    "format": String,
    # Type checking
    "isinstance": Bool,
    "issubclass": Bool,
    "callable": Bool,
    "hasattr": Bool,
    # Other
    "hash": Int,
    "id": Int,
}

# Return types for methods based on receiver type
# Key is (receiver_type, method_name)
METHOD_RETURN_TYPES = {
    # String methods
    (String, "upper"): String,
    (String, "lower"): String,
    (String, "capitalize"): String,
    (String, "title"): String,
    (String, "strip"): String,
    (String, "lstrip"): String,
    (String, "rstrip"): String,
    (String, "split"): List,
    (String, "rsplit"): List,
    (String, "splitlines"): List,
    (String, "join"): String,
    (String, "replace"): String,
    (String, "format"): String,
    (String, "find"): Int,
    (String, "rfind"): Int,
    (String, "index"): Int,
    (String, "rindex"): Int,
    (String, "count"): Int,
    (String, "startswith"): Bool,
    (String, "endswith"): Bool,
    (String, "isdigit"): Bool,
    (String, "isalpha"): Bool,
    (String, "isalnum"): Bool,
    (String, "isspace"): Bool,
    (String, "isupper"): Bool,
    (String, "islower"): Bool,
    (String, "istitle"): Bool,
    (String, "isnumeric"): Bool,
    (String, "isdecimal"): Bool,
    (String, "isidentifier"): Bool,
    (String, "isprintable"): Bool,
    (String, "isascii"): Bool,
    (String, "encode"): Unknown,  # bytes
    (String, "zfill"): String,
    (String, "center"): String,
    (String, "ljust"): String,
    (String, "rjust"): String,
    (String, "expandtabs"): String,
    (String, "partition"): Tuple,
    (String, "rpartition"): Tuple,
    (String, "swapcase"): String,
    (String, "casefold"): String,
    # List methods
    (List, "copy"): List,
    (List, "index"): Int,
    (List, "count"): Int,
    # Dict methods
    (Dict, "keys"): List,
    (Dict, "values"): List,
    (Dict, "items"): List,
    (Dict, "copy"): Dict,
    (Dict, "get"): Unknown,  # value type unknown
    (Dict, "pop"): Unknown,
    (Dict, "setdefault"): Unknown,
}


class TypeInference(Visitor):
    """Visitor that infers and attaches types to AST nodes."""

    def __init__(self):
        # Track variable types by name in current scope
        # Stack of dicts for nested scopes
        self._var_types: list[dict[str, type]] = [{}]

    def _push_scope(self):
        """Push a new scope for variable tracking."""
        self._var_types.append({})

    def _pop_scope(self):
        """Pop the current scope."""
        if len(self._var_types) > 1:
            self._var_types.pop()

    def _set_var_type(self, name: str, var_type: type):
        """Set the type of a variable in the current scope."""
        self._var_types[-1][name] = var_type

    def _get_var_type(self, name: str) -> type:
        """Get the type of a variable, searching from innermost to outermost scope."""
        for scope in reversed(self._var_types):
            if name in scope:
                return scope[name]
        return Unknown

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
        # Register function's return type in current scope so calls can use it
        self._set_var_type(node.name, node._type)
        self._push_scope()
        self.visit(node.args)
        self.visit_list(node.body)
        self._pop_scope()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Infer async function return type from annotation."""
        node._type = self._type_from_annotation(node.returns)
        # Register function's return type in current scope so calls can use it
        self._set_var_type(node.name, node._type)
        self._push_scope()
        self.visit(node.args)
        self.visit_list(node.body)
        self._pop_scope()

    def visit_arg(self, node: ast.arg):
        """Infer argument type from annotation."""
        arg_type = self._type_from_annotation(node.annotation)
        node._type = arg_type
        # Register argument type in scope
        self._set_var_type(node.arg, arg_type)

    def visit_Lambda(self, node: ast.Lambda):
        """Lambda expression - type unknown without annotation."""
        self._push_scope()
        self.visit(node.args)
        self.visit(node.body)
        self._pop_scope()
        node._type = Unknown

    # =========================================================================
    # Assignments
    # =========================================================================

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """Annotated assignment - use the annotation."""
        if node.value:
            self.visit(node.value)
        target_type = self._type_from_annotation(node.annotation)
        node.target._type = target_type
        # Register variable type in scope for simple Name targets
        if isinstance(node.target, ast.Name):
            self._set_var_type(node.target.id, target_type)

    def visit_Assign(self, node: ast.Assign):
        """Assignment - propagate type from value to targets."""
        self.visit(node.value)
        value_type = getattr(node.value, "_type", Unknown)
        for target in node.targets:
            target._type = value_type
            # Register variable type in scope for simple Name targets
            if isinstance(target, ast.Name):
                self._set_var_type(target.id, value_type)

    def visit_NamedExpr(self, node: ast.NamedExpr):
        """Walrus operator := - type is the value's type."""
        self.visit(node.value)
        self.visit(node.target)
        node._type = getattr(node.value, "_type", Unknown)

    # =========================================================================
    # Names and Calls
    # =========================================================================

    def visit_Name(self, node: ast.Name):
        """Name reference - get type from scope if loading."""
        match node.ctx:
            case ast.Load():
                # Look up variable type in scope
                node._type = self._get_var_type(node.id)
            case ast.Store():
                pass  # Type set by assignment
            case _:
                node._type = Unknown

    def visit_Call(self, node: ast.Call):
        """Function call - infer type from builtins, methods, or definition."""
        self.visit(node.func)
        self.visit_list(node.args)
        for keyword in node.keywords:
            self.visit(keyword.value)

        # Try to infer type from the call
        node._type = self._infer_call_type(node)

    def _infer_call_type(self, node: ast.Call) -> type:
        """Infer the return type of a function call."""
        func = node.func

        # Check for builtin function: name(...)
        if isinstance(func, ast.Name):
            builtin_type = BUILTIN_RETURN_TYPES.get(func.id)
            if builtin_type is not None:
                return builtin_type

            # Check for user-defined function with return type annotation
            # The function's type was set from its return annotation in visit_FunctionDef
            func_type = getattr(func, "_type", Unknown)
            if func_type is not Unknown:
                return func_type

        # Check for method call: expr.method(...)
        if isinstance(func, ast.Attribute):
            receiver_type = getattr(func.value, "_type", Unknown)
            method_name = func.attr
            method_type = METHOD_RETURN_TYPES.get((receiver_type, method_name))
            if method_type is not None:
                return method_type

        # Fall back to definition-based inference
        return self._type_from_definition(node)

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
        """Binary operation - infer from operands with proper type rules."""
        self.visit(node.left)
        self.visit(node.right)

        left_type = getattr(node.left, "_type", Unknown)
        right_type = getattr(node.right, "_type", Unknown)

        match node.op:
            case ast.Add():
                # Numeric promotion or string/list concatenation
                if left_type == Float or right_type == Float:
                    node._type = Float
                elif left_type == Int and right_type == Int:
                    node._type = Int
                elif left_type == String and right_type == String:
                    node._type = String
                elif left_type == List and right_type == List:
                    node._type = List
                else:
                    node._type = Unknown

            case ast.Sub():
                # Numeric only
                if left_type == Float or right_type == Float:
                    node._type = Float
                elif left_type == Int and right_type == Int:
                    node._type = Int
                else:
                    node._type = Unknown

            case ast.Mult():
                # Numeric or string/list repeat
                if left_type == Float or right_type == Float:
                    node._type = Float
                elif left_type == Int and right_type == Int:
                    node._type = Int
                elif (left_type == String and right_type == Int) or (
                    left_type == Int and right_type == String
                ):
                    node._type = String
                elif (left_type == List and right_type == Int) or (
                    left_type == Int and right_type == List
                ):
                    node._type = List
                else:
                    node._type = Unknown

            case ast.Div():
                # Division always produces float in Python 3
                node._type = Float

            case ast.FloorDiv():
                # Floor division preserves int if both int
                if left_type == Int and right_type == Int:
                    node._type = Int
                else:
                    node._type = Float

            case ast.Mod():
                # Modulo preserves int if both int, or string for formatting
                if left_type == String:
                    node._type = String  # String % tuple formatting
                elif left_type == Int and right_type == Int:
                    node._type = Int
                else:
                    node._type = Float

            case ast.Pow():
                # Power with float or negative exponent yields float
                if left_type == Float or right_type == Float:
                    node._type = Float
                elif left_type == Int and right_type == Int:
                    node._type = (
                        Int  # May actually overflow to float, but Int is reasonable
                    )
                else:
                    node._type = Unknown

            case ast.BitOr() | ast.BitXor() | ast.BitAnd():
                # Bitwise ops yield int
                if left_type == Int and right_type == Int:
                    node._type = Int
                elif left_type == Bool and right_type == Bool:
                    node._type = Bool
                else:
                    node._type = Unknown

            case ast.LShift() | ast.RShift():
                # Shift ops yield int
                if left_type == Int and right_type == Int:
                    node._type = Int
                else:
                    node._type = Unknown

            case ast.MatMult():
                # Matrix multiplication - type unknown without numpy support
                node._type = Unknown

            case _:
                node._type = Unknown

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
