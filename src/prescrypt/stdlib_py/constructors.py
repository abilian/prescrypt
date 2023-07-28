from ..exceptions import JSError
from ..generator import gen_expr
from ..generator.stdlib import call_std_function
from ..utils import unify


#
# Contructors
#
def function_str(compiler, args, _kwargs):
    match args:
        case []:
            return '""'
        case [arg]:
            js_arg = unify(gen_expr(arg))
            return f"({js_arg}).toString()"
        case [*_]:
            return call_std_function("str", args)


def function_bool(compiler, args, _kwargs):
    match args:
        case []:
            return "false"
        case [_arg]:
            js_expr = call_std_function("truthy", args)
            return f"!!({js_expr})"
        case _:
            raise JSError("bool() at most one argument")


def function_int(compiler, args, _kwargs):
    match args:
        case []:
            return "0"
        case [arg]:
            js_arg = unify(gen_expr(arg))
            return f"parseInt({js_arg})"
        case _:
            raise JSError("int() at most one argument")


def function_float(compiler, args, _kwargs):
    match args:
        case []:
            return "0.0"
        case [arg]:
            js_arg = unify(gen_expr(arg))
            return f"parseFloat({js_arg})"
        case _:
            raise JSError("float() at most one argument")


def function_dict(compiler, args, kwargs):
    match args, kwargs:
        case [], []:
            return "({})"
        case [], [*_]:
            js_kwargs = [f"{arg.arg}: {unify(gen_expr(arg.value))}" for arg in kwargs]
            return "({%s})" % ", ".join(js_kwargs)
        case [*_], []:
            return call_std_function("dict", args)
        case _, _:
            # TODO
            raise JSError("dict() takes at most one argument")


def function_list(compiler, args, _kwargs):
    match args:
        case []:
            return "[]"
        case [*_]:
            js_args = [gen_expr(arg) for arg in args]
            return call_std_function("list", js_args)


def function_tuple(compiler, args, kwargs):
    return function_list(compiler, args, kwargs)
