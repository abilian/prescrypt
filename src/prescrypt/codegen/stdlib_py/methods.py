from __future__ import annotations

from prescrypt.codegen import CodeGen
from prescrypt.exceptions import JSError
from prescrypt.front import ast


#
# Methods of builtin types
#
def method_sort(codegen: CodeGen, base, args, kwargs):
    if len(args) != 0:  # sorts args are keyword-only
        msg = "Method sort() is keyword-only."
        raise JSError(msg)

    key, reverse = ast.Name("undefined"), ast.Constant(False)
    for kw in kwargs:
        if kw.arg == "key":
            key = kw.value
        elif kw.arg == "reverse":
            reverse = kw.value
        else:
            msg = f"Invalid keyword argument for sort: {kw.arg!r}"
            raise JSError(msg)

    return codegen.call_std_method(base, "sort", [key, reverse])


def method_format(codegen: CodeGen, base, args, kwargs):
    if kwargs:
        msg = "Method format() currently does not support keyword args."
        raise JSError(msg)

    return codegen.call_std_method(base, "format", args)
