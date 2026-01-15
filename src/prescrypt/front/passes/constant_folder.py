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

    def visit_Call(self, node: ast.Call) -> ast.expr:
        """Inline simple builtin function calls on constant arguments.

        Examples:
            len([1, 2, 3]) → 3
            len("hello") → 5
            min(1, 2, 3) → 1
            max(1, 2, 3) → 3
            abs(-5) → 5
            sum([1, 2, 3]) → 6
            bool(0) → False
            int("123") → 123
            float("1.5") → 1.5
            str(123) → "123"
            round(3.14159, 2) → 3.14
        """
        node = self.generic_visit(node)

        # Only handle simple function names (not methods)
        if not isinstance(node.func, ast.Name):
            return node

        func_name = node.func.id
        args = node.args

        # Skip if there are keyword arguments (for simplicity)
        if node.keywords:
            return node

        # Try to inline the function call
        try:
            result = self._try_inline_call(func_name, args, node)
            if result is not None:
                return result
        except (ValueError, TypeError, OverflowError):
            # If inlining fails, keep the original call
            pass

        return node

    def _try_inline_call(
        self, func_name: str, args: list[ast.expr], node: ast.Call
    ) -> ast.Constant | None:
        """Try to inline a function call. Returns None if not possible."""

        # len() on constant sequences
        if func_name == "len" and len(args) == 1:
            arg = args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, (str, bytes)):
                return self._make_constant(len(arg.value), node)
            if isinstance(arg, (ast.List, ast.Tuple)):
                return self._make_constant(len(arg.elts), node)
            if isinstance(arg, ast.Dict):
                return self._make_constant(len(arg.keys), node)
            if isinstance(arg, ast.Set):
                return self._make_constant(len(arg.elts), node)

        # min/max on constant arguments
        if func_name in ("min", "max") and args:
            const_values = self._extract_constant_values(args)
            if const_values is not None:
                # Handle single iterable argument
                if len(const_values) == 1 and isinstance(const_values[0], (list, tuple)):
                    const_values = list(const_values[0])
                if const_values:
                    func = min if func_name == "min" else max
                    return self._make_constant(func(const_values), node)

        # abs() on constant number
        if func_name == "abs" and len(args) == 1:
            if isinstance(args[0], ast.Constant) and isinstance(args[0].value, (int, float)):
                return self._make_constant(abs(args[0].value), node)

        # sum() on constant list
        if func_name == "sum" and len(args) in (1, 2):
            if isinstance(args[0], (ast.List, ast.Tuple)):
                values = self._extract_list_values(args[0])
                if values is not None and all(isinstance(v, (int, float)) for v in values):
                    start = 0
                    if len(args) == 2 and isinstance(args[1], ast.Constant):
                        start = args[1].value
                    return self._make_constant(sum(values, start), node)

        # bool() on constant
        if func_name == "bool" and len(args) == 1:
            if isinstance(args[0], ast.Constant):
                return self._make_constant(bool(args[0].value), node)
            if isinstance(args[0], (ast.List, ast.Tuple)):
                # Empty list/tuple is falsy
                return self._make_constant(len(args[0].elts) > 0, node)

        # int() on constant
        if func_name == "int" and len(args) in (1, 2):
            if len(args) == 1 and isinstance(args[0], ast.Constant):
                val = args[0].value
                if isinstance(val, (int, float, str)):
                    return self._make_constant(int(val), node)
            elif len(args) == 2:
                if isinstance(args[0], ast.Constant) and isinstance(args[1], ast.Constant):
                    return self._make_constant(int(args[0].value, args[1].value), node)

        # float() on constant
        if func_name == "float" and len(args) == 1:
            if isinstance(args[0], ast.Constant):
                val = args[0].value
                if isinstance(val, (int, float, str)):
                    return self._make_constant(float(val), node)

        # str() on constant (but NOT booleans - JS uses "true"/"false", Python uses "True"/"False")
        if func_name == "str" and len(args) == 1:
            if isinstance(args[0], ast.Constant):
                val = args[0].value
                # Don't inline booleans - let the JS runtime handle them for JS semantics
                if not isinstance(val, bool):
                    return self._make_constant(str(val), node)

        # round() on constant
        if func_name == "round" and len(args) in (1, 2):
            if isinstance(args[0], ast.Constant) and isinstance(args[0].value, (int, float)):
                if len(args) == 1:
                    return self._make_constant(round(args[0].value), node)
                elif isinstance(args[1], ast.Constant) and isinstance(args[1].value, int):
                    return self._make_constant(round(args[0].value, args[1].value), node)

        # chr() on constant int
        if func_name == "chr" and len(args) == 1:
            if isinstance(args[0], ast.Constant) and isinstance(args[0].value, int):
                val = args[0].value
                if 0 <= val <= 0x10FFFF:
                    return self._make_constant(chr(val), node)

        # ord() on constant single-char string
        if func_name == "ord" and len(args) == 1:
            if isinstance(args[0], ast.Constant) and isinstance(args[0].value, str):
                if len(args[0].value) == 1:
                    return self._make_constant(ord(args[0].value), node)

        return None

    def _extract_constant_values(self, args: list[ast.expr]) -> list | None:
        """Extract constant values from arguments. Returns None if any arg is not constant."""
        values = []
        for arg in args:
            if isinstance(arg, ast.Constant):
                values.append(arg.value)
            elif isinstance(arg, (ast.List, ast.Tuple)):
                inner = self._extract_list_values(arg)
                if inner is None:
                    return None
                values.append(inner)
            else:
                return None
        return values

    def _extract_list_values(self, node: ast.List | ast.Tuple) -> list | None:
        """Extract constant values from a list/tuple. Returns None if any element is not constant."""
        values = []
        for el in node.elts:
            if isinstance(el, ast.Constant):
                values.append(el.value)
            else:
                return None
        return values

    def _make_constant(self, value: Any, original_node: ast.AST) -> ast.Constant:
        """Create a Constant node preserving source location."""
        new_node = ast.Constant(value=value)
        return _ast.copy_location(new_node, original_node)
