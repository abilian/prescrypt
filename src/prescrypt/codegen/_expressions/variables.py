from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_expr
from prescrypt.constants import JS_RESERVED_NAMES
from prescrypt.exceptions import JSError
from prescrypt.front import ast

# Type identifiers - map Python type names to stdlib type functions
TYPE_IDENTIFIERS = {
    "int": "type_int",
    "float": "type_float",
    "str": "type_str",
    "bool": "type_bool",
    "list": "type_list",
    "tuple": "type_tuple",
    "dict": "type_dict",
    "set": "type_set",
    "bytes": "type_bytes",
    "object": "type_object",
    "type": "type_type",
}

# Exception types - map Python exception names to stdlib exception functions
EXCEPTION_TYPES = {
    "BaseException": "BaseException",
    "Exception": "Exception",
    "StopIteration": "StopIteration",
    "GeneratorExit": "GeneratorExit",
    "ValueError": "ValueError",
    "IndexError": "IndexError",
    "KeyError": "KeyError",
    "AttributeError": "AttributeError",
    "TypeError": "TypeError_py",  # Avoid conflict with JS TypeError
    "RuntimeError": "RuntimeError",
    "NameError": "NameError",
}

# Builtin names - map Python builtin names to stdlib functions
BUILTIN_NAMES = {
    "NotImplemented": "NotImplemented",
    "len": "op_len",
    "hex": "hex",
    "bin": "bin",
    "oct": "oct",
    "abs": "abs",
    "hash": "hash",
    "id": "id",
    "next": "next",
    "zip": "zip",
    "map": "map",
    "filter": "filter",
    "iter": "iter",
    "getattr": "getattr",
    "hasattr": "hasattr",
    "setattr": "setattr",
    "delattr": "delattr",
    "dir": "dir",
    "callable": "callable",
}


@gen_expr.register
def gen_name(node: ast.Name, codegen: CodeGen) -> str:
    name = node.id

    # Convert Python's self to JavaScript's this
    if name == "self":
        return "this"

    # Rename 'super' when used as a regular variable (not the builtin)
    # JavaScript reserves 'super' as a keyword
    if name == "super" and codegen.ns.is_known(name):
        return "_super"

    # Handle Ellipsis builtin - reference the stdlib constant
    if name == "Ellipsis":
        codegen._used_std_functions.add("Ellipsis")
        return codegen.function_prefix + "Ellipsis"

    # Handle type identifiers (int, str, list, etc.)
    if name in TYPE_IDENTIFIERS:
        stdlib_name = TYPE_IDENTIFIERS[name]
        codegen._used_std_functions.add(stdlib_name)
        return codegen.function_prefix + stdlib_name

    # Handle exception types
    if name in EXCEPTION_TYPES:
        stdlib_name = EXCEPTION_TYPES[name]
        codegen._used_std_functions.add(stdlib_name)
        return codegen.function_prefix + stdlib_name

    # Handle builtin names
    if name in BUILTIN_NAMES:
        stdlib_name = BUILTIN_NAMES[name]
        codegen._used_std_functions.add(stdlib_name)
        return codegen.function_prefix + stdlib_name

    if name in JS_RESERVED_NAMES:
        msg = f"Cannot use reserved name '{name}' as a variable name"
        raise JSError(msg, node)

    # TODO:
    if codegen.ns.is_known(name):
        return codegen.with_prefix(name)

    # if self._scope_prefix:
    #     for stackitem in reversed(self._stack):
    #         scope = stackitem[2]
    #         for prefix in reversed(self._scope_prefix):
    #             prefixed_name = prefix + name
    #             if prefixed_name in scope:
    #                 return prefixed_name

    # if name in NAME_MAP:
    #     return NAME_MAP[name]

    # if name in self._functions or name in ("undefined", "window"):
    #     return name

    # mark as used (not defined)
    # used_name = (name + "." + fullname) if fullname else name
    # self.vars.use(name, used_name)

    return name
