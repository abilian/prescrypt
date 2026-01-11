"""Tests for string formatting expression handlers.

Tests f-strings, %-formatting, and .format() method.
"""
from __future__ import annotations

import pytest

from prescrypt import py2js
from prescrypt.testing import js_eq, js_eval


class TestFStrings:
    """Test f-string (JoinedStr) code generation."""

    def test_basic_fstring(self):
        """Test basic f-string with variable substitution."""
        code = """
name = "World"
result = f"Hello {name}!"
result
"""
        js = py2js(code)
        assert js_eval(js) == "Hello World!"

    def test_fstring_multiple_values(self):
        """Test f-string with multiple substitutions."""
        code = """
a = 1
b = 2
result = f"{a} + {b} = {a + b}"
result
"""
        js = py2js(code)
        assert js_eval(js) == "1 + 2 = 3"

    def test_fstring_expression(self):
        """Test f-string with expression."""
        code = """
x = 5
result = f"Double: {x * 2}"
result
"""
        js = py2js(code)
        assert js_eval(js) == "Double: 10"

    def test_fstring_with_repr(self):
        """Test f-string with !r conversion."""
        code = """
x = "hello"
result = f"{x!r}"
result
"""
        js = py2js(code)
        result = js_eval(js)
        # Should include quotes
        assert "hello" in result

    def test_fstring_adjacent_text(self):
        """Test f-string with adjacent literal text."""
        code = """
x = 42
result = f"Value={x}px"
result
"""
        js = py2js(code)
        assert js_eval(js) == "Value=42px"

    def test_fstring_empty_string(self):
        """Test f-string that evaluates to empty."""
        code = """
result = f""
result
"""
        js = py2js(code)
        assert js_eval(js) == ""

    def test_fstring_only_literal(self):
        """Test f-string with only literal text (no substitutions)."""
        code = """
result = f"Just text"
result
"""
        js = py2js(code)
        assert js_eval(js) == "Just text"


class TestPercentFormatting:
    """Test %-style string formatting."""

    def test_percent_string(self):
        """Test %s string substitution."""
        code = """
name = "World"
result = "Hello %s!" % name
result
"""
        js = py2js(code)
        result = js_eval(js)
        assert "World" in result

    def test_percent_multiple(self):
        """Test multiple % substitutions."""
        code = """
result = "%s + %s = %s" % (1, 2, 3)
result
"""
        js = py2js(code)
        result = js_eval(js)
        # Should contain the values
        assert "1" in result and "2" in result and "3" in result


class TestFormatMethod:
    """Test .format() string method."""

    def test_format_basic(self):
        """Test basic .format() call."""
        code = """
result = "Hello {}!".format("World")
result
"""
        js = py2js(code)
        assert js_eval(js) == "Hello World!"

    def test_format_multiple(self):
        """Test .format() with multiple arguments."""
        code = """
result = "{} + {} = {}".format(1, 2, 3)
result
"""
        js = py2js(code)
        assert js_eval(js) == "1 + 2 = 3"

    def test_format_mixed_text(self):
        """Test .format() with mixed literal and substitution."""
        code = """
result = "Value: {}px".format(42)
result
"""
        js = py2js(code)
        assert js_eval(js) == "Value: 42px"


class TestOperatorPrecedence:
    """Test operator precedence in generated code."""

    def test_multiplication_before_addition(self):
        """Test * has higher precedence than +."""
        code = "result = 1 + 2 * 3\nresult"
        assert js_eval(py2js(code)) == 7

    def test_parentheses_override_precedence(self):
        """Test parentheses override precedence."""
        code = "result = (1 + 2) * 3\nresult"
        assert js_eval(py2js(code)) == 9

    def test_power_right_associative(self):
        """Test ** is right-associative."""
        code = "result = 2 ** 3 ** 2\nresult"
        # 2 ** (3 ** 2) = 2 ** 9 = 512
        assert js_eval(py2js(code)) == 512

    def test_boolean_precedence(self):
        """Test and has higher precedence than or."""
        code = "result = True or False and False\nresult"
        assert js_eval(py2js(code)) == True

    def test_subtraction_left_associative(self):
        """Test - is left-associative."""
        code = "result = 10 - 3 - 2\nresult"
        assert js_eval(py2js(code)) == 5


class TestComparisonChains:
    """Test comparison chain desugaring."""

    def test_simple_chain(self):
        """Test simple comparison chain."""
        code = "result = 1 < 2 < 3\nresult"
        assert js_eval(py2js(code)) == True

    def test_chain_false(self):
        """Test comparison chain that's false."""
        code = "result = 1 < 3 < 2\nresult"
        assert js_eval(py2js(code)) == False

    def test_mixed_operators(self):
        """Test chain with mixed operators."""
        code = "result = 1 <= 2 <= 2\nresult"
        assert js_eval(py2js(code)) == True

    def test_long_chain(self):
        """Test long comparison chain."""
        code = "result = 0 < 1 < 2 < 3 < 4\nresult"
        assert js_eval(py2js(code)) == True

    def test_equality_chain(self):
        """Test equality chain."""
        code = "result = 1 == 1 == 1\nresult"
        assert js_eval(py2js(code)) == True
