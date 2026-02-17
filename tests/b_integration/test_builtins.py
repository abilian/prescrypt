"""Tests for Python builtin functions."""

from __future__ import annotations

from prescrypt import py2js
from prescrypt.testing import js_eval


class TestNumericBuiltins:
    """Test numeric builtin functions."""

    def test_abs(self):
        assert js_eval(py2js("abs(-5)")) == 5
        assert js_eval(py2js("abs(5)")) == 5
        assert js_eval(py2js("abs(-3.14)")) == 3.14

    def test_round(self):
        assert js_eval(py2js("round(3.7)")) == 4
        assert js_eval(py2js("round(3.2)")) == 3
        assert js_eval(py2js("round(3.14159, 2)")) == 3.14

    def test_pow(self):
        assert js_eval(py2js("pow(2, 3)")) == 8
        assert js_eval(py2js("pow(2, 10)")) == 1024

    def test_divmod(self):
        result = js_eval(py2js("divmod(17, 5)"))
        assert result == [3, 2]

    def test_sum(self):
        assert js_eval(py2js("sum([1, 2, 3, 4, 5])")) == 15
        assert js_eval(py2js("sum([])")) == 0

    def test_min_max(self):
        assert js_eval(py2js("min(3, 1, 4, 1, 5)")) == 1
        assert js_eval(py2js("max(3, 1, 4, 1, 5)")) == 5
        assert js_eval(py2js("min([3, 1, 4, 1, 5])")) == 1
        assert js_eval(py2js("max([3, 1, 4, 1, 5])")) == 5

    def test_min_max_tuples(self):
        """Test min/max with tuple comparison (lexicographic)."""
        # Tuple comparison
        code = """
arr = [3, 1, 4, 1, 5]
result = min((x, i) for i, x in enumerate(arr))
result
"""
        result = js_eval(py2js(code))
        assert result == [1, 1]  # (1, 1) - smallest value is 1 at index 1

        code = """
arr = [3, 1, 4, 1, 5]
result = max((x, i) for i, x in enumerate(arr))
result
"""
        result = js_eval(py2js(code))
        assert result == [5, 4]  # (5, 4) - largest value is 5 at index 4

        # Multiple tuple arguments
        code = "min((1, 2), (1, 1), (2, 0))"
        result = js_eval(py2js(code))
        assert result == [1, 1]  # (1, 1) is smallest lexicographically

    def test_min_max_with_key(self):
        """Test min/max with key function."""
        code = "min([3, 1, 4], key=lambda x: -x)"
        result = js_eval(py2js(code))
        assert result == 4  # -4 is smallest, so 4 is returned

        code = "max([3, 1, 4], key=lambda x: -x)"
        result = js_eval(py2js(code))
        assert result == 1  # -1 is largest, so 1 is returned

        code = "min(['abc', 'a', 'ab'], key=len)"
        result = js_eval(py2js(code))
        assert result == "a"

    def test_min_max_with_default(self):
        """Test min/max with default value for empty iterables."""
        code = "min([], default=42)"
        result = js_eval(py2js(code))
        assert result == 42

        code = "max([], default=-1)"
        result = js_eval(py2js(code))
        assert result == -1


class TestStringConversions:
    """Test string conversion builtins."""

    def test_chr(self):
        assert js_eval(py2js("chr(65)")) == "A"
        assert js_eval(py2js("chr(97)")) == "a"
        assert js_eval(py2js("chr(48)")) == "0"

    def test_ord(self):
        assert js_eval(py2js("ord('A')")) == 65
        assert js_eval(py2js("ord('a')")) == 97
        assert js_eval(py2js("ord('0')")) == 48

    def test_chr_ord_roundtrip(self):
        code = """
x = 72
chr(x) + chr(x+1)
"""
        assert js_eval(py2js(code)) == "HI"

    def test_str(self):
        assert js_eval(py2js("str(42)")) == "42"
        assert js_eval(py2js("str(3.14)")) == "3.14"
        assert js_eval(py2js("str(True)")) == "True"  # Python style: capital T
        assert js_eval(py2js("str(False)")) == "False"  # Python style: capital F
        assert js_eval(py2js("str()")) == ""

    def test_repr(self):
        # repr uses single quotes for strings, like Python
        assert js_eval(py2js("repr('hello')")) == "'hello'"
        assert js_eval(py2js("repr(42)")) == "42"


class TestTypeConversions:
    """Test type conversion builtins."""

    def test_int(self):
        assert js_eval(py2js("int('42')")) == 42
        assert js_eval(py2js("int(3.7)")) == 3
        assert js_eval(py2js("int()")) == 0

    def test_float(self):
        assert js_eval(py2js("float('3.14')")) == 3.14
        assert js_eval(py2js("float(42)")) == 42.0
        assert js_eval(py2js("float()")) == 0.0

    def test_bool(self):
        assert js_eval(py2js("bool(1)")) == True
        assert js_eval(py2js("bool(0)")) == False
        assert js_eval(py2js("bool([])")) == False
        assert js_eval(py2js("bool([1])")) == True
        assert js_eval(py2js("bool('')")) == False
        assert js_eval(py2js("bool('x')")) == True
        assert js_eval(py2js("bool()")) == False

    def test_list(self):
        assert js_eval(py2js("list()")) == []
        assert js_eval(py2js("list('abc')")) == ["a", "b", "c"]
        assert js_eval(py2js("list(range(3))")) == [0, 1, 2]

    def test_dict(self):
        assert js_eval(py2js("dict()")) == {}
        assert js_eval(py2js("dict(a=1, b=2)")) == {"a": 1, "b": 2}


