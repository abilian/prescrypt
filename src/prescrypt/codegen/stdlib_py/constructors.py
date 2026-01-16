from __future__ import annotations

from prescrypt.codegen.main import CodeGen
from prescrypt.codegen.type_utils import get_type, is_numeric, is_primitive
from prescrypt.codegen.utils import unify
from prescrypt.exceptions import JSError
from prescrypt.front.passes.types import Bool, String


#
# Contructors
#
def function_str(codegen: CodeGen, args, _kwargs):
    match args:
        case []:
            return '""'
        case [arg]:
            arg_type = get_type(arg)
            js_arg = unify(codegen.gen_expr(arg))

            if arg_type is String:
                # Already a string, return as-is
                return js_arg
            elif is_numeric(arg_type) or arg_type is Bool:
                # Numeric or bool: use String() for clean conversion
                return f"String({js_arg})"
            else:
                # Unknown or complex type: use _pyfunc_str for Python-style output
                return codegen.call_std_function("str", args)
        case _:
            raise JSError("str() at most one argument")


def function_bool(codegen: CodeGen, args, _kwargs):
    match args:
        case []:
            return "false"
        case [_arg]:
            js_expr = codegen.call_std_function("truthy", args)
            return f"!!({js_expr})"
        case _:
            raise JSError("bool() at most one argument")


def function_int(codegen: CodeGen, args, _kwargs):
    match args:
        case []:
            return "0"
        case [arg]:
            js_arg = unify(codegen.gen_expr(arg))
            return f"parseInt({js_arg})"
        case _:
            raise JSError("int() at most one argument")


def function_float(codegen: CodeGen, args, _kwargs):
    match args:
        case []:
            return "0.0"
        case [arg]:
            js_arg = unify(codegen.gen_expr(arg))
            return f"parseFloat({js_arg})"
        case _:
            raise JSError("float() at most one argument")


def function_dict(codegen: CodeGen, args, kwargs):
    match args, kwargs:
        case [], []:
            return "({})"
        case [], [*_]:
            js_kwargs = [
                f"{arg.arg}: {unify(codegen.gen_expr(arg.value))}" for arg in kwargs
            ]
            return "({%s})" % ", ".join(js_kwargs)
        case [*_], []:
            return codegen.call_std_function("dict", args)
        case _, _:
            # TODO
            raise JSError("dict() takes at most one argument")


def function_list(codegen: CodeGen, args, _kwargs):
    match args:
        case []:
            return "[]"
        case [*_]:
            js_args = [codegen.gen_expr(arg) for arg in args]
            return codegen.call_std_function("list", js_args)


def function_tuple(codegen: CodeGen, args, kwargs):
    return function_list(codegen, args, kwargs)
