import re

from prescrypt.ast import ast
from prescrypt.stdlib_js import FUNCTION_PREFIX
from prescrypt.utils import unify

from ..constants import RETURNING_BOOL
from ..exceptions import JSError
from .context import ctx
from .stdlib import call_std_function
from . import gen_expr


#
# Utility functions
#
def gen_truthy(node: ast.expr) -> str | list:
    """Wraps an operation in a truthy call, unless it's not necessary."""
    eq_name = FUNCTION_PREFIX + "op_equals"
    test = "".join(gen_expr(node))
    if not ctx._pscript_overload:
        return unify(test)
    elif (
        test.endswith(".length")
        or test.startswith("!")
        or test.isnumeric()
        or test == "true"
        or test == "false"
        or test.count("==")
        or test.count(">")
        or test.count("<")
        or test.count(eq_name)
        or test == '"this_is_js()"'
        or test.startswith("Array.isArray(")
        or (test.startswith(RETURNING_BOOL) and "||" not in test)
    ):
        return unify(test)
    else:
        return call_std_function("truthy", [test])


def _format_string(self, left, right):
    """Format a string using the old-school `%` operator."""

    # Get value_nodes
    if isinstance(right, (ast.Tuple, ast.List)):
        value_nodes = right.elts
    else:
        value_nodes = [right]

    # Is the left side a string? If not, exit early
    # This works, but we cannot know whether the left was a string or number :P
    # if not isinstance(node.left_node, ast.Str):
    #     thestring = unify(self.parse(node.left_node))
    #     thestring += ".replace(/%([0-9\.\+\-\#]*[srdeEfgGioxXc])/g, '{:$1}')"
    #     return self.use_std_method(thestring, 'format', value_nodes)

    assert isinstance(left, ast.Str)
    js_left = "".join(self.gen_expr(left))
    sep, js_left = js_left[0], js_left[1:-1]

    # Get matches
    matches = list(re.finditer(r"%[0-9.+#-]*[srdeEfgGioxXc]", js_left))
    if len(matches) != len(value_nodes):
        raise JSError(
            "In string formatting, number of placeholders "
            "does not match number of replacements"
        )
    # Format
    parts = []
    start = 0
    for m in matches:
        fmt = m.group(0)
        fmt = {"%r": "!r", "%s": ""}.get(fmt, ":" + fmt[1:])
        # Add the part in front of the match (and after prev match)
        parts.append(left[start : m.start()])
        parts.append("{%s}" % fmt)
        start = m.end()
    parts.append(left[start:])
    thestring = sep + "".join(parts) + sep
    return self.call_std_method(thestring, "format", value_nodes)