class TestSequenceBuiltins:
    """Test sequence-related builtins."""

    def test_len(self):
        assert js_eval(py2js("len([1, 2, 3])")) == 3
        assert js_eval(py2js("len('hello')")) == 5
        assert js_eval(py2js("len({})")) == 0
        assert js_eval(py2js("len({'a': 1, 'b': 2})")) == 2

    def test_range(self):
        assert js_eval(py2js("list(range(5))")) == [0, 1, 2, 3, 4]
        assert js_eval(py2js("list(range(2, 5))")) == [2, 3, 4]
        assert js_eval(py2js("list(range(0, 10, 2))")) == [0, 2, 4, 6, 8]

    def test_reversed(self):
        assert js_eval(py2js("list(reversed([1, 2, 3]))")) == [3, 2, 1]
        # Note: reversed on strings requires converting to list first in JS
        assert js_eval(py2js("list(reversed(list('abc')))")) == ["c", "b", "a"]

    def test_sorted(self):
        assert js_eval(py2js("sorted([3, 1, 4, 1, 5])")) == [1, 1, 3, 4, 5]
        assert js_eval(py2js("sorted([3, 1, 4], reverse=True)")) == [4, 3, 1]

    def test_enumerate(self):
        code = """
result = []
for i, x in enumerate(['a', 'b', 'c']):
    result.append([i, x])
result
"""
        assert js_eval(py2js(code)) == [[0, "a"], [1, "b"], [2, "c"]]

    def test_zip(self):
        code = """
result = []
for a, b in zip([1, 2, 3], ['a', 'b', 'c']):
    result.append([a, b])
result
"""
        assert js_eval(py2js(code)) == [[1, "a"], [2, "b"], [3, "c"]]

    def test_map(self):
        code = """
def double(x):
    return x * 2

list(map(double, [1, 2, 3]))
"""
        assert js_eval(py2js(code)) == [2, 4, 6]

    def test_filter(self):
        code = """
def is_even(x):
    return x % 2 == 0

list(filter(is_even, [1, 2, 3, 4, 5, 6]))
"""
        assert js_eval(py2js(code)) == [2, 4, 6]


class TestBooleanBuiltins:
    """Test boolean builtins."""

    def test_all(self):
        assert js_eval(py2js("all([True, True, True])")) == True
        assert js_eval(py2js("all([True, False, True])")) == False
        assert js_eval(py2js("all([])")) == True
        assert js_eval(py2js("all([1, 2, 3])")) == True
        assert js_eval(py2js("all([1, 0, 3])")) == False

    def test_any(self):
        assert js_eval(py2js("any([False, False, True])")) == True
        assert js_eval(py2js("any([False, False, False])")) == False
        assert js_eval(py2js("any([])")) == False
        assert js_eval(py2js("any([0, 0, 1])")) == True


class TestObjectBuiltins:
    """Test object-related builtins."""

    def test_callable(self):
        code = """
def foo():
    pass

x = 42
[callable(foo), callable(x)]
"""
        # Note: callable(len) doesn't work because len is a compile-time builtin
        assert js_eval(py2js(code)) == [True, False]

    def test_hasattr(self):
        code = """
class Foo:
    def __init__(self):
        self.x = 10

f = Foo()
[hasattr(f, 'x'), hasattr(f, 'y')]
"""
        assert js_eval(py2js(code)) == [True, False]

    def test_getattr(self):
        code = """
class Foo:
    def __init__(self):
        self.x = 42

f = Foo()
getattr(f, 'x')
"""
        assert js_eval(py2js(code)) == 42

    def test_getattr_default(self):
        code = """
class Foo:
    pass

f = Foo()
getattr(f, 'x', 100)
"""
        assert js_eval(py2js(code)) == 100

    def test_setattr(self):
        code = """
class Foo:
    pass

f = Foo()
setattr(f, 'x', 42)
f.x
"""
        assert js_eval(py2js(code)) == 42

    def test_delattr(self):
        code = """
class Foo:
    def __init__(self):
        self.x = 42
        self.y = 100

f = Foo()
delattr(f, 'x')
hasattr(f, 'x')
"""
        assert js_eval(py2js(code)) == False


class TestTypeChecking:
    """Test type checking builtins."""

    def test_isinstance_basic(self):
        code = """
x = 42
isinstance(x, int)
"""
        # Note: In JS, int maps to 'number'
        result = js_eval(py2js(code))
        assert result == True

    def test_isinstance_string(self):
        code = """
x = "hello"
isinstance(x, str)
"""
        assert js_eval(py2js(code)) == True

    def test_isinstance_list(self):
        code = """
x = [1, 2, 3]
isinstance(x, list)
"""
        assert js_eval(py2js(code)) == True

    def test_isinstance_custom_class(self):
        code = """
class Foo:
    pass

f = Foo()
isinstance(f, Foo)
"""
        assert js_eval(py2js(code)) == True

    def test_isinstance_inheritance(self):
        code = """
class Animal:
    pass

class Dog(Animal):
    pass

d = Dog()
[isinstance(d, Dog), isinstance(d, Animal)]
"""
        assert js_eval(py2js(code)) == [True, True]


class TestPrintFunction:
    """Test print function (limited testing since it outputs to console)."""

    def test_print_basic(self):
        # Just verify it compiles without error
        code = "print('hello')"
        js = py2js(code)
        assert "console.log" in js

    def test_print_multiple_args(self):
        code = "print('a', 'b', 'c')"
        js = py2js(code)
        assert "console.log" in js

    def test_print_sep(self):
        code = "print('a', 'b', sep='-')"
        js = py2js(code)
        assert "console.log" in js
        assert "'-'" in js


class TestMiscBuiltins:
    """Test miscellaneous builtins."""

    def test_format(self):
        assert js_eval(py2js("format(42)")) == "42"
        assert js_eval(py2js("format(3.14159, '.2f')")) == "3.14"
