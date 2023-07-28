#
# Using stdlib
#
from prescrypt.ast import ast
from prescrypt.generator import gen_expr
from prescrypt.stdlib_js import FUNCTION_PREFIX, METHOD_PREFIX
from prescrypt.utils import unify


def call_std_function(name: str, args: list[str | ast.expr]) -> str:
    """Generate a function call from the Prescrypt standard library."""
    mangled_name = FUNCTION_PREFIX + name
    js_args = [(a if isinstance(a, str) else unify(gen_expr(a))) for a in args]
    return f"{mangled_name}({', '.join(js_args)})"


def call_std_method(base, name: str, args: list) -> str:
    """Generate a method call from the Prescrypt standard library."""
    mangled_name = METHOD_PREFIX + name
    js_args = [(a if isinstance(a, str) else unify(gen_expr(a))) for a in args]
    args.insert(0, base)
    return f"{mangled_name}.call({', '.join(js_args)})"
