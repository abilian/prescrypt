from __future__ import annotations

from prescrypt.codegen import CodeGen
from prescrypt.exceptions import JSError
from prescrypt.front import ast


#
# Methods of builtin types
#
def method_sort(codegen: CodeGen, base, args, kwargs):
    if len(args) != 0:
        # Positional args to sort() - Python raises TypeError at runtime
        # Let it compile and fail at runtime
        return codegen.call_std_method(base, "sort", args)

    key, reverse = ast.Name("undefined"), ast.Constant(False)
    for kw in kwargs:
        if kw.arg == "key":
            key = kw.value
        elif kw.arg == "reverse":
            reverse = kw.value
        else:
            # Unknown kwarg - let runtime handle it
            return codegen.call_std_method(base, "sort", [key, reverse])

    return codegen.call_std_method(base, "sort", [key, reverse])


def method_format(codegen: CodeGen, base, args, kwargs):
    # Pass through to runtime - it handles both positional and keyword args
    return codegen.call_std_method(base, "format", args)
