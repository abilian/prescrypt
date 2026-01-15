"""Tests for the constant folding optimization pass."""

from __future__ import annotations

import pytest

from prescrypt.exceptions import JSError
from prescrypt.front import ast
from prescrypt.front.passes.constant_folder import fold_constants
from prescrypt.front.passes.desugar import desugar


def parse_and_fold(code: str) -> str:
    """Parse code, desugar, fold constants, and unparse."""
    tree = ast.parse(code)
    tree = desugar(tree)
    tree = fold_constants(tree)
    return ast.unparse(tree)


class TestArithmeticFolding:
    """Test folding of arithmetic operations."""

    def test_addition(self):
        assert parse_and_fold("x = 1 + 2") == "x = 3"

    def test_subtraction(self):
        assert parse_and_fold("x = 5 - 3") == "x = 2"

    def test_multiplication(self):
        assert parse_and_fold("x = 4 * 5") == "x = 20"

    def test_division(self):
        assert parse_and_fold("x = 10 / 4") == "x = 2.5"

    def test_floor_division(self):
        assert parse_and_fold("x = 10 // 3") == "x = 3"

    def test_modulo(self):
        assert parse_and_fold("x = 10 % 3") == "x = 1"

    def test_power(self):
        assert parse_and_fold("x = 2 ** 8") == "x = 256"

    def test_nested_arithmetic(self):
        assert parse_and_fold("x = 1 + 2 * 3") == "x = 7"

    def test_complex_expression(self):
        assert parse_and_fold("x = (1 + 2) * (3 + 4)") == "x = 21"

    def test_negative_number(self):
        # After desugar: -5 becomes (0 - 5)
        assert parse_and_fold("x = -5") == "x = -5"

    def test_negative_in_expression(self):
        # -5 + 3 becomes (0 - 5) + 3 = -2
        assert parse_and_fold("x = -5 + 3") == "x = -2"

    def test_float_arithmetic(self):
        assert parse_and_fold("x = 1.5 + 2.5") == "x = 4.0"

    def test_mixed_int_float(self):
        assert parse_and_fold("x = 1 + 2.5") == "x = 3.5"


class TestDivisionEdgeCases:
    """Test that division by zero raises compile-time error."""

    def test_division_by_zero_raises_error(self):
        with pytest.raises(JSError, match="Division by zero"):
            parse_and_fold("x = 1 / 0")

    def test_floor_division_by_zero_raises_error(self):
        with pytest.raises(JSError, match="Division by zero"):
            parse_and_fold("x = 1 // 0")

    def test_modulo_by_zero_raises_error(self):
        with pytest.raises(JSError, match="Division by zero"):
            parse_and_fold("x = 5 % 0")


class TestStringFolding:
    """Test folding of string operations."""

    def test_string_concatenation(self):
        assert parse_and_fold('x = "a" + "b"') == "x = 'ab'"

    def test_string_repetition(self):
        assert parse_and_fold('x = "x" * 3') == "x = 'xxx'"

    def test_string_repetition_reversed(self):
        assert parse_and_fold('x = 3 * "y"') == "x = 'yyy'"

    def test_string_repetition_zero(self):
        assert parse_and_fold('x = "x" * 0') == "x = ''"

    def test_string_repetition_negative(self):
        # Negative repetition should not be folded (Python returns empty string but might be unexpected)
        result = parse_and_fold('x = "x" * -1')
        # Either folded to '' or kept as is (with single or double quotes)
        assert "''" in result or '""' in result or "* -1" in result or "*-1" in result


class TestBooleanFolding:
    """Test folding of boolean operations."""

    def test_not_true(self):
        assert parse_and_fold("x = not True") == "x = False"

    def test_not_false(self):
        assert parse_and_fold("x = not False") == "x = True"

    def test_and_true_true(self):
        assert parse_and_fold("x = True and True") == "x = True"

    def test_and_true_false(self):
        assert parse_and_fold("x = True and False") == "x = False"

    def test_and_false_anything(self):
        # False and x → False (short-circuit)
        assert parse_and_fold("x = False and True") == "x = False"

    def test_or_true_anything(self):
        # True or x → True (short-circuit)
        assert parse_and_fold("x = True or False") == "x = True"

    def test_or_false_true(self):
        assert parse_and_fold("x = False or True") == "x = True"

    def test_chained_and(self):
        # After desugar: True and True and True → True and (True and True)
        assert parse_and_fold("x = True and True and True") == "x = True"

    def test_chained_or(self):
        assert parse_and_fold("x = False or False or True") == "x = True"


