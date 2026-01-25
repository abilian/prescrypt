"""Tests for __slots__ support."""
from __future__ import annotations

from prescrypt import py2js
from prescrypt.testing import js_eval


class TestSlots:
    """Test __slots__ functionality."""

    def test_basic_slots(self):
        """Test basic class with __slots__."""
        code = """
class Point:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
[p.x, p.y]
"""
        assert js_eval(py2js(code)) == [1, 2]

    def test_slots_tuple(self):
        """Test __slots__ defined as tuple."""
        code = """
class Point:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(3, 4)
[p.x, p.y]
"""
        assert js_eval(py2js(code)) == [3, 4]

    def test_slots_single_string(self):
        """Test __slots__ defined as single string."""
        code = """
class Counter:
    __slots__ = 'value'
    def __init__(self, value):
        self.value = value

c = Counter(42)
c.value
"""
        assert js_eval(py2js(code)) == 42

    def test_slots_modify_existing(self):
        """Test that modifying existing slots works."""
        code = """
class Point:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
p.x = 10
p.y = 20
[p.x, p.y]
"""
        assert js_eval(py2js(code)) == [10, 20]

    def test_slots_with_methods(self):
        """Test __slots__ class with methods."""
        code = """
class Rectangle:
    __slots__ = ['width', 'height']

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

r = Rectangle(5, 3)
r.area()
"""
        assert js_eval(py2js(code)) == 15

    def test_slots_in_prototype(self):
        """Test that __slots__ is accessible on instances."""
        code = """
class Point:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
list(p.__slots__)
"""
        assert js_eval(py2js(code)) == ["x", "y"]
