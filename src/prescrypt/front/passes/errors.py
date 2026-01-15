"""Errors raised during frontend passes (binding, type checking)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prescrypt.exceptions import PrescryptError, SemanticError, SourceLocation

if TYPE_CHECKING:
    from prescrypt.front import ast


class BindError(SemanticError):
    """Error during binding/scope analysis."""


class TypeCheckError(PrescryptError):
    """Error during type checking."""


class UnknownSymbolError(BindError):
    """Reference to an undefined symbol."""

    def __init__(
        self,
        symbol: str,
        node: ast.AST | None = None,
        message: str | None = None,
    ):
        self.symbol = symbol
        msg = message or f"Unknown symbol: {symbol}"
        super().__init__(msg, node=node)


class StatementOutOfLoopError(BindError):
    """Break/continue statement outside of a loop."""

    def __init__(
        self,
        statement: str = "",
        node: ast.AST | None = None,
        message: str | None = None,
    ):
        self.statement = statement
        msg = message or f"'{statement}' not allowed outside of a loop"
        super().__init__(msg, node=node)


class UnknownTypeError(TypeCheckError):
    """Reference to an undefined type."""

    def __init__(
        self,
        type_name: str,
        node: ast.AST | None = None,
        message: str | None = None,
    ):
        self.type_name = type_name
        msg = message or f"Unknown type: {type_name}"
        super().__init__(msg, node=node)


class IncompatibleTypeError(TypeCheckError):
    """Type mismatch in an operation."""

    def __init__(
        self,
        type1: str,
        type2: str,
        node: ast.AST | None = None,
        message: str | None = None,
    ):
        self.type1 = type1
        self.type2 = type2
        msg = message or f"Incompatible types: {type1} and {type2}"
        super().__init__(msg, node=node)
