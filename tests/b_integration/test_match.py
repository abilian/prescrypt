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


class TestMatchStar:
    """Test starred patterns in sequences."""

    def test_star_at_end(self):
        """Test [first, *rest] pattern."""
        code = """
x = [1, 2, 3, 4, 5]
match x:
    case [first, *rest]:
        result = [first, rest]
    case _:
        result = None
result
"""
        assert js_eval(py2js(code)) == [1, [2, 3, 4, 5]]

    def test_star_at_start(self):
        """Test [*rest, last] pattern."""
        code = """
x = [1, 2, 3, 4, 5]
match x:
    case [*rest, last]:
        result = [rest, last]
    case _:
        result = None
result
"""
        assert js_eval(py2js(code)) == [[1, 2, 3, 4], 5]

    def test_star_in_middle(self):
        """Test [first, *middle, last] pattern."""
        code = """
x = [1, 2, 3, 4, 5]
match x:
    case [first, *middle, last]:
        result = [first, middle, last]
    case _:
        result = None
result
"""
        assert js_eval(py2js(code)) == [1, [2, 3, 4], 5]

    def test_star_empty_rest(self):
        """Test star matching empty list."""
        code = """
x = [1, 2]
match x:
    case [first, *middle, last]:
        result = [first, middle, last]
    case _:
        result = None
result
"""
        assert js_eval(py2js(code)) == [1, [], 2]

    def test_star_wildcard(self):
        """Test [first, *_, last] pattern (ignore middle)."""
        code = """
x = [1, 2, 3, 4, 5]
match x:
    case [first, *_, last]:
        result = [first, last]
    case _:
        result = None
result
"""
        assert js_eval(py2js(code)) == [1, 5]

    def test_star_single_element(self):
        """Test star with single element list."""
        code = """
x = [42]
match x:
    case [only]:
        result = f"one: {only}"
    case [first, *rest]:
        result = f"many: {first}"
    case _:
        result = "empty"
result
"""
        assert js_eval(py2js(code)) == "one: 42"

    def test_star_minimum_length(self):
        """Test that star respects minimum length."""
        code = """
x = [1]
match x:
    case [a, b, *rest]:
        result = "at least 2"
    case [a]:
        result = "exactly 1"
    case _:
        result = "other"
result
"""
        assert js_eval(py2js(code)) == "exactly 1"

    def test_star_with_literals(self):
        """Test star with literal elements."""
        code = """
x = [0, 1, 2, 3]
match x:
    case [0, *rest]:
        result = rest
    case _:
        result = []
result
"""
        assert js_eval(py2js(code)) == [1, 2, 3]


class TestMatchMapping:
    """Test dictionary/mapping patterns."""

    def test_simple_mapping(self):
        """Test simple mapping pattern with capture."""
        code = """
data = {"x": 10, "y": 20}
match data:
    case {"x": x, "y": y}:
        result = x + y
    case _:
        result = 0
result
"""
        assert js_eval(py2js(code)) == 30

    def test_mapping_with_literal(self):
        """Test mapping pattern with literal value check."""
        code = """
cmd = {"type": "move", "x": 5}
match cmd:
    case {"type": "stop"}:
        result = "stopping"
    case {"type": "move", "x": x}:
        result = f"moving {x}"
    case _:
        result = "unknown"
result
"""
        assert js_eval(py2js(code)) == "moving 5"

    def test_mapping_no_match(self):
        """Test mapping pattern that doesn't match."""
        code = """
data = {"a": 1}
match data:
    case {"x": x}:
        result = x
    case _:
        result = "no x"
result
"""
        assert js_eval(py2js(code)) == "no x"

    def test_mapping_nested(self):
        """Test nested mapping pattern."""
        code = """
data = {"point": {"x": 3, "y": 4}}
match data:
    case {"point": {"x": x, "y": y}}:
        result = x * x + y * y
    case _:
        result = 0
result
"""
        assert js_eval(py2js(code)) == 25


class TestMatchClass:
    """Test class patterns."""

    def test_class_keyword_pattern(self):
        """Test class pattern with keyword attributes."""
        code = """
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(3, 4)
match p:
    case Point(x=x, y=y):
        result = x + y
    case _:
        result = 0
result
"""
        assert js_eval(py2js(code)) == 7

    def test_class_literal_check(self):
        """Test class pattern with literal value check."""
        code = """
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(0, 5)
match p:
    case Point(x=0, y=y):
        result = f"on y-axis at {y}"
    case Point(x=x, y=0):
        result = f"on x-axis at {x}"
    case _:
        result = "elsewhere"
result
"""
        assert js_eval(py2js(code)) == "on y-axis at 5"

    def test_class_no_match(self):
        """Test class pattern that doesn't match type."""
        code = """
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Circle:
    def __init__(self, r):
        self.r = r

c = Circle(10)
match c:
    case Point(x=x, y=y):
        result = "point"
    case Circle(r=r):
        result = f"circle r={r}"
    case _:
        result = "unknown"
result
"""
        assert js_eval(py2js(code)) == "circle r=10"

    def test_class_with_guard(self):
        """Test class pattern with guard."""
        code = """
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(3, 4)
match p:
    case Point(x=x, y=y) if x == y:
        result = "diagonal"
    case Point(x=x, y=y) if x > y:
        result = "right of diagonal"
    case Point(x=x, y=y):
        result = "left of diagonal"
result
"""
        assert js_eval(py2js(code)) == "left of diagonal"
