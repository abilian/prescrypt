"""Tests for lambda expression compilation."""

from __future__ import annotations

from prescrypt import py2js


def js(code: str) -> str:
    """Compile Python to JavaScript without stdlib."""
    return py2js(code, include_stdlib=False)


class TestLambdaBasic:
    """Basic lambda expression tests."""

    def test_lambda_single_arg(self):
        """Lambda with single argument."""
        code = "f = lambda x: x + 1"
        result = js(code)
        assert "(x) =>" in result
        assert "const f" in result

    def test_lambda_multiple_args(self):
        """Lambda with multiple arguments."""
        code = "add = lambda a, b: a + b"
        result = js(code)
        assert "(a, b) =>" in result

    def test_lambda_no_args(self):
        """Lambda with no arguments."""
        code = "get_zero = lambda: 0"
        result = js(code)
        assert "() => (0)" in result

    def test_lambda_default_arg(self):
        """Lambda with default argument."""
        code = 'greet = lambda name="World": name'
        result = js(code)
        assert "(name = 'World')" in result

    def test_lambda_multiple_defaults(self):
        """Lambda with multiple default arguments."""
        code = "f = lambda x, y=1, z=2: x + y + z"
        result = js(code)
        assert "y = 1" in result
        assert "z = 2" in result

    def test_lambda_varargs(self):
        """Lambda with *args."""
        code = "f = lambda *args: len(args)"
        result = js(code)
        assert "...args" in result

    def test_lambda_mixed_args_and_defaults(self):
        """Lambda with positional and default args."""
        code = "f = lambda a, b, c=3: a + b + c"
        result = js(code)
        assert "(a, b, c = 3)" in result


class TestLambdaInline:
    """Lambda expressions used inline in function calls."""

    def test_lambda_in_sorted_key(self):
        """Lambda as key function in sorted()."""
        code = """
items = ["b", "a", "c"]
result = sorted(items, key=lambda x: x)
"""
        result = js(code)
        assert "(x) =>" in result
        assert "_pyfunc_sorted" in result

    def test_lambda_in_map(self):
        """Lambda in map() call."""
        code = """
nums = [1, 2, 3]
result = list(map(lambda x: x * 2, nums))
"""
        result = js(code)
        assert "(x) =>" in result
        assert "_pyfunc_map" in result

    def test_lambda_in_filter(self):
        """Lambda in filter() call."""
        code = """
nums = [1, 2, 3, 4]
evens = list(filter(lambda x: x % 2 == 0, nums))
"""
        result = js(code)
        assert "(x) =>" in result
        assert "_pyfunc_filter" in result


class TestLambdaExpressions:
    """Lambda body expression tests."""

    def test_lambda_string_operation(self):
        """Lambda with string operation."""
        code = "f = lambda s: s.upper()"
        result = js(code)
        assert "_pymeth_upper" in result

    def test_lambda_comparison(self):
        """Lambda with comparison."""
        code = "is_positive = lambda x: x > 0"
        result = js(code)
        # Accept either native operator or runtime helper for unknown types
        assert "(x > 0)" in result or "op_gt(x, 0)" in result

    def test_lambda_boolean_expression(self):
        """Lambda with boolean expression."""
        code = "is_valid = lambda x: x > 0 and x < 100"
        result = js(code)
        assert "&&" in result

    def test_lambda_ternary(self):
        """Lambda with ternary expression."""
        code = "abs_val = lambda x: x if x >= 0 else -x"
        result = js(code)
        assert "?" in result
        assert ":" in result

    def test_lambda_attribute_access(self):
        """Lambda accessing attribute."""
        code = "get_name = lambda obj: obj.name"
        result = js(code)
        assert "obj.name" in result

    def test_lambda_method_call(self):
        """Lambda calling method."""
        code = "to_lower = lambda s: s.lower()"
        result = js(code)
        assert "_pymeth_lower" in result


class TestLambdaAssignment:
    """Lambda assignment variations."""

    def test_lambda_reassignment(self):
        """Lambda can be reassigned."""
        code = """
f = lambda x: x + 1
f = lambda x: x + 2
"""
        result = js(code)
        assert "let f" in result or result.count("f =") == 2

    def test_lambda_in_list(self):
        """Lambda in list literal."""
        code = """
funcs = [lambda x: x + 1, lambda x: x * 2]
"""
        result = js(code)
        assert result.count("=>") == 2

    def test_lambda_in_dict(self):
        """Lambda as dict value."""
        code = """
ops = {"inc": lambda x: x + 1, "dec": lambda x: x - 1}
"""
        result = js(code)
        assert "inc" in result
        assert "dec" in result
        assert result.count("=>") == 2


class TestLambdaEdgeCases:
    """Edge cases for lambda expressions."""

    def test_nested_lambda(self):
        """Nested lambda expressions."""
        code = "f = lambda x: lambda y: x + y"
        result = js(code)
        assert result.count("=>") == 2

    def test_lambda_returning_lambda(self):
        """Lambda that returns another lambda."""
        code = """
make_adder = lambda n: lambda x: x + n
add5 = make_adder(5)
"""
        result = js(code)
        assert result.count("=>") == 2

    def test_lambda_with_complex_default(self):
        """Lambda with expression as default value."""
        code = "f = lambda x, y=1+2: x + y"
        result = js(code)
        # Default should be evaluated
        assert "y = 3" in result or "y = (1 + 2)" in result
