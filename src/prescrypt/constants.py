from __future__ import annotations

import re

from . import stdlib_js
from .front import ast

# Not needed ?
# NAME_MAP = {
#     # "True": "true",
#     # "False": "false",
#     # "None": "null",
#     # "unicode": "str",  # legacy Py compat
#     # "unichr": "chr",
#     # "xrange": "range",
#     # "self": "this",
# }

ATTRIBUTE_MAP = {
    "__class__": "Object.getPrototypeOf({})",
}

_BINARY_OP = {
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Div: "/",
    ast.Mod: "%",
    ast.LShift: "<<",
    ast.RShift: ">>",
    ast.BitOr: "|",
    ast.BitXor: "^",
    ast.BitAnd: "&",
}

_UNARY_OP = {
    ast.Invert: "~",
    ast.Not: "!",
    ast.UAdd: "+",
    ast.USub: "-",
}

_BOOL_OP = {
    ast.And: "&&",
    ast.Or: "||",
}

_COMP_OP = {
    ast.Eq: "==",
    ast.NotEq: "!=",
    ast.Lt: "<",
    ast.LtE: "<=",
    ast.Gt: ">",
    ast.GtE: ">=",
    ast.Is: "===",
    ast.IsNot: "!==",
}


class Map:
    def __init__(self, mapping):
        self.mapping = mapping

    def __getitem__(self, key):
        return self.mapping[type(key)]


BINARY_OP = Map(_BINARY_OP)
UNARY_OP = Map(_UNARY_OP)
BOOL_OP = Map(_BOOL_OP)
COMP_OP = Map(_COMP_OP)


# precompile regexp to help determine whether a string is an identifier
ISIDENTIFIER1 = re.compile(r"^\w+$", re.UNICODE)
isidentifier1 = ISIDENTIFIER1

JS_RESERVED_NAMES = (
    "abstract",
    "instanceof",
    "boolean",
    "enum",
    "switch",
    "export",
    "interface",
    "synchronized",
    "extends",
    "let",
    "case",
    "throw",
    "catch",
    "final",
    "native",
    "throws",
    "new",
    "transient",
    "const",
    "package",
    "function",
    "private",
    "typeof",
    "debugger",
    "goto",
    "protected",
    "var",
    "default",
    "public",
    "void",
    "delete",
    "implements",
    "volatile",
    "do",
    "static",
    # Commented, because are disallowed in Python too.
    # 'else', 'break', 'finally', 'class', 'for', 'try', 'continue', 'if',
    # 'return', 'import', 'while', 'in', 'with',
    # Commented for pragmatic reasons
    # 'super', 'float', 'this', 'int', 'byte', 'long', 'char', 'short',
    # 'double', 'null', 'true', 'false',
)

# Define builtin stuff for which we know that it returns a bool or int
_bool_funcs = (
    "hasattr",
    "all",
    "any",
    "op_contains",
    "op_equals",
    "truthy",
)
_bool_meths = (
    "count",
    "isalnum",
    "isalpha",
    "isidentifier",
    "islower",
    "isnumeric",
    "isdigit",
    "isdecimal",
    "isspace",
    "istitle",
    "isupper",
    "startswith",
)
RETURNING_BOOL = tuple(
    [stdlib_js.FUNCTION_PREFIX + x + "(" for x in _bool_funcs]
    + [stdlib_js.METHOD_PREFIX + x + "." for x in _bool_meths]
)
