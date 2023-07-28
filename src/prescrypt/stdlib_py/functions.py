import ast

from ..exceptions import JSError
from ..utils import flatten, unify


#
# Other builtin functions
#
def function_isinstance(compiler, args, kwargs):
    if len(args) != 2:
        raise JSError("isinstance() expects two arguments.")

    ob = unify(compiler.gen_expr(args[0]))
    cls = unify(compiler.gen_expr(args[1]))
    if cls[0] in "\"'":
        cls = cls[1:-1]  # remove quotes

    BASIC_TYPES = (
        "number",
        "boolean",
        "string",
        "function",
        "array",
        "object",
        "null",
        "undefined",
    )

    MAP = {
        "[int, float]": "number",
        "[float, int]": "number",
        "float": "number",
        "str": "string",
        "bool": "boolean",
        "FunctionType": "function",
        "types.FunctionType": "function",
        "list": "array",
        "tuple": "array",
        "[list, tuple]": "array",
        "[tuple, list]": "array",
        "dict": "object",
    }

    cmp = MAP.get(cls, cls)

    if cmp == "array":
        return ["Array.isArray(", ob, ")"]
    elif cmp.lower() in BASIC_TYPES:
        # Basic type, use Object.prototype.toString
        return [
            "Object.prototype.toString.call(",
            ob,
            f").slice(8,-1).toLowerCase() === '{cmp.lower()}'",
        ]
        # In http://stackoverflow.com/questions/11108877 the following is
        # proposed, which might be better in theory, but is > 50% slower
        return [
            "({}).toString.call(",
            ob,
            r").match(/\s([a-zA-Z]+)/)[1].toLowerCase() === ",
            f"'{cmp.lower()}'",
        ]
    else:
        # User defined type, use instanceof
        # http://tobyho.com/2011/01/28/checking-types-in-javascript/
        cmp = unify(cls)
        if cmp[0] == "(":
            raise JSError("isinstance() can only compare to simple types")
        return ob, " instanceof ", cmp


def function_issubclass(compiler, args, kwargs):
    # issubclass only needs to work on custom classes
    if len(args) != 2:
        raise JSError("issubclass() expects two arguments.")

    cls1 = unify(compiler.gen_expr(args[0]))
    cls2 = unify(compiler.gen_expr(args[1]))
    if cls2 == "object":
        cls2 = "Object"
    return f"({cls1}.prototype instanceof {cls2})"


def function_print(compiler, args, kwargs):
    # Process keywords
    sep, end = '" "', ""
    for kw in kwargs:
        if kw.name == "sep":
            sep = flatten(compiler.gen_expr(kw.value))
        elif kw.name == "end":
            end = flatten(compiler.gen_expr(kw.value))
        elif kw.name in ("file", "flush"):
            raise JSError("print() file and flush args not supported")
        else:
            raise JSError(f"Invalid argument for print(): {kw.name!r}")

    # Combine args
    js_args = [unify(compiler.gen_expr(arg)) for arg in args]
    end = f" + {end}" if (js_args and end and end != "\n") else ""
    combiner = f" + {sep} + "
    args_concat = combiner.join(js_args) or '""'
    return "console.log(" + args_concat + end + ")"


def function_len(compiler, args, kwargs):
    match args:
        case [arg]:
            js_arg = unify(compiler.gen_expr(arg))
            return f"{js_arg}.length"
        case _:
            raise JSError("len() needs exactly one argument")


def function_max(compiler, args, kwargs):
    match args:
        case []:
            raise JSError("max() needs at least one argument")
        case [arg]:
            js_arg = flatten(compiler.gen_expr(arg))
            return f"Math.max.apply(null, {js_arg})"
        case [*_]:
            js_args = ", ".join([unify(compiler.gen_expr(arg)) for arg in args])
            return f"Math.max({js_args})"


def function_min(compiler, args, kwargs):
    match args:
        case []:
            raise JSError("min() needs at least one argument")
        case [arg]:
            js_arg = flatten(compiler.gen_expr(arg))
            return f"Math.min.apply(null, {js_arg})"
        case [*_]:
            js_args = ", ".join([unify(compiler.gen_expr(arg)) for arg in args])
            return f"Math.min({js_args})"


def function_callable(compiler, args, kwargs):
    match args:
        case [arg]:
            js_arg = unify(compiler.gen_expr(arg))
            return f'(typeof {js_arg} === "function")'
        case _:
            raise JSError("callable() needs exactly one argument")


def function_chr(compiler, args, kwargs) -> str:
    match args:
        case [arg]:
            js_arg = flatten(compiler.gen_expr(arg))
            return f"String.fromCharCode({js_arg})"
        case _:
            raise JSError("chr() needs exactly one argument")


def function_ord(compiler, args, kwargs) -> str:
    match args:
        case [arg]:
            js_arg = flatten(compiler.gen_expr(arg))
            return f"{js_arg}.charCodeAt(0)"
        case _:
            raise JSError("ord() exactly one argument")


def function_range(compiler, args, kwargs):
    match args:
        case [a]:
            args = ast.Num(0), a, ast.Num(1)
            return compiler.call_std_function("range", args)
        case [a, b]:
            args = a, b, ast.Num(1)
            return compiler.call_std_function("range", args)
        case [a, b, c]:
            return compiler.call_std_function("range", args)
        case _:
            raise JSError("range() needs 1, 2 or 3 arguments")


def function_sorted(compiler, args, kwargs):
    if len(args) != 1:
        raise JSError("sorted() needs one argument")

    key, reverse = "undefined", ast.NameConstant(False)
    for kw in kwargs:
        if kw.name == "key":
            key = kw.value
        elif kw.name == "reverse":
            reverse = kw.value
        else:
            raise JSError(f"Invalid keyword argument for sorted: {kw.name!r}")

    return compiler.call_std_function("sorted", [args[0], key, reverse])
