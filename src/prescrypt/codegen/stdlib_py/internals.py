from prescrypt.ast import ast
from prescrypt.exceptions import JSError


def function_this_is_js(compiler, args):
    # Note that we handle this_is_js() shortcuts in the if-statement
    # directly. This replacement with a string is when this_is_js()
    # is used outside an if statement.
    if len(args) != 0:
        raise JSError("this_is_js() expects zero arguments.")
    return '"this_is_js()"'


def function_RawJS(compiler, args):
    if len(args) != 1:
        return None  # maybe RawJS is a thing

    if not isinstance(args[0], ast.Str):
        raise JSError(
            "RawJS needs a verbatim string (use multiple "
            "args to bypass PScript's RawJS)."
        )

    lines = RawJS._str2lines(node.arg_nodes[0].value.strip())
    nl = "\n" + (compiler._indent * 4) * " "
    return nl.join(lines)
