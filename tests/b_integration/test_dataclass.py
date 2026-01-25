"""Tests for dataclass support.

Tests that @dataclass decorator generates appropriate __init__, __repr__, and __eq__.
"""

from __future__ import annotations

from prescrypt import py2js
from prescrypt.testing import js_eval


class TestDataclassBasic:
    """Basic dataclass tests."""

    def test_dataclass_simple(self):
        """Simple dataclass with fields."""
        code = """
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

p = Point(1, 2)
[p.x, p.y]
"""
        result = js_eval(py2js(code))
        assert result == [1, 2]

    def test_dataclass_with_defaults(self):
        """Dataclass with default values."""
        code = """
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int = 0

p = Point(5)
[p.x, p.y]
"""
        result = js_eval(py2js(code))
        assert result == [5, 0]

    def test_dataclass_all_defaults(self):
        """Dataclass with all default values."""
        code = """
from dataclasses import dataclass

@dataclass
class Config:
    debug: bool = False
    timeout: int = 30
    name: str = "default"

c = Config()
[c.debug, c.timeout, c.name]
"""
        result = js_eval(py2js(code))
        assert result == [False, 30, "default"]

    def test_dataclass_override_defaults(self):
        """Dataclass with overridden defaults."""
        code = """
from dataclasses import dataclass

@dataclass
class Config:
    debug: bool = False
    timeout: int = 30

c = Config(True, 60)
[c.debug, c.timeout]
"""
        result = js_eval(py2js(code))
        assert result == [True, 60]


class TestDataclassRepr:
    """Tests for __repr__ generation."""

    def test_dataclass_repr(self):
        """Dataclass should have __repr__."""
        code = """
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

p = Point(3, 4)
repr(p)
"""
        result = js_eval(py2js(code))
        assert result == "Point(x=3, y=4)"

    def test_dataclass_repr_string_field(self):
        """Dataclass repr with string field."""
        code = """
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int

p = Person("Alice", 30)
repr(p)
"""
        result = js_eval(py2js(code))
        assert result == "Person(name='Alice', age=30)"


class TestDataclassEquality:
    """Tests for __eq__ generation."""

    def test_dataclass_equal(self):
        """Dataclass equality with same values."""
        code = """
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

p1 = Point(1, 2)
p2 = Point(1, 2)
p1 == p2
"""
        result = js_eval(py2js(code))
        assert result is True

    def test_dataclass_not_equal(self):
        """Dataclass inequality with different values."""
        code = """
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

p1 = Point(1, 2)
p2 = Point(3, 4)
p1 == p2
"""
        result = js_eval(py2js(code))
        assert result is False


class TestDataclassOptions:
    """Tests for dataclass options."""

    def test_dataclass_eq_false(self):
        """Dataclass with eq=False should not have __eq__."""
        code = """
from dataclasses import dataclass

@dataclass(eq=False)
class Point:
    x: int
    y: int

p1 = Point(1, 2)
p2 = Point(1, 2)
p1 == p2
"""
        # Without __eq__, objects are compared by identity
        result = js_eval(py2js(code))
        assert result is False  # Different instances


class TestDataclassWithMethods:
    """Tests for dataclasses with additional methods."""

    def test_dataclass_with_method(self):
        """Dataclass can have additional methods."""
        code = """
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

    def distance_from_origin(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

p = Point(3, 4)
p.distance_from_origin()
"""
        result = js_eval(py2js(code))
        assert result == 5.0

    def test_dataclass_with_classmethod(self):
        """Dataclass can have class methods."""
        code = """
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

    @classmethod
    def origin(cls):
        return cls(0, 0)

p = Point.origin()
[p.x, p.y]
"""
        result = js_eval(py2js(code))
        assert result == [0, 0]
