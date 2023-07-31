from prescrypt.ast import ast
from prescrypt.exceptions import JSError


#
# Methods of builtin types
#
def method_sort(compiler, args, kwargs, base):
    if len(args) == 0:  # sorts args are keyword-only
        key, reverse = ast.Name("undefined"), ast.NameConstant(False)
        for kw in kwargs:
            if kw.name == "key":
                key = kw.value_node
            elif kw.name == "reverse":
                reverse = kw.value_node
            else:
                raise JSError(f"Invalid keyword argument for sort: {kw.name!r}")
        return compiler.call_std_method(base, "sort", [key, reverse])


def method_format(compiler, args, kwargs, base):
    if kwargs:
        raise JSError("Method format() currently does not support keyword args.")

    return compiler.call_std_method(base, "format", args)
