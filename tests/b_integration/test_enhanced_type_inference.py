"""Tests for enhanced type inference (Phase 2).

Tests that type inference correctly handles:
- Built-in function return types
- Method return types
- Improved arithmetic type inference
"""

from __future__ import annotations

from prescrypt import py2js
from prescrypt.testing import js_eval


class TestBuiltinReturnTypes:
    """Test that built-in function return types are inferred."""

    def test_len_returns_int(self):
        """len() should return Int, enabling native + with int."""
        code = """
items = [1, 2, 3]
n = len(items)
result = n + 10
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js
        assert "+" in js

    def test_len_result_correct(self):
        """Verify len + int produces correct result."""
        code = """
items = [1, 2, 3]
n = len(items)
result = n + 10
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == 13

    def test_str_returns_string(self):
        """str() should return String, enabling native +."""
        code = """
n = 42
s = str(n)
result = s + "!"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js
        assert "+" in js

    def test_str_result_correct(self):
        """Verify str + string produces correct result."""
        code = """
n = 42
s = str(n)
result = s + "!"
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "42!"

    def test_int_returns_int(self):
        """int() should return Int, enabling native +."""
        code = """
s = "42"
n = int(s)
result = n + 8
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js
        assert "+" in js

    def test_ord_returns_int(self):
        """ord() should return Int."""
        code = """
c = "A"
n = ord(c)
result = n + 1
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_chr_returns_string(self):
        """chr() should return String."""
        code = """
n = 65
c = chr(n)
result = c + "BC"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_isinstance_returns_bool(self):
        """isinstance() should return Bool."""
        code = """
x = 42
b = isinstance(x, int)
"""
        js = py2js(code, include_stdlib=False)
        # Bool type should be inferred
        # This test mainly verifies no errors during compilation


class TestMethodReturnTypes:
    """Test that method return types are inferred."""

    def test_string_upper_returns_string(self):
        """str.upper() should return String."""
        code = """
s = "hello"
u = s.upper()
result = u + "!"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js
        assert "+" in js

    def test_string_upper_result_correct(self):
        """Verify str.upper() + string produces correct result."""
        code = """
s = "hello"
u = s.upper()
result = u + "!"
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "HELLO!"

    def test_string_lower_returns_string(self):
        """str.lower() should return String."""
        code = """
s = "HELLO"
l = s.lower()
result = l + " world"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_string_strip_returns_string(self):
        """str.strip() should return String."""
        code = """
s = "  hello  "
stripped = s.strip()
result = stripped + "!"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_string_replace_returns_string(self):
        """str.replace() should return String."""
        code = """
s = "hello"
r = s.replace("l", "L")
result = r + "!"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_string_find_returns_int(self):
        """str.find() should return Int."""
        code = """
s = "hello"
idx = s.find("l")
result = idx + 10
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_string_find_result_correct(self):
        """Verify str.find() + int produces correct result."""
        code = """
s = "hello"
idx = s.find("l")
result = idx + 10
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == 12  # 2 + 10

    def test_string_count_returns_int(self):
        """str.count() should return Int."""
        code = """
s = "hello"
n = s.count("l")
result = n + 5
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_string_startswith_returns_bool(self):
        """str.startswith() should return Bool."""
        code = """
s = "hello"
b = s.startswith("he")
"""
        js = py2js(code, include_stdlib=False)
        # Mainly verifies compilation works

    def test_string_split_returns_list(self):
        """str.split() should return List."""
        code = """
s = "a,b,c"
parts = s.split(",")
"""
        js = py2js(code, include_stdlib=False)
        # List type should be inferred

    def test_string_join_returns_string(self):
        """str.join() should return String."""
        code = """
sep = ", "
parts = ["a", "b", "c"]
result = sep.join(parts) + "!"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js


class TestArithmeticTypeInference:
    """Test improved arithmetic type inference."""

    def test_int_div_returns_float(self):
        """Division always returns Float in Python 3."""
        code = """
a = 10
b = 3
result = a / b
"""
        js = py2js(code, include_stdlib=False)
        # result should have Float type

    def test_int_floordiv_returns_int(self):
        """Floor division of ints returns Int."""
        code = """
a = 10
b = 3
result = a // b + 1
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_int_mod_returns_int(self):
        """Modulo of ints returns Int."""
        code = """
a = 10
b = 3
result = a % b + 1
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_int_pow_returns_int(self):
        """Power of ints returns Int."""
        code = """
a = 2
b = 3
result = a ** b + 1
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_float_promotion(self):
        """Int + Float should promote to Float."""
        code = """
a = 10
b = 2.5
c = a + b
result = c + 1.0
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_string_mult_int_returns_string(self):
        """String * Int should return String."""
        code = """
s = "ab"
n = 3
r = s * n
result = r + "!"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_int_sub_int_returns_int(self):
        """Int - Int should return Int."""
        code = """
a = 10
b = 3
c = a - b
result = c + 1
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js


class TestChainedInference:
    """Test that type inference chains through multiple operations."""

    def test_chained_string_methods(self):
        """Chained string methods should preserve String type."""
        code = """
s = "  Hello World  "
result = s.strip().lower() + "!"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_chained_string_methods_result(self):
        """Verify chained string methods produce correct result."""
        code = """
s = "  Hello World  "
result = s.strip().lower() + "!"
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "hello world!"

    def test_len_plus_len(self):
        """len() + len() should use native +."""
        code = """
a = [1, 2, 3]
b = [4, 5]
result = len(a) + len(b)
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_len_plus_len_result(self):
        """Verify len + len produces correct result."""
        code = """
a = [1, 2, 3]
b = [4, 5]
result = len(a) + len(b)
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == 5

    def test_str_from_int_plus_str(self):
        """str(int) + str should use native +."""
        code = """
n = 42
result = str(n) + " is the answer"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js


class TestFunctionParameterTypes:
    """Test that function parameter annotations propagate types."""

    def test_annotated_int_params_use_native(self):
        """Int parameters should use native + inside function."""
        code = """
def add(a: int, b: int) -> int:
    return a + b
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js
        assert "+" in js

    def test_annotated_str_params_use_native(self):
        """String parameters should use native + inside function."""
        code = """
def concat(a: str, b: str) -> str:
    return a + b
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js
        assert "+" in js

    def test_mixed_annotated_uses_helper(self):
        """Mixed annotated and unknown params should use helper."""
        code = """
def add(a: int, b):
    return a + b
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" in js

    def test_unannotated_params_use_helper(self):
        """Unannotated parameters should use helper."""
        code = """
def add(a, b):
    return a + b
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" in js
