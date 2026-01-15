"""Constant folding optimization pass.

This pass evaluates constant expressions at compile time to reduce
the size and improve the performance of generated JavaScript code.

Supports:
- Binary arithmetic: 1 + 2 → 3
- Unary not: not True → False
- Boolean operations: True and False → False
- String operations: "a" + "b" → "ab", "x" * 3 → "xxx"
- List/tuple operations: len([1,2,3]) → 3 (when used with simple builtins)

This pass should run AFTER desugaring, since desugar transforms:
- -X → (0 - X)
- +X → X
- x += 1 → x = x + 1
"""

from __future__ import annotations

import ast as _ast
import operator
from typing import Any

from prescrypt.exceptions import JSError
from prescrypt.front import ast


def fold_constants(tree: ast.Module) -> ast.Module:
    """Apply constant folding to an AST tree.

    Args:
        tree: The AST module to optimize

    Returns:
        The optimized AST module with constant expressions folded
    """
    return _ast.fix_missing_locations(ConstantFolder().visit(tree))


class ConstantFolder(ast.NodeTransformer):
    """Fold constant expressions at compile time.

    This transformer visits the AST and replaces operations on
    constant values with their computed results.
    """

    # Mapping from AST operator types to Python operator functions
    BINARY_OPS: dict[type, Any] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    COMPARE_OPS: dict[type, Any] = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
    }

    def visit_BinOp(self, node: ast.BinOp) -> ast.expr:
        """Fold binary operations on constants.

        Examples:
            1 + 2 → 3
            "a" + "b" → "ab"
            "x" * 3 → "xxx"
            0 - 5 → -5 (from desugared -5)
        """
        # First, recursively fold children
        node = self.generic_visit(node)

        # Check if both operands are constants
        if not (isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant)):
            return node

        left_val = node.left.value
        right_val = node.right.value
        op_type = type(node.op)

        # Handle numeric operations
        if op_type in self.BINARY_OPS:
            # Only fold if both are numbers (int or float)
            if isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
                try:
                    result = self.BINARY_OPS[op_type](left_val, right_val)
                    return self._make_constant(result, node)
                except ZeroDivisionError:
                    line = getattr(node, "lineno", "?")
                    raise JSError(f"Division by zero at line {line}: {left_val} / {right_val}")
                except OverflowError:
                    line = getattr(node, "lineno", "?")
                    raise JSError(f"Numeric overflow at line {line}: {left_val} {op_type.__name__} {right_val}")
                except ValueError as e:
                    line = getattr(node, "lineno", "?")
                    raise JSError(f"Invalid operation at line {line}: {e}")

        # Handle string concatenation: "a" + "b" → "ab"
        if op_type == ast.Add:
            if isinstance(left_val, str) and isinstance(right_val, str):
                return self._make_constant(left_val + right_val, node)

        # Handle string/list repetition: "x" * 3 → "xxx"
        if op_type == ast.Mult:
            if isinstance(left_val, str) and isinstance(right_val, int):
                if right_val >= 0:
                    return self._make_constant(left_val * right_val, node)
            if isinstance(left_val, int) and isinstance(right_val, str):
                if left_val >= 0:
                    return self._make_constant(left_val * right_val, node)

        return node

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.expr:
        """Fold unary operations on constants.

        Examples:
            not True → False
            not False → True
            ~5 → -6 (bitwise invert)

        Note: UAdd (+x) and USub (-x) are handled by desugarer,
        which transforms them to x and (0 - x) respectively.
        """
        node = self.generic_visit(node)

        if not isinstance(node.operand, ast.Constant):
            return node

        value = node.operand.value

        if isinstance(node.op, ast.Not):
            return self._make_constant(not value, node)

        if isinstance(node.op, ast.Invert) and isinstance(value, int):
            return self._make_constant(~value, node)

        return node

    def visit_BoolOp(self, node: ast.BoolOp) -> ast.expr:
        """Fold boolean operations on constants.

        Examples:
            True and False → False
            True or False → True
            True and True → True

        Note: After desugaring, BoolOp always has exactly 2 values.
        """
        node = self.generic_visit(node)

        # After desugaring, BoolOp should have exactly 2 values
        if len(node.values) != 2:
            return node

        left, right = node.values

        # Both must be constants for folding
        if not (isinstance(left, ast.Constant) and isinstance(right, ast.Constant)):
            # Partial evaluation: if left is constant, we might be able to simplify
            if isinstance(left, ast.Constant):
                if isinstance(node.op, ast.And):
                    # False and x → False
                    if not left.value:
                        return left
                    # True and x → x
                    return right
                else:  # ast.Or
                    # True or x → True
                    if left.value:
                        return left
                    # False or x → x
                    return right
            return node

        # Both are constants - compute result
        if isinstance(node.op, ast.And):
            result = left.value and right.value
        else:  # ast.Or
            result = left.value or right.value

        return self._make_constant(result, node)

    def visit_Compare(self, node: ast.Compare) -> ast.expr:
        """Fold comparison operations on constants.

        Examples:
            1 < 2 → True
            "a" == "b" → False

        Note: After desugaring, Compare always has exactly 1 op and 1 comparator.
        """
        node = self.generic_visit(node)

        # After desugaring, should have exactly one comparison
        if len(node.ops) != 1 or len(node.comparators) != 1:
            return node

        left = node.left
        right = node.comparators[0]
        op_type = type(node.ops[0])

        # Both must be constants
        if not (isinstance(left, ast.Constant) and isinstance(right, ast.Constant)):
            return node

        left_val = left.value
        right_val = right.value

        # Handle 'in' and 'not in' for strings
        if isinstance(node.ops[0], ast.In):
            if isinstance(left_val, str) and isinstance(right_val, str):
                return self._make_constant(left_val in right_val, node)
            return node

        if isinstance(node.ops[0], ast.NotIn):
            if isinstance(left_val, str) and isinstance(right_val, str):
                return self._make_constant(left_val not in right_val, node)
            return node

        # Handle 'is' and 'is not' for None
        if isinstance(node.ops[0], ast.Is):
            if left_val is None or right_val is None:
                return self._make_constant(left_val is right_val, node)
            return node

        if isinstance(node.ops[0], ast.IsNot):
            if left_val is None or right_val is None:
                return self._make_constant(left_val is not right_val, node)
            return node

        # Standard comparisons
        if op_type in self.COMPARE_OPS:
            try:
                result = self.COMPARE_OPS[op_type](left_val, right_val)
                return self._make_constant(result, node)
            except TypeError:
                # Incompatible types
                return node

        return node

    def visit_IfExp(self, node: ast.IfExp) -> ast.expr:
        """Fold conditional expressions with constant conditions.

        Examples:
            1 if True else 2 → 1
            1 if False else 2 → 2
        """
        node = self.generic_visit(node)

        if isinstance(node.test, ast.Constant):
            if node.test.value:
                return node.body
            else:
                return node.orelse

        return node

    def visit_Subscript(self, node: ast.Subscript) -> ast.expr:
        """Fold subscript operations on constant sequences.

        Examples:
            "hello"[0] → "h"
            [1, 2, 3][1] → 2
            (1, 2, 3)[-1] → 3
        """
        node = self.generic_visit(node)

        # Value must be a constant or a constant list/tuple
        if isinstance(node.value, ast.Constant):
            value = node.value.value
        elif isinstance(node.value, (ast.List, ast.Tuple)):
            # Check if all elements are constants
            if not all(isinstance(el, ast.Constant) for el in node.value.elts):
                return node
            value = [el.value for el in node.value.elts]
            if isinstance(node.value, ast.Tuple):
                value = tuple(value)
        else:
            return node

        # Index must be a constant integer
        if not isinstance(node.slice, ast.Constant):
            return node

        index = node.slice.value

        if not isinstance(index, int):
            return node

        # Perform the subscript operation
        try:
            result = value[index]
            return self._make_constant(result, node)
        except (IndexError, TypeError):
            return node

    def _make_constant(self, value: Any, original_node: ast.AST) -> ast.Constant:
        """Create a Constant node preserving source location."""
        new_node = ast.Constant(value=value)
        return _ast.copy_location(new_node, original_node)
