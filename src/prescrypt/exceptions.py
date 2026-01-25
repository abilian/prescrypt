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
        hint: str | None = None,
    ):
        self.message = message
        self.hint = hint
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

    def format_with_context(self, source: str, context_lines: int = 1) -> str:
        """Format error with source context.

        Args:
            source: The source code
            context_lines: Number of lines to show before and after the error
        """
        base = self.format()
        if not self.location or self.location.line == 0:
            if self.hint:
                return f"{base}\n\nHint: {self.hint}"
            return base

        lines = source.splitlines()
        if self.location.line > len(lines):
            if self.hint:
                return f"{base}\n\nHint: {self.hint}"
            return base

        error_line = self.location.line

        # Determine line range to display
        start_line = max(1, error_line - context_lines)
        end_line = min(len(lines), error_line + context_lines)

        # Calculate width for line numbers
        max_line_num = end_line
        num_width = len(str(max_line_num))

        # Build output
        result = [base, ""]

        # Show context lines
        for line_num in range(start_line, end_line + 1):
            line_content = lines[line_num - 1]
            prefix = ">" if line_num == error_line else " "
            result.append(f"{prefix} {line_num:>{num_width}} | {line_content}")

            # Add underline for error line
            if line_num == error_line:
                col = self.location.column
                end_col = self.location.end_column

                # Calculate underline length
                if end_col and end_col > col:
                    underline_len = end_col - col
                else:
                    # Underline to end of meaningful content or at least 1 char
                    underline_len = max(1, len(line_content.rstrip()) - col)

                # Build the underline
                padding = " " * (num_width + 4 + col)  # prefix + space + num + " | "
                underline = "^" * underline_len
                result.append(f"{padding}{underline}")

        # Add hint if present
        if self.hint:
            result.append("")
            result.append(f"Hint: {self.hint}")

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
        hint: str | None = None,
    ):
        super().__init__(message, node=node, location=location, hint=hint)


class UnsupportedFeatureError(PrescryptError):
    """Python feature not supported by Prescrypt."""


class ImportError(PrescryptError):
    """Module import error."""


class SemanticError(PrescryptError):
    """Error during semantic analysis."""
