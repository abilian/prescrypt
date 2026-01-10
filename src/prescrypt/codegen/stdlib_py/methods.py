from __future__ import annotations

from prescrypt.codegen import CodeGen
from prescrypt.exceptions import JSError
from prescrypt.front import ast


#
# Methods of builtin types
#
def method_sort(codegen: CodeGen, base, args, kwargs):
    if len(args) != 0:  # sorts args are keyword-only
        raise JSError("Method sort() is keyword-only.")

    key, reverse = ast.Name("undefined"), ast.Constant(False)
    for kw in kwargs:
        if kw.arg == "key":
            key = kw.value
        elif kw.arg == "reverse":
            reverse = kw.value
        else:
            raise JSError(f"Invalid keyword argument for sort: {kw.arg!r}")

    return codegen.call_std_method(base, "sort", [key, reverse])


def method_format(codegen: CodeGen, base, args, kwargs):
    if kwargs:
        raise JSError("Method format() currently does not support keyword args.")

    return codegen.call_std_method(base, "format", args)
