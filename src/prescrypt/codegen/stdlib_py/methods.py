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


def method_send(codegen: CodeGen, base, args, kwargs):
    """Handle generator.send(value).

    Uses runtime _pymeth_send which:
    - Validates first call must be None
    - Unwraps JS generator result {value, done} to just value
    - Raises StopIteration when done
    """
    if kwargs:
        return None  # Let runtime handle unexpected kwargs
    return codegen.call_std_method(base, "send", args)


def method_throw(codegen: CodeGen, base, args, kwargs):
    """Handle generator.throw(type[, value[, traceback]]).

    Uses runtime _pymeth_gen_throw which:
    - Creates exception from type/value
    - Calls JS generator.throw()
    - Unwraps result or propagates exception
    """
    if kwargs:
        return None  # Let runtime handle unexpected kwargs
    # Use gen_throw to avoid JS reserved word issue
    return codegen.call_std_method(base, "gen_throw", args)


def method_close(codegen: CodeGen, base, args, kwargs):
    """Handle generator.close().

    Uses runtime _pymeth_gen_close which:
    - Throws GeneratorExit into the generator
    - Handles StopIteration/GeneratorExit silently
    - Raises RuntimeError if generator yields a value

    Note: Only applies to non-self calls to avoid intercepting
    user-defined .close() methods on classes.
    """
    if kwargs or args:
        return None  # close() takes no arguments
    # Don't intercept self.close() - that's likely a user-defined method
    if base in ("self", "this"):
        return None
    # Use gen_close to avoid conflicts with other close methods
    return codegen.call_std_method(base, "gen_close", [])
