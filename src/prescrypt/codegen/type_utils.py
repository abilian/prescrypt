"""Type utilities for code generation.

Provides helper functions to check AST node types and make codegen decisions.
"""

from __future__ import annotations

from prescrypt.front import ast
from prescrypt.front.passes.types import Bool, Float, Int, List, String, Unknown


def get_type(node):
    """Get the inferred type of an AST node.

    Returns Unknown if no type information is available.
    For Constant nodes, returns the type based on the value type.
    """
    # Check for existing type annotation from type inference pass
    if hasattr(node, "_type") and node._type is not None:
        return node._type

    # For constants, infer type directly from the value
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, bool):
            return Bool
        elif isinstance(value, int):
            return Int
        elif isinstance(value, float):
            return Float
        elif isinstance(value, str):
            return String

    return Unknown


def is_numeric(t) -> bool:
    """Check if type is numeric (Int, Float, or Bool).

    Bool is included because JavaScript treats booleans as numeric in arithmetic.
    """
    return t in (Int, Float, Bool)


def is_primitive(t) -> bool:
    """Check if type is a primitive (can use === for comparison)."""
    return t in (Int, Float, Bool, String)


def is_string(t) -> bool:
    """Check if type is String."""
    return t is String


def is_list(t) -> bool:
    """Check if type is List."""
    return t is List


def is_known(t) -> bool:
    """Check if type is known (not Unknown)."""
    return t is not Unknown
