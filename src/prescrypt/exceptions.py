"""Prescrypt error types with source location support."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prescrypt.front import ast


@dataclass
class SourceLocation:
    """Source code location for error reporting."""

    file: str | None = None
    line: int = 0
    column: int = 0
    end_line: int | None = None
    end_column: int | None = None

    @classmethod
    def from_node(cls, node: ast.AST, file: str | None = None) -> SourceLocation:
        """Create location from an AST node."""
        return cls(
            file=file,
            line=getattr(node, "lineno", 0),
            column=getattr(node, "col_offset", 0),
            end_line=getattr(node, "end_lineno", None),
            end_column=getattr(node, "end_col_offset", None),
        )

    def __str__(self) -> str:
        if self.file:
            return f"{self.file}:{self.line}:{self.column}"
        return f"{self.line}:{self.column}"


class PrescryptError(Exception):
    """Base class for all Prescrypt errors with optional source location."""

    def __init__(
        self,
        message: str,
        node: ast.AST | None = None,
        location: SourceLocation | None = None,
    ):
        self.message = message
        # Location can be provided directly or extracted from node
        if location:
            self.location = location
        elif node:
            self.location = SourceLocation.from_node(node)
        else:
            self.location = None
        super().__init__(self.format())

    def format(self) -> str:
        """Format error message with location if available."""
        if self.location and self.location.line > 0:
            return f"{self.location}: error: {self.message}"
        return f"error: {self.message}"

    def format_with_context(self, source: str) -> str:
        """Format error with source context."""
        base = self.format()
        if not self.location or self.location.line == 0:
            return base

        lines = source.splitlines()
        if self.location.line > len(lines):
            return base

        # Get source line
        line_content = lines[self.location.line - 1]
        line_num = str(self.location.line)

        # Build output
        result = [base]
        result.append(f"  {line_num} | {line_content}")

        # Underline the error location
        padding = " " * (len(line_num) + 3 + self.location.column)
        if self.location.end_column and self.location.end_column > self.location.column:
            underline = "^" * (self.location.end_column - self.location.column)
        else:
            underline = "^"
        result.append(f"{padding}{underline}")

        return "\n".join(result)


class JSError(PrescryptError):
    """Exception raised when unable to convert Python to JS.

    This is the main error class used during code generation.
    Supports optional source location for better error messages.
    """

    def __init__(
        self,
        message: str,
        node: ast.AST | None = None,
        location: SourceLocation | None = None,
    ):
        super().__init__(message, node=node, location=location)


class UnsupportedFeatureError(PrescryptError):
    """Python feature not supported by Prescrypt."""


class ImportError(PrescryptError):
    """Module import error."""


class SemanticError(PrescryptError):
    """Error during semantic analysis."""
