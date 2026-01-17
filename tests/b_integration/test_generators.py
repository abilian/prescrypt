"""Tests for generator functions."""

from __future__ import annotations

from prescrypt import py2js


def js(code: str) -> str:
    """Compile Python to JavaScript without stdlib."""
    return py2js(code, include_stdlib=False)


class TestGeneratorDetection:
    """Test generator function detection."""

    def test_simple_yield(self):
        """Function with yield is detected as generator."""
        code = "def gen():\n    yield 1"
        result = js(code)
        assert "function*" in result
        assert "yield 1" in result

    def test_yield_in_loop(self):
        """Function with yield in loop is detected as generator."""
        code = "def gen():\n    for i in range(10):\n        yield i"
        result = js(code)
        assert "function*" in result

    def test_yield_from(self):
        """Function with yield from is detected as generator."""
        code = "def gen():\n    yield from other()"
        result = js(code)
        assert "function*" in result
        assert "yield*" in result

    def test_no_yield_not_generator(self):
        """Regular function without yield is not a generator."""
        code = "def func():\n    return 1"
        result = js(code)
        assert "function*" not in result
        assert "function func" in result

    def test_nested_yield_not_detected(self):
        """Yield in nested function doesn't make outer function a generator."""
        code = """
def outer():
    def inner():
        yield 1
    return inner
"""
        result = js(code)
        # outer should be regular function
        assert result.count("function*") == 1  # only inner


class TestYieldExpression:
    """Test yield expression generation."""

    def test_yield_value(self):
        """Yield with value generates correctly."""
        code = "def gen():\n    yield 42"
        result = js(code)
        assert "yield 42" in result

    def test_yield_expression(self):
        """Yield with expression generates correctly."""
        code = "def gen():\n    yield x + 1"
        result = js(code)
        assert "yield" in result

    def test_yield_none(self):
        """Bare yield (no value) generates correctly."""
        code = "def gen():\n    yield"
        result = js(code)
        assert "yield;" in result or "yield\n" in result or "yield}" in result

    def test_yield_in_assignment(self):
        """Yield as expression in assignment."""
        code = "def gen():\n    x = yield 1"
        result = js(code)
        assert "yield 1" in result


class TestYieldFrom:
    """Test yield from expression generation."""

    def test_yield_from_call(self):
        """Yield from function call."""
        code = "def gen():\n    yield from other()"
        result = js(code)
        assert "yield* other()" in result

    def test_yield_from_name(self):
        """Yield from variable."""
        code = "def gen():\n    yield from items"
        result = js(code)
        assert "yield* items" in result

    def test_yield_from_expression(self):
        """Yield from complex expression."""
        code = "def gen():\n    yield from range(10)"
        result = js(code)
        assert "yield*" in result


class TestGeneratorPatterns:
    """Test common generator patterns."""

    def test_simple_counter(self):
        """Simple counter generator."""
        code = """
def count(n):
    i = 0
    while i < n:
        yield i
        i += 1
"""
        result = js(code)
        assert "function* count" in result
        assert "yield i" in result

    def test_filter_generator(self):
        """Generator that filters values."""
        code = """
def evens(items):
    for x in items:
        if x % 2 == 0:
            yield x
"""
        result = js(code)
        assert "function* evens" in result

    def test_transform_generator(self):
        """Generator that transforms values."""
        code = """
def squares(items):
    for x in items:
        yield x * x
"""
        result = js(code)
        assert "function* squares" in result

    def test_chain_generators(self):
        """Generator that chains others with yield from."""
        code = """
def chain(a, b):
    yield from a
    yield from b
"""
        result = js(code)
        assert "function* chain" in result
        assert result.count("yield*") == 2


class TestGeneratorContext:
    """Test generators in different contexts."""

    def test_generator_in_class(self):
        """Generator method in class."""
        code = """
class MyClass:
    def gen_items(self):
        yield 1
        yield 2
"""
        result = js(code)
        assert "function*" in result

    def test_nested_generator(self):
        """Nested generator function."""
        code = """
def outer():
    def inner():
        yield 1
        yield 2
    return inner
"""
        result = js(code)
        assert "function* inner" in result
