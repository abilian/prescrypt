"""Tests for f-string optimization (Phase 4).

When all interpolated values have primitive types and no format specs/conversions,
use direct concatenation instead of _pymeth_format.
"""

from __future__ import annotations

from prescrypt import py2js
from prescrypt.testing import js_eval


class TestSimpleFStringOptimization:
    """Test f-string optimization with simple interpolations."""

    def test_fstring_with_string_var_uses_concat(self):
        """f-string with string variable should use concatenation."""
        code = """
name = "World"
result = f"Hello, {name}!"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js
        assert "+" in js

    def test_fstring_with_string_var_result(self):
        """Verify f-string with string variable produces correct result."""
        code = """
name = "World"
result = f"Hello, {name}!"
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "Hello, World!"

    def test_fstring_with_int_var_uses_concat(self):
        """f-string with int variable should use concatenation."""
        code = """
count = 42
result = f"Count: {count}"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js
        assert "+" in js

    def test_fstring_with_int_var_result(self):
        """Verify f-string with int variable produces correct result."""
        code = """
count = 42
result = f"Count: {count}"
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "Count: 42"

    def test_fstring_with_float_var_uses_concat(self):
        """f-string with float variable should use concatenation."""
        code = """
value = 3.14
result = f"Pi is approximately {value}"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js
        assert "+" in js

    def test_fstring_with_bool_var_uses_concat(self):
        """f-string with bool variable should use concatenation."""
        code = """
flag = True
result = f"Flag is {flag}"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js
        assert "+" in js

    def test_fstring_multiple_vars_uses_concat(self):
        """f-string with multiple primitive vars should use concatenation."""
        code = """
name = "Alice"
age = 30
result = f"{name} is {age} years old"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js
        assert "+" in js

    def test_fstring_multiple_vars_result(self):
        """Verify f-string with multiple vars produces correct result."""
        code = """
name = "Alice"
age = 30
result = f"{name} is {age} years old"
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "Alice is 30 years old"


class TestFStringFallbackToFormat:
    """Test that f-strings fall back to format when needed."""

    def test_fstring_with_format_spec_uses_format(self):
        """f-string with format spec should use _pymeth_format."""
        code = """
value = 3.14159
result = f"Pi: {value:.2f}"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" in js

    def test_fstring_with_format_spec_result(self):
        """Verify f-string with format spec produces correct result."""
        code = """
value = 3.14159
result = f"Pi: {value:.2f}"
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "Pi: 3.14"

    def test_fstring_with_repr_conversion_uses_format(self):
        """f-string with !r conversion should use _pymeth_format."""
        code = """
name = "World"
result = f"Name: {name!r}"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" in js

    def test_fstring_with_str_conversion_uses_format(self):
        """f-string with !s conversion should use _pymeth_format."""
        code = """
value = 42
result = f"Value: {value!s}"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" in js

    def test_fstring_with_unknown_type_uses_format(self):
        """f-string with unknown type should use _pymeth_format."""
        code = """
def greet(name):
    return f"Hello, {name}!"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" in js

    def test_fstring_with_list_uses_format(self):
        """f-string with list variable should use _pymeth_format."""
        code = """
items = [1, 2, 3]
result = f"Items: {items}"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" in js


class TestFStringWithBuiltinTypes:
    """Test f-string optimization with types inferred from builtins."""

    def test_fstring_with_len_uses_concat(self):
        """f-string with len() result should use concatenation."""
        code = """
items = [1, 2, 3]
result = f"Count: {len(items)}"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js
        assert "+" in js

    def test_fstring_with_len_result(self):
        """Verify f-string with len() produces correct result."""
        code = """
items = [1, 2, 3]
result = f"Count: {len(items)}"
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "Count: 3"

    def test_fstring_with_str_upper_uses_concat(self):
        """f-string with str.upper() result should use concatenation."""
        code = """
name = "world"
result = f"Hello, {name.upper()}!"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js
        assert "+" in js

    def test_fstring_with_str_upper_result(self):
        """Verify f-string with str.upper() produces correct result."""
        code = """
name = "world"
result = f"Hello, {name.upper()}!"
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "Hello, WORLD!"

    def test_fstring_with_str_call_uses_concat(self):
        """f-string with str() call should use concatenation."""
        code = """
n = 42
result = f"Number: {str(n)}"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js
        assert "+" in js


class TestFStringWithAnnotatedParams:
    """Test f-string optimization with annotated function parameters."""

    def test_fstring_with_annotated_str_param_uses_concat(self):
        """f-string with annotated str param should use concatenation."""
        code = """
def greet(name: str) -> str:
    return f"Hello, {name}!"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js
        assert "+" in js

    def test_fstring_with_annotated_int_param_uses_concat(self):
        """f-string with annotated int param should use concatenation."""
        code = """
def show_count(n: int) -> str:
    return f"Count: {n}"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js
        assert "+" in js

    def test_fstring_with_mixed_annotated_params(self):
        """f-string with multiple annotated params should use concatenation."""
        code = """
def describe(name: str, age: int) -> str:
    return f"{name} is {age} years old"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js
        assert "+" in js


class TestFStringEdgeCases:
    """Test edge cases for f-string optimization."""

    def test_fstring_only_literal_uses_concat(self):
        """f-string with only literal text uses simple string."""
        code = """
result = f"Hello, World!"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js

    def test_fstring_only_var(self):
        """f-string with only a variable."""
        code = """
name = "World"
result = f"{name}"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js

    def test_fstring_only_var_result(self):
        """Verify f-string with only a variable produces correct result."""
        code = """
name = "World"
result = f"{name}"
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "World"

    def test_fstring_empty(self):
        """Empty f-string."""
        code = """
result = f""
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js

    def test_fstring_adjacent_vars(self):
        """f-string with adjacent variables."""
        code = """
a = "Hello"
b = "World"
result = f"{a}{b}"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js
        assert "+" in js

    def test_fstring_adjacent_vars_result(self):
        """Verify f-string with adjacent variables produces correct result."""
        code = """
a = "Hello"
b = "World"
result = f"{a}{b}"
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "HelloWorld"

    def test_fstring_with_expression(self):
        """f-string with simple expression using primitives."""
        code = """
x = 10
y = 20
result = f"Sum: {x + y}"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_format" not in js
        assert "+" in js

    def test_fstring_with_expression_result(self):
        """Verify f-string with expression produces correct result."""
        code = """
x = 10
y = 20
result = f"Sum: {x + y}"
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "Sum: 30"
