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


def method_to_bytes(codegen: CodeGen, base, args, kwargs):
    """Handle int.to_bytes(length, byteorder, *, signed=False)."""
    # Extract keyword arguments
    signed = ast.Constant(False)
    for kw in kwargs:
        if kw.arg == "signed":
            signed = kw.value
    # Add signed to args for runtime function
    return codegen.call_std_method(base, "to_bytes", [*args, signed])


def method_from_bytes(codegen: CodeGen, base, args, kwargs):
    """Handle int.from_bytes(bytes, byteorder, *, signed=False)."""
    # Only handle int.from_bytes
    if base != "int":
        return None
    # Extract keyword arguments
    signed = ast.Constant(False)
    for kw in kwargs:
        if kw.arg == "signed":
            signed = kw.value
    # Call runtime function
    return codegen.call_std_function("int_from_bytes", [*args, signed])
