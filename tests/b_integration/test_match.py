"""Tests for match statement support."""
from __future__ import annotations

from prescrypt import py2js
from prescrypt.testing import js_eval


class TestMatchBasic:
    """Test basic match patterns."""

    def test_literal_match(self):
        """Test matching literal values."""
        code = """
x = 1
match x:
    case 0:
        result = 'zero'
    case 1:
        result = 'one'
    case 2:
        result = 'two'
    case _:
        result = 'other'
result
"""
        assert js_eval(py2js(code)) == "one"

    def test_wildcard(self):
        """Test wildcard pattern."""
        code = """
x = 999
match x:
    case 0:
        result = 'zero'
    case _:
        result = 'other'
result
"""
        assert js_eval(py2js(code)) == "other"

    def test_capture(self):
        """Test capture pattern."""
        code = """
x = 42
match x:
    case 0:
        result = 0
    case n:
        result = n * 2
result
"""
        assert js_eval(py2js(code)) == 84

    def test_string_match(self):
        """Test matching string values."""
        code = """
x = 'hello'
match x:
    case 'hi':
        result = 'greeting hi'
    case 'hello':
        result = 'greeting hello'
    case _:
        result = 'unknown'
result
"""
        assert js_eval(py2js(code)) == "greeting hello"


class TestMatchOr:
    """Test OR patterns."""

    def test_or_pattern(self):
        """Test OR pattern matching."""
        code = """
x = 2
match x:
    case 1 | 2 | 3:
        result = 'small'
    case _:
        result = 'big'
result
"""
        assert js_eval(py2js(code)) == "small"

    def test_or_pattern_no_match(self):
        """Test OR pattern not matching."""
        code = """
x = 10
match x:
    case 1 | 2 | 3:
        result = 'small'
    case _:
        result = 'big'
result
"""
        assert js_eval(py2js(code)) == "big"


class TestMatchSingleton:
    """Test singleton patterns (None, True, False)."""

    def test_none(self):
        """Test matching None."""
        code = """
x = None
match x:
    case None:
        result = 'none'
    case _:
        result = 'other'
result
"""
        assert js_eval(py2js(code)) == "none"

    def test_true(self):
        """Test matching True."""
        code = """
x = True
match x:
    case True:
        result = 'true'
    case False:
        result = 'false'
    case _:
        result = 'other'
result
"""
        assert js_eval(py2js(code)) == "true"

    def test_false(self):
        """Test matching False."""
        code = """
x = False
match x:
    case True:
        result = 'true'
    case False:
        result = 'false'
    case _:
        result = 'other'
result
"""
        assert js_eval(py2js(code)) == "false"


class TestMatchSequence:
    """Test sequence patterns."""

    def test_list_match(self):
        """Test matching a list."""
        code = """
x = [1, 2]
match x:
    case [a, b]:
        result = a + b
    case _:
        result = 0
result
"""
        assert js_eval(py2js(code)) == 3

    def test_list_wrong_length(self):
        """Test list with wrong length doesn't match."""
        code = """
x = [1, 2, 3]
match x:
    case [a, b]:
        result = 'two'
    case _:
        result = 'other'
result
"""
        assert js_eval(py2js(code)) == "other"

    def test_list_with_literal(self):
        """Test list pattern with literal."""
        code = """
x = [1, 2]
match x:
    case [1, y]:
        result = y
    case _:
        result = 0
result
"""
        assert js_eval(py2js(code)) == 2

    def test_nested_list(self):
        """Test nested list pattern."""
        code = """
x = [[1, 2], 3]
match x:
    case [[a, b], c]:
        result = a + b + c
    case _:
        result = 0
result
"""
        assert js_eval(py2js(code)) == 6


class TestMatchGuard:
    """Test guard clauses."""

    def test_guard_positive(self):
        """Test guard with positive condition."""
        code = """
x = 5
match x:
    case n if n > 0:
        result = 'positive'
    case n if n < 0:
        result = 'negative'
    case _:
        result = 'zero'
result
"""
        assert js_eval(py2js(code)) == "positive"

    def test_guard_negative(self):
        """Test guard with negative condition."""
        code = """
x = -3
match x:
    case n if n > 0:
        result = 'positive'
    case n if n < 0:
        result = 'negative'
    case _:
        result = 'zero'
result
"""
        assert js_eval(py2js(code)) == "negative"

    def test_guard_zero(self):
        """Test guard falling through."""
        code = """
x = 0
match x:
    case n if n > 0:
        result = 'positive'
    case n if n < 0:
        result = 'negative'
    case _:
        result = 'zero'
result
"""
        assert js_eval(py2js(code)) == "zero"

    def test_sequence_guard(self):
        """Test guard with sequence pattern."""
        code = """
x = [3, 4]
match x:
    case [a, b] if a + b > 5:
        result = 'big'
    case [a, b]:
        result = 'small'
    case _:
        result = 'other'
result
"""
        assert js_eval(py2js(code)) == "big"


class TestMatchMultipleStatements:
    """Test match with multiple statements in body."""

    def test_multiple_statements(self):
        """Test multiple statements in case body."""
        code = """
x = 2
match x:
    case 1:
        a = 10
        b = 20
        result = a + b
    case 2:
        a = 100
        b = 200
        result = a + b
    case _:
        result = 0
result
"""
        assert js_eval(py2js(code)) == 300