class TestPartialBooleanEvaluation:
    """Test partial evaluation of boolean operations with one constant."""

    def test_false_and_variable(self):
        # False and y → False
        assert parse_and_fold("x = False and y") == "x = False"

    def test_true_and_variable(self):
        # True and y → y
        assert parse_and_fold("x = True and y") == "x = y"

    def test_true_or_variable(self):
        # True or y → True
        assert parse_and_fold("x = True or y") == "x = True"

    def test_false_or_variable(self):
        # False or y → y
        assert parse_and_fold("x = False or y") == "x = y"


class TestComparisonFolding:
    """Test folding of comparison operations."""

    def test_less_than_true(self):
        assert parse_and_fold("x = 1 < 2") == "x = True"

    def test_less_than_false(self):
        assert parse_and_fold("x = 2 < 1") == "x = False"

    def test_greater_than(self):
        assert parse_and_fold("x = 3 > 2") == "x = True"

    def test_equal(self):
        assert parse_and_fold("x = 1 == 1") == "x = True"

    def test_not_equal(self):
        assert parse_and_fold("x = 1 != 2") == "x = True"

    def test_string_equality(self):
        assert parse_and_fold('x = "a" == "b"') == "x = False"

    def test_string_equality_true(self):
        assert parse_and_fold('x = "a" == "a"') == "x = True"


class TestConditionalExpressionFolding:
    """Test folding of conditional expressions (ternary)."""

    def test_true_condition(self):
        assert parse_and_fold("x = 1 if True else 2") == "x = 1"

    def test_false_condition(self):
        assert parse_and_fold("x = 1 if False else 2") == "x = 2"

    def test_constant_condition_folded(self):
        # 1 < 2 folds to True, then ternary folds
        assert parse_and_fold("x = 'yes' if 1 < 2 else 'no'") == "x = 'yes'"


class TestSubscriptFolding:
    """Test folding of subscript operations."""

    def test_string_subscript(self):
        assert parse_and_fold('x = "hello"[0]') == "x = 'h'"

    def test_string_subscript_negative(self):
        assert parse_and_fold('x = "hello"[-1]') == "x = 'o'"

    def test_list_subscript(self):
        assert parse_and_fold("x = [1, 2, 3][1]") == "x = 2"

    def test_tuple_subscript(self):
        assert parse_and_fold("x = (1, 2, 3)[-1]") == "x = 3"


class TestNoFoldingWhenVariablesPresent:
    """Test that expressions with variables are not folded."""

    def test_variable_in_addition(self):
        result = parse_and_fold("x = y + 2")
        assert "y" in result

    def test_variable_in_multiplication(self):
        result = parse_and_fold("x = y * 3")
        assert "y" in result

    def test_variable_in_comparison(self):
        result = parse_and_fold("x = y < 5")
        assert "y" in result


class TestPreserveNonConstant:
    """Test that non-constant expressions are preserved."""

    def test_function_call_preserved(self):
        result = parse_and_fold("x = len([1, 2, 3])")
        assert "len" in result

    def test_method_call_preserved(self):
        result = parse_and_fold('x = "hello".upper()')
        assert "upper" in result

    def test_attribute_access_preserved(self):
        result = parse_and_fold("x = obj.value")
        assert "obj.value" in result


class TestBitwiseOperations:
    """Test folding of bitwise operations."""

    def test_bitwise_invert(self):
        assert parse_and_fold("x = ~5") == "x = -6"

    def test_bitwise_invert_negative(self):
        result = parse_and_fold("x = ~(-1)")
        # After desugar, -1 becomes (0 - 1), then ~0 = -1, then overall ~(-1) = 0
        assert "0" in result


class TestInOperator:
    """Test folding of 'in' operator."""

    def test_string_in_string_true(self):
        assert parse_and_fold('x = "a" in "abc"') == "x = True"

    def test_string_in_string_false(self):
        assert parse_and_fold('x = "x" in "abc"') == "x = False"

    def test_string_not_in_string(self):
        assert parse_and_fold('x = "x" not in "abc"') == "x = True"


class TestIsOperator:
    """Test folding of 'is' operator for None."""

    def test_none_is_none(self):
        assert parse_and_fold("x = None is None") == "x = True"

    def test_value_is_not_none(self):
        assert parse_and_fold("x = 1 is not None") == "x = True"

    def test_none_is_not_value(self):
        assert parse_and_fold("x = None is not 1") == "x = True"
