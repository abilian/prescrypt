from typing import Iterator

from devtools import debug

from prescrypt.ast import ast
from prescrypt.stdlib_js import FUNCTION_PREFIX, METHOD_PREFIX
from prescrypt.utils import unify

from . import gen_expr


def call_std_function(name: str, args: list[str | ast.expr]) -> str:
    """Generate a function call from the Prescrypt standard library."""
    mangled_name = FUNCTION_PREFIX + name
    return f"{mangled_name}({', '.join(gen_js_args(args))})"


def call_std_method(base, name: str, args: list) -> str:
    """Generate a method call from the Prescrypt standard library."""
    mangled_name = METHOD_PREFIX + name
    js_args = list(gen_js_args(args))
    # FIXME: what does this do?
    # args.insert(0, base)
    return f"{mangled_name}.call({', '.join(js_args)})"


def gen_js_args(args) -> Iterator[str]:
    for arg in args:
        if isinstance(arg, str):
            yield arg
        else:
            debug(arg, gen_expr(arg))
            yield unify(gen_expr(arg))
