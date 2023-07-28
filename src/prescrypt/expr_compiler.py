from .ast import ast
from .base_compiler import BaseCompiler
from .generator import gen_expr
from .utils import flatten


class ExpressionCompiler(BaseCompiler):
    """
    + Constant(constant value, string? kind)
    + List(expr* elts, expr_context ctx)
    + Tuple(expr* elts, expr_context ctx)
    + Dict(expr* keys, expr* values)
    + Set(expr* elts)

    + BoolOp(boolop op, expr* values)
    + UnaryOp(unaryop op, expr operand)
    + BinOp(expr left, operator op, expr right)
    + Compare(expr left, cmpop* ops, expr* comparators)
    + Call(expr func, expr* args, keyword* keywords)

    + JoinedStr(expr* values)
    + Name(identifier id, expr_context ctx)
    + Attribute(expr value, identifier attr, expr_context ctx)
    + IfExp(expr test, expr body, expr orelse)

    - Lambda(arguments args, expr body)

    - ListComp(expr elt, comprehension* generators)
    - SetComp(expr elt, comprehension* generators)
    - DictComp(expr key, expr value, comprehension* generators)
    - GeneratorExp(expr elt, comprehension* generators)

    - NamedExpr(expr target, expr value)
    - Await(expr value)
    - Yield(expr? value)
    - YieldFrom(expr value)
    - FormattedValue(expr value, int conversion, expr? format_spec)
    - Subscript(expr value, expr slice, expr_context ctx)
    - Starred(expr value, expr_context ctx)
    - Slice(expr? lower, expr? upper, expr? step)
    """

    def __init__(self, *args, **kwargs):
        # Temp
        self._pscript_overload = False
        self._methods = {}
        self._functions = {}
        self._seen_func_names = set()
        self._seen_class_names = set()
        self._std_methods = set()
        self._stack = []

    def gen_expr(self, expr_node: ast.expr) -> str:
        assert isinstance(expr_node, ast.expr), expr_node
        code = gen_expr(expr_node)
        return flatten(code)
