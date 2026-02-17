from __future__ import annotations

from prescrypt.codegen.main import CodeGen
from prescrypt.codegen.type_utils import get_type
from prescrypt.exceptions import JSError
from prescrypt.front.passes.types import Float, Int, String


#
# Contructors
#
def function_str(codegen: CodeGen, args, _kwargs):
    match args:
        case []:
            return '""'
        case [arg]:
            arg_type = get_type(arg)
            js_arg = codegen.gen_expr_unified(arg)

            if arg_type is String:
                # Already a string, return as-is
                return js_arg
            elif arg_type in (Int, Float):
                # Numeric (int/float): use String() for clean conversion
                return f"String({js_arg})"
            else:
                # Unknown or complex type (including booleans): use _pyfunc_str
                # for Python-style output (True/False instead of true/false)
                return codegen.call_std_function("str", args)
        case [bytes_arg, encoding]:
            # str(bytes, encoding) - decode bytes to string
            return codegen.call_std_function("str_decode", args)
        case [bytes_arg, encoding, _errors]:
            # str(bytes, encoding, errors) - decode with error handling
            # For now, ignore errors parameter
            return codegen.call_std_function("str_decode", [bytes_arg, encoding])
        case _:
            # Too many arguments - generate runtime TypeError
            return codegen.call_std_function("str_error_args", args)


def function_bool(codegen: CodeGen, args, _kwargs):
    match args:
        case []:
            return "false"
        case [_arg]:
            js_expr = codegen.call_std_function("truthy", args)
            return f"!!({js_expr})"
        case _:
            msg = "bool() at most one argument"
            raise JSError(msg)


def function_int(codegen: CodeGen, args, _kwargs):
    match args:
        case []:
            return "0"
        case [arg]:
            # Use stdlib int() which handles booleans, strings, and numbers properly
            return codegen.call_std_function("int", args)
        case [arg, base]:
            # int(x, base) - e.g., int('ff', 16)
            return codegen.call_std_function("int", args)
        case _:
            msg = "int() takes at most 2 arguments"
            raise JSError(msg)


def function_float(codegen: CodeGen, args, _kwargs):
    match args:
        case []:
            return "0.0"
        case [arg]:
            # Use stdlib float() which handles 'inf', '-inf', 'nan' properly
            return codegen.call_std_function("float", args)
        case _:
            msg = "float() at most one argument"
            raise JSError(msg)


def function_dict(codegen: CodeGen, args, kwargs):
    match args, kwargs:
        case [], []:
            return "({})"
        case [], [*_]:
            js_kwargs = [
                f"{kw.arg}: {codegen.gen_expr_unified(kw.value)}" for kw in kwargs
            ]
            return "({%s})" % ", ".join(js_kwargs)
        case [arg], []:
            return codegen.call_std_function("dict", args)
        case [arg], [*_]:
            # dict({1:2}, a=3) or dict([(1,2)], a=3)
            # Merge positional arg with kwargs using Object.assign
            js_arg = codegen.call_std_function("dict", [arg])
            js_kwargs = [
                f"{kw.arg}: {codegen.gen_expr_unified(kw.value)}" for kw in kwargs
            ]
            return f"Object.assign({js_arg}, {{{', '.join(js_kwargs)}}})"
        case _:
            msg = "dict() takes at most one positional argument"
            raise JSError(msg)


def function_list(codegen: CodeGen, args, _kwargs):
    match args:
        case []:
            return "[]"
        case [*_]:
            js_args = [codegen.gen_expr_unified(arg) for arg in args]
            return codegen.call_std_function("list", js_args)


def function_tuple(codegen: CodeGen, args, kwargs):
    return function_list(codegen, args, kwargs)


def function_set(codegen: CodeGen, args, _kwargs):
    match args:
        case []:
            return "new Set()"
        case [arg]:
            js_arg = codegen.gen_expr_unified(arg)
            return f"new Set({js_arg})"
        case _:
            msg = "set() takes at most one argument"
            raise JSError(msg)


def function_bytes(codegen: CodeGen, args, _kwargs):
    """Handle bytes() constructor.

    Forms:
    - bytes() -> empty bytes
    - bytes(n) -> n zero bytes
    - bytes(iterable) -> bytes from iterable of ints
    - bytes(bytes_obj) -> copy of bytes
    - bytes(string, encoding) -> encode string
    - bytes(string, encoding, errors) -> encode with error handling
    """
    match args:
        case []:
            return "new Uint8Array()"
        case [arg]:
            # bytes(source) - could be int, bytes, or iterable
            return codegen.call_std_function("bytes", args)
        case [string_arg, encoding]:
            # bytes(string, encoding)
            return codegen.call_std_function("bytes_encode", args)
        case [string_arg, encoding, errors]:
            # bytes(string, encoding, errors) - ignore errors for now
            return codegen.call_std_function("bytes_encode", [string_arg, encoding])
        case _:
            # Too many arguments
            return codegen.call_std_function("bytes_error_args", args)
