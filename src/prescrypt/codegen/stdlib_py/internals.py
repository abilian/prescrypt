from __future__ import annotations

from prescrypt.exceptions import JSError
from prescrypt.front import ast


def function_this_is_js(compiler, args):
    # Note that we handle this_is_js() shortcuts in the if-statement
    # directly. This replacement with a string is when this_is_js()
    # is used outside an if statement.
    if len(args) != 0:
        msg = "this_is_js() expects zero arguments."
        raise JSError(msg)
    return '"this_is_js()"'


def function_RawJS(compiler, args):
    if len(args) != 1:
        return None  # maybe RawJS is a thing

    if not isinstance(args[0], ast.Str):
        msg = (
            "RawJS needs a verbatim string (use multiple "
            "args to bypass PScript's RawJS)."
        )
        raise JSError(msg)

    lines = RawJS._str2lines(node.arg_nodes[0].value.strip())
    nl = "\n" + (compiler._indent * 4) * " "
    return nl.join(lines)
