"""Tests for equality optimization (Phase 3).

When both operands have primitive types (Int, Float, String, Bool),
use === instead of _pyfunc_op_equals for better performance.
"""

from __future__ import annotations

from prescrypt import py2js
from prescrypt.testing import js_eval


class TestIntEquality:
    """Test equality optimization for integers."""

    def test_int_eq_int_uses_strict_equality(self):
        """Int == Int should use ===."""
        code = """
x = 10
y = 20
result = x == y
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" not in js
        assert "===" in js

    def test_int_eq_int_result_true(self):
        """Verify int == int works correctly (true case)."""
        code = """
x = 10
y = 10
result = x == y
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") is True

    def test_int_eq_int_result_false(self):
        """Verify int == int works correctly (false case)."""
        code = """
x = 10
y = 20
result = x == y
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") is False

    def test_int_neq_int_uses_strict_inequality(self):
        """Int != Int should use !==."""
        code = """
x = 10
y = 20
result = x != y
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" not in js
        assert "!==" in js

    def test_int_neq_int_result(self):
        """Verify int != int works correctly."""
        code = """
x = 10
y = 20
result = x != y
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") is True


class TestStringEquality:
    """Test equality optimization for strings."""

    def test_str_eq_str_uses_strict_equality(self):
        """String == String should use ===."""
        code = """
x = "hello"
y = "world"
result = x == y
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" not in js
        assert "===" in js

    def test_str_eq_str_result_true(self):
        """Verify string == string works correctly (true case)."""
        code = """
x = "hello"
y = "hello"
result = x == y
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") is True

    def test_str_eq_str_result_false(self):
        """Verify string == string works correctly (false case)."""
        code = """
x = "hello"
y = "world"
result = x == y
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") is False

    def test_str_neq_str_uses_strict_inequality(self):
        """String != String should use !==."""
        code = """
x = "hello"
y = "world"
result = x != y
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" not in js
        assert "!==" in js


class TestFloatEquality:
    """Test equality optimization for floats."""

    def test_float_eq_float_uses_strict_equality(self):
        """Float == Float should use ===."""
        code = """
x = 1.5
y = 2.5
result = x == y
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" not in js
        assert "===" in js

    def test_float_eq_float_result(self):
        """Verify float == float works correctly."""
        code = """
x = 1.5
y = 1.5
result = x == y
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") is True

    def test_int_eq_float_uses_strict_equality(self):
        """Int == Float (both numeric/primitive) should use ===."""
        code = """
x = 10
y = 10.0
result = x == y
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" not in js
        assert "===" in js


class TestBoolEquality:
    """Test equality optimization for booleans."""

    def test_bool_eq_bool_uses_strict_equality(self):
        """Bool == Bool should use ===."""
        code = """
x = True
y = False
result = x == y
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" not in js
        assert "===" in js

    def test_bool_eq_bool_result(self):
        """Verify bool == bool works correctly."""
        code = """
x = True
y = True
result = x == y
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") is True


class TestFallbackToHelper:
    """Test that non-primitive types still use helper."""

    def test_list_eq_list_uses_helper(self):
        """List == List should use helper for deep comparison."""
        code = """
x = [1, 2, 3]
y = [1, 2, 3]
result = x == y
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" in js

    def test_list_eq_list_result(self):
        """Verify list == list works correctly with helper."""
        code = """
x = [1, 2, 3]
y = [1, 2, 3]
result = x == y
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") is True

    def test_dict_eq_dict_uses_helper(self):
        """Dict == Dict should use helper for deep comparison."""
        code = """
x = {"a": 1}
y = {"a": 1}
result = x == y
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" in js

    def test_unknown_eq_unknown_uses_helper(self):
        """Unknown types should use helper."""
        code = """
def check_equal(a, b):
    return a == b
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" in js

    def test_primitive_eq_unknown_uses_helper(self):
        """Primitive == Unknown should use helper."""
        code = """
def check(x):
    return x == 10
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" in js


class TestWithBuiltinReturnTypes:
    """Test equality with inferred types from builtins."""

    def test_len_eq_int_uses_strict_equality(self):
        """len() == int should use === since len returns Int."""
        code = """
items = [1, 2, 3]
result = len(items) == 3
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" not in js
        assert "===" in js

    def test_len_eq_int_result(self):
        """Verify len() == int works correctly."""
        code = """
items = [1, 2, 3]
result = len(items) == 3
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") is True

    def test_str_upper_eq_str_uses_strict_equality(self):
        """str.upper() == str should use ===."""
        code = """
s = "hello"
result = s.upper() == "HELLO"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" not in js
        assert "===" in js


class TestInConditionals:
    """Test equality optimization in if statements."""

    def test_if_int_eq_int(self):
        """If with int == int should use ===."""
        code = """
x = 10
if x == 10:
    result = "yes"
else:
    result = "no"
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" not in js
        assert "===" in js

    def test_if_int_eq_int_result(self):
        """Verify if with int == int executes correctly."""
        code = """
x = 10
result = "no"
if x == 10:
    result = "yes"
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "yes"

    def test_while_str_neq_str(self):
        """While with str != str should use !==."""
        code = """
s = "a"
count = 0
while s != "aaaa":
    s = s + "a"
    count = count + 1
result = count
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" not in js
        assert "!==" in js


class TestAnnotatedParameters:
    """Test equality with annotated function parameters."""

    def test_annotated_int_params_eq(self):
        """Annotated int params should use === for equality."""
        code = """
def is_equal(a: int, b: int) -> bool:
    return a == b
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" not in js
        assert "===" in js

    def test_annotated_str_params_eq(self):
        """Annotated str params should use === for equality."""
        code = """
def is_equal(a: str, b: str) -> bool:
    return a == b
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_equals" not in js
        assert "===" in js
