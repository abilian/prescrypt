"""Lambda expression handler.

Converts Python lambda expressions to JavaScript arrow functions.
"""

from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_expr
from prescrypt.codegen.utils import flatten
from prescrypt.exceptions import JSError
from prescrypt.front import ast


@gen_expr.register
def gen_lambda(node: ast.Lambda, codegen: CodeGen) -> str:
    """Generate JavaScript arrow function from Python lambda.

    Python: lambda x, y=1: x + y
    JavaScript: (x, y = 1) => (x + y)
    """
    params = gen_lambda_params(node.args, codegen)
    body = flatten(codegen.gen_expr(node.body))

    return f"({params}) => ({body})"


def gen_lambda_params(args: ast.arguments, codegen: CodeGen) -> str:
    """Generate parameter list for lambda/arrow function.

    Handles:
    - Regular parameters: lambda x, y: ...
    - Default values: lambda x, y=1: ...
    - *args: lambda *args: ...
    - Keyword-only args: lambda *, x, y: ...
    """
    parts = []

    # Regular positional args
    num_defaults = len(args.defaults)
    num_args = len(args.args)

    for i, arg in enumerate(args.args):
        name = arg.arg
        # Check for default value
        default_idx = i - (num_args - num_defaults)
        if default_idx >= 0:
            default = flatten(codegen.gen_expr(args.defaults[default_idx]))
            parts.append(f"{name} = {default}")
        else:
            parts.append(name)

    # *args (vararg)
    if args.vararg:
        parts.append(f"...{args.vararg.arg}")

    # Keyword-only args (after *)
    if args.kwonlyargs:
        num_kw_defaults = len(args.kw_defaults)
        for i, arg in enumerate(args.kwonlyargs):
            name = arg.arg
            # kw_defaults may contain None for args without defaults
            if i < len(args.kw_defaults) and args.kw_defaults[i] is not None:
                default = flatten(codegen.gen_expr(args.kw_defaults[i]))
                parts.append(f"{name} = {default}")
            else:
                parts.append(name)

    # **kwargs - not directly supported in arrow functions
    if args.kwarg:
        msg = (
            f"**{args.kwarg.arg} in lambda is not supported. "
            "Use a regular function instead."
        )
        raise JSError(msg)

    return ", ".join(parts)
