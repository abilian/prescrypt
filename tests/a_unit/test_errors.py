"""Tests for error messages with source locations."""

from __future__ import annotations

import pytest

from prescrypt.exceptions import JSError, PrescryptError, SourceLocation
from prescrypt.front import ast
from prescrypt.front.passes.errors import (
    IncompatibleTypeError,
    StatementOutOfLoopError,
    UnknownSymbolError,
    UnknownTypeError,
)


class TestSourceLocation:
    def test_basic_location(self):
        loc = SourceLocation(line=10, column=5)
        assert str(loc) == "10:5"

    def test_location_with_file(self):
        loc = SourceLocation(file="foo.py", line=10, column=5)
        assert str(loc) == "foo.py:10:5"

    def test_from_node(self):
        # Create a mock node with location info
        node = ast.Name(id="x", ctx=ast.Load())
        node.lineno = 42
        node.col_offset = 8
        node.end_lineno = 42
        node.end_col_offset = 9

        loc = SourceLocation.from_node(node)
        assert loc.line == 42
        assert loc.column == 8
        assert loc.end_line == 42
        assert loc.end_column == 9


class TestPrescryptError:
    def test_error_without_location(self):
        err = PrescryptError("Something went wrong")
        assert err.message == "Something went wrong"
        assert err.location is None
        assert "error: Something went wrong" in str(err)

    def test_error_with_location(self):
        loc = SourceLocation(file="test.py", line=5, column=10)
        err = PrescryptError("Invalid syntax", location=loc)
        assert "test.py:5:10: error: Invalid syntax" in str(err)

    def test_error_with_node(self):
        node = ast.Name(id="x", ctx=ast.Load())
        node.lineno = 15
        node.col_offset = 4

        err = PrescryptError("Undefined variable", node=node)
        assert err.location is not None
        assert err.location.line == 15
        assert err.location.column == 4

    def test_format_with_context(self):
        loc = SourceLocation(line=2, column=4, end_column=7)
        err = PrescryptError("Invalid token", location=loc)

        source = "x = 1\nfoo bar\ny = 2"
        formatted = err.format_with_context(source)

        assert "2:4: error: Invalid token" in formatted
        assert "foo bar" in formatted
        assert "^^^" in formatted  # underline

    def test_format_with_context_single_char(self):
        loc = SourceLocation(line=1, column=0)
        err = PrescryptError("Unexpected character", location=loc)

        source = "x = 1"
        formatted = err.format_with_context(source)

        assert "^" in formatted  # single char underline


class TestJSError:
    def test_basic_error(self):
        err = JSError("Feature not supported")
        assert "Feature not supported" in str(err)

    def test_error_with_node(self):
        node = ast.Set(elts=[])
        node.lineno = 10
        node.col_offset = 0

        err = JSError("Sets not supported", node)
        assert err.location.line == 10


class TestBindErrors:
    def test_unknown_symbol(self):
        err = UnknownSymbolError("foo")
        assert err.symbol == "foo"
        assert "Unknown symbol: foo" in str(err)

    def test_unknown_symbol_with_node(self):
        node = ast.Name(id="undefined_var", ctx=ast.Load())
        node.lineno = 5
        node.col_offset = 0

        err = UnknownSymbolError("undefined_var", node=node)
        assert err.location.line == 5

    def test_statement_out_of_loop(self):
        err = StatementOutOfLoopError("break")
        assert "'break' not allowed outside of a loop" in str(err)

    def test_statement_out_of_loop_with_node(self):
        node = ast.Break()
        node.lineno = 20
        node.col_offset = 8

        err = StatementOutOfLoopError("break", node=node)
        assert err.location.line == 20


class TestTypeErrors:
    def test_unknown_type(self):
        err = UnknownTypeError("FooBar")
        assert err.type_name == "FooBar"
        assert "Unknown type: FooBar" in str(err)

    def test_incompatible_types(self):
        err = IncompatibleTypeError("int", "str")
        assert err.type1 == "int"
        assert err.type2 == "str"
        assert "Incompatible types: int and str" in str(err)


class TestErrorInCompilation:
    """Test that errors raised during compilation have source locations."""

    def test_reserved_name_error(self):
        from prescrypt.compiler import py2js

        # 'interface' is valid Python but reserved in JS
        # Using it in a load context (reading the variable)
        with pytest.raises(JSError) as exc_info:
            py2js("x = interface + 1")

        err = exc_info.value
        # The error should have a location
        assert err.location is not None
        assert err.location.line >= 1
        assert "interface" in err.message

    def test_set_literal_error(self):
        from prescrypt.compiler import py2js

        with pytest.raises(JSError) as exc_info:
            py2js("x = {1, 2, 3}")  # Sets not supported

        err = exc_info.value
        assert err.location is not None
        assert "Set" in err.message

    def test_multiple_inheritance_error(self):
        from prescrypt.compiler import py2js

        code = """
class Foo(A, B):
    pass
"""
        with pytest.raises(JSError) as exc_info:
            py2js(code)

        err = exc_info.value
        assert err.location is not None
        assert "inheritance" in err.message.lower()
