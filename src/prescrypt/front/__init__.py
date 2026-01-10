"""
Frontend of the compiler (actually, middle-end, since the parser is just CPython's parser).

AST, scopes, binder, type checker, etc.

Everything that happens after parsing and before code generation.
"""
from __future__ import annotations

from .ast import ast
from .ast.scope import Scope, Variable
from .front import to_ast

__all__ = ["ast", "Scope", "Variable", "to_ast"]
