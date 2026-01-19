"""Tests for print() and str() optimization with type inference.

These tests verify that print() and str() skip the _pyfunc_str wrapper
when the argument type is known to be a primitive (int, float, str, bool).
"""

from __future__ import annotations

import pytest

from prescrypt import py2js


def js(code: str) -> str:
    """Compile Python to JavaScript without stdlib."""
    return py2js(code, include_stdlib=False)


class TestPrintOptimization:
    """Tests for print() optimization."""

    def test_print_string_literal(self):
        """print() with string literal should use direct console.log."""
        code = 'print("hello")'
        result = js(code)
        assert 'console.log("hello")' in result or "console.log('hello')" in result
        assert "_pyfunc_str" not in result

    def test_print_int_literal(self):
        """print() with int literal should use direct console.log."""
        code = "print(42)"
        result = js(code)
        assert "console.log(42)" in result
        assert "_pyfunc_str" not in result

    def test_print_typed_string_variable(self):
        """print() with typed string variable should skip wrapper."""
        code = """
def get_name() -> str:
    return "Alice"

print(get_name())
"""
        result = js(code)
        assert "console.log(get_name())" in result
        assert "_pyfunc_str" not in result

    def test_print_typed_int_variable(self):
        """print() with typed int variable should skip wrapper."""
        code = """
def get_age() -> int:
    return 30

print(get_age())
"""
        result = js(code)
        assert "console.log(get_age())" in result
        assert "_pyfunc_str" not in result

    def test_print_typed_float_variable(self):
        """print() with typed float variable should skip wrapper."""
        code = """
def get_price() -> float:
    return 19.99

print(get_price())
"""
        result = js(code)
        assert "console.log(get_price())" in result
        assert "_pyfunc_str" not in result

    def test_print_typed_bool_variable(self):
        """print() with typed bool variable needs _pyfunc_str for Python-style True/False."""
        code = """
def is_ready() -> bool:
    return True

print(is_ready())
"""
        result = js(code)
        # Booleans need _pyfunc_str() wrapper to output "True"/"False" instead of "true"/"false"
        assert "_pyfunc_str(is_ready())" in result

    def test_print_multiple_typed_args(self):
        """print() with multiple typed args should use concatenation."""
        code = """
def get_name() -> str:
    return "Alice"

def get_age() -> int:
    return 30

print(get_name(), get_age())
"""
        result = js(code)
        # Should use direct concatenation
        assert "get_name()" in result
        assert "get_age()" in result
        assert "_pyfunc_str" not in result

    def test_print_untyped_function_uses_wrapper(self):
        """print() with untyped function should use _pyfunc_str."""
        code = """
def get_data():
    return [1, 2, 3]

print(get_data())
"""
        result = js(code)
        assert "_pyfunc_str(get_data())" in result

    def test_print_list_literal_uses_wrapper(self):
        """print() with list literal should use _pyfunc_str."""
        code = "print([1, 2, 3])"
        result = js(code)
        assert "_pyfunc_str" in result

    def test_print_fstring_with_typed_interpolation(self):
        """print() with f-string containing typed values should optimize both."""
        code = """
def greet(name: str) -> str:
    return f"Hello, {name}!"

print(greet("World"))
"""
        result = js(code)
        # Both f-string and print should be optimized
        assert "console.log(greet('World'))" in result
        assert "_pyfunc_str" not in result
        assert "Hello, " in result  # f-string uses direct concatenation


class TestStrOptimization:
    """Tests for str() optimization."""

    def test_str_of_string_returns_as_is(self):
        """str() of a string should return the value unchanged."""
        code = """
def get_name() -> str:
    return "Alice"

x = str(get_name())
"""
        result = js(code)
        assert "x = get_name()" in result
        assert "_pyfunc_str" not in result

    def test_str_of_int_uses_String(self):
        """str() of an int should use native String()."""
        code = """
def get_count() -> int:
    return 42

x = str(get_count())
"""
        result = js(code)
        assert "String(get_count())" in result
        assert "_pyfunc_str" not in result

    def test_str_of_float_uses_String(self):
        """str() of a float should use native String()."""
        code = """
def get_price() -> float:
    return 19.99

x = str(get_price())
"""
        result = js(code)
        assert "String(get_price())" in result
        assert "_pyfunc_str" not in result

    def test_str_of_bool_uses_pyfunc_str(self):
        """str() of a bool should use _pyfunc_str for Python-style output (True/False)."""
        code = """
def is_ready() -> bool:
    return True

x = str(is_ready())
"""
        result = js(code)
        # Booleans need _pyfunc_str to convert true/false -> True/False
        assert "_pyfunc_str" in result

    def test_str_of_int_literal(self):
        """str() of an int literal should be optimized (constant folded or String())."""
        code = "x = str(42)"
        result = js(code)
        # Constant folding may convert str(42) to '42' directly
        # Otherwise it should use String(42)
        assert "String(42)" in result or "'42'" in result or '"42"' in result
        assert "_pyfunc_str" not in result

    def test_str_of_unknown_type_uses_wrapper(self):
        """str() of unknown type should use _pyfunc_str."""
        code = """
def get_data():
    return [1, 2, 3]

x = str(get_data())
"""
        result = js(code)
        assert "_pyfunc_str" in result

    def test_str_no_args_returns_empty_string(self):
        """str() with no args should return empty string."""
        code = "x = str()"
        result = js(code)
        assert 'x = ""' in result


class TestBuiltinReturnTypes:
    """Tests for builtin function return type inference."""

    def test_len_returns_int(self):
        """len() returns int, so str(len(...)) should use String()."""
        code = """
items = [1, 2, 3]
x = str(len(items))
"""
        result = js(code)
        # len() returns Int, so str() should use String()
        assert "_pyfunc_str" not in result

    def test_string_method_returns_string(self):
        """String method returns string, so print() should skip wrapper."""
        code = """
name = "alice"
print(name.upper())
"""
        result = js(code)
        # .upper() returns String, so print should skip _pyfunc_str
        assert "_pyfunc_str" not in result


class TestNestedCalls:
    """Tests for nested function calls with type inference."""

    def test_nested_typed_calls(self):
        """Nested typed function calls should all be optimized."""
        code = """
def inner() -> str:
    return "hello"

def outer(s: str) -> str:
    return s.upper()

print(outer(inner()))
"""
        result = js(code)
        assert "console.log" in result
        assert "outer(inner())" in result
        assert "_pyfunc_str" not in result

    def test_chained_string_methods(self):
        """Chained string methods should preserve type information."""
        code = """
name = "alice"
print(name.upper().strip())
"""
        result = js(code)
        # Both .upper() and .strip() return String
        assert "_pyfunc_str" not in result
