"""Tests for type-informed code generation.

When types are known (from literals or inference), the compiler should
generate direct JavaScript operators instead of stdlib helpers.

Note: Annotated assignments (x: int = 1) are not yet supported.
Type inference currently works from:
- Literals (1, "hello", etc.)
- Propagation through simple assignments
"""

from __future__ import annotations

from prescrypt import py2js
from prescrypt.testing import js_eval


class TestAddOptimization:
    """Test that + uses native operator when types are known."""

    def test_int_literals_no_helper(self):
        """Int + Int literals should not use helper (constant folded)"""
        code = "x = 1 + 2"
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js
        # Constant folding produces: const x = 3;

    def test_float_literals_no_helper(self):
        """Float + Float literals should not use helper (constant folded)"""
        code = "x = 1.5 + 2.5"
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_string_literals_no_helper(self):
        """String + String literals should not use helper (constant folded)"""
        code = 'x = "hello" + "world"'
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_int_variable_plus_literal_uses_native(self):
        """Int variable + int literal should use native +"""
        code = """
x = 10
y = x + 5
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js
        assert "+" in js

    def test_string_variable_plus_literal_uses_native(self):
        """String variable + string literal should use native +"""
        code = '''
x = "hello"
y = x + " world"
'''
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js
        assert "+" in js

    def test_two_int_variables_use_native(self):
        """Two int variables should use native +"""
        code = """
x = 10
y = 20
z = x + y
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js
        assert "+" in js

    def test_two_string_variables_use_native(self):
        """Two string variables should use native +"""
        code = '''
x = "hello"
y = "world"
z = x + y
'''
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js
        assert "+" in js

    def test_unknown_types_use_helper(self):
        """Unknown types should still use helper"""
        code = """
def add(a, b):
    return a + b
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" in js

    def test_mixed_literal_and_unknown_uses_helper(self):
        """String literal + unknown should use helper"""
        code = """
def greet(name):
    return "Hello, " + name
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" in js

    def test_int_add_produces_correct_result(self):
        """Verify int addition works correctly"""
        code = """
x = 10
y = 20
result = x + y
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == 30

    def test_string_add_produces_correct_result(self):
        """Verify string concatenation works correctly"""
        code = '''
x = "hello"
y = "world"
result = x + y
'''
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "helloworld"


class TestMultOptimization:
    """Test that * uses native operator when types are known."""

    def test_int_literals_no_helper(self):
        """Int * Int literals should not use helper (constant folded)"""
        code = "x = 3 * 4"
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_mul" not in js

    def test_float_literals_no_helper(self):
        """Float * Float literals should not use helper"""
        code = "x = 1.5 * 2.0"
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_mul" not in js

    def test_int_variable_times_literal_uses_native(self):
        """Int variable * int literal should use native *"""
        code = """
x = 10
y = x * 5
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_mul" not in js
        assert "*" in js

    def test_two_int_variables_use_native(self):
        """Two int variables should use native *"""
        code = """
x = 6
y = 7
z = x * y
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_mul" not in js
        assert "*" in js

    def test_string_repeat_literal_uses_repeat(self):
        """String literal * Int literal should use .repeat() or fold"""
        code = 'x = "ab" * 3'
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_mul" not in js
        # Either constant-folded or uses .repeat()

    def test_string_variable_times_int_uses_repeat(self):
        """String variable * int should use .repeat()"""
        code = '''
s = "ab"
n = 3
result = s * n
'''
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_mul" not in js
        assert ".repeat(" in js

    def test_int_times_string_uses_repeat(self):
        """Int * String should use .repeat()"""
        code = '''
n = 3
s = "ab"
result = n * s
'''
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_mul" not in js
        assert ".repeat(" in js

    def test_unknown_types_use_helper(self):
        """Unknown types should still use helper"""
        code = """
def multiply(a, b):
    return a * b
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_mul" in js

    def test_int_mult_produces_correct_result(self):
        """Verify int multiplication works correctly"""
        code = """
x = 6
y = 7
result = x * y
"""
        js = py2js(code)
        assert js_eval(js + "\nresult;") == 42

    def test_string_repeat_produces_correct_result(self):
        """Verify string repeat works correctly"""
        code = '''
s = "ab"
n = 3
result = s * n
'''
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "ababab"

    def test_int_times_string_produces_correct_result(self):
        """Verify int * string repeat works correctly"""
        code = '''
n = 3
s = "ab"
result = n * s
'''
        js = py2js(code)
        assert js_eval(js + "\nresult;") == "ababab"


class TestTypeInferenceFromLiterals:
    """Test that literals are properly typed."""

    def test_int_literal_chain_no_helper(self):
        """Int literals should be typed as Int"""
        code = "x = 1 + 2 + 3"
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_string_literal_chain_no_helper(self):
        """String literals should be typed as String"""
        code = 'x = "a" + "b" + "c"'
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_chained_int_operations_use_native(self):
        """Chained operations with int variables should use native ops"""
        code = """
a = 1
b = 2
c = 3
result = a + b + c
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js

    def test_chained_string_operations_use_native(self):
        """Chained operations with string variables should use native ops"""
        code = '''
a = "x"
b = "y"
c = "z"
result = a + b + c
'''
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" not in js


class TestFallbackBehavior:
    """Test that unknown types still work correctly with helpers."""

    def test_list_concat_uses_helper(self):
        """List + List should use helper (type is List, not optimized)"""
        code = """
a = [1, 2]
b = [3, 4]
c = a + b
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" in js

    def test_list_concat_produces_correct_result(self):
        """Verify list concatenation still works"""
        code = """
a = [1, 2]
b = [3, 4]
result = a + b
"""
        js = py2js(code)
        result = js_eval(js + "\nresult;")
        assert result == [1, 2, 3, 4]

    def test_list_repeat_uses_helper(self):
        """List * Int should use helper (not optimized yet)"""
        code = """
a = [1, 2]
result = a * 3
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_mul" in js

    def test_list_repeat_produces_correct_result(self):
        """Verify list repeat still works"""
        code = """
a = [1, 2]
result = a * 3
"""
        js = py2js(code)
        result = js_eval(js + "\nresult;")
        assert result == [1, 2, 1, 2, 1, 2]

    def test_mixed_int_list_uses_helper(self):
        """Int + List should use helper"""
        # This would be a type error in Python, but we handle it gracefully
        code = """
def bad_add(x, items):
    return x + items
"""
        js = py2js(code, include_stdlib=False)
        assert "_pyfunc_op_add" in js
