"""Tests for Set literals."""

from __future__ import annotations

from prescrypt import py2js


def js(code: str) -> str:
    """Compile Python to JavaScript without stdlib."""
    return py2js(code, include_stdlib=False)


class TestSetLiteral:
    """Set literal compilation tests."""

    def test_empty_set(self):
        """Empty set literal - not possible in Python syntax, uses set()"""
        # {  } is an empty dict, not set
        # Python uses set() for empty sets

    def test_single_element(self):
        """Single element set {1}"""
        code = "{1}"
        result = js(code)
        assert "new Set([1])" in result

    def test_multiple_elements(self):
        """Multiple element set {1, 2, 3}"""
        code = "{1, 2, 3}"
        result = js(code)
        assert "new Set(" in result
        assert "1" in result
        assert "2" in result
        assert "3" in result

    def test_string_elements(self):
        """Set with string elements"""
        code = "{'a', 'b', 'c'}"
        result = js(code)
        assert "new Set(" in result
        assert "'a'" in result or '"a"' in result

    def test_mixed_elements(self):
        """Set with mixed types"""
        code = "{1, 'two', 3.0}"
        result = js(code)
        assert "new Set(" in result

    def test_set_with_variables(self):
        """Set with variable elements"""
        code = "{a, b, c}"
        result = js(code)
        assert "new Set([a, b, c])" in result

    def test_set_assignment(self):
        """Set assigned to variable"""
        code = "s = {1, 2, 3}"
        result = js(code)
        assert "new Set(" in result
