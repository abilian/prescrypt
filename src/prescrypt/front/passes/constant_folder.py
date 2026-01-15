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

Architecture: Hybrid DSL approach
- Declarative tables for simple, regular rules
- Pattern matching for complex cases with multiple variations
"""

from __future__ import annotations

import ast as _ast
import operator
from typing import Any, Callable

from prescrypt.exceptions import JSError
from prescrypt.front import ast

# =============================================================================
# Type Aliases
# =============================================================================
Number = (int, float)
Text = (str, bytes)

# =============================================================================
# Declarative Rule Tables
# =============================================================================

# Binary operations on numbers: (op_type) -> operator_func
NUMERIC_BINARY_OPS: dict[type, Callable] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

# Comparison operations: (op_type) -> operator_func
COMPARE_OPS: dict[type, Callable] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}

# Simple single-arg functions: (name, allowed_types, compute_func, guard)
# guard: optional predicate on the value, returns True if folding is allowed
SIMPLE_FUNCTIONS: list[tuple[str, type | tuple, Callable, Callable | None]] = [
    ("abs", Number, abs, None),
    ("bool", object, bool, None),
    ("chr", int, chr, lambda v: 0 <= v <= 0x10FFFF),
    ("ord", str, ord, lambda s: len(s) == 1),
    ("float", (int, float, str), float, None),
    ("int", (int, float, str), int, None),
    # Don't inline str(bool) - JS uses "true"/"false", Python uses "True"/"False"
    ("str", (int, float, str), str, lambda v: not isinstance(v, bool)),
]


# =============================================================================
# Public API
# =============================================================================


def fold_constants(tree: ast.Module) -> ast.Module:
    """Apply constant folding to an AST tree.

    Args:
        tree: The AST module to optimize

    Returns:
        The optimized AST module with constant expressions folded
    """
    return _ast.fix_missing_locations(ConstantFolder().visit(tree))


# =============================================================================
# Constant Folder Implementation
# =============================================================================


class ConstantFolder(ast.NodeTransformer):
    """Fold constant expressions at compile time.

    Uses a hybrid approach:
    - Declarative tables for regular patterns
    - Pattern matching for complex/irregular cases
    """

    def visit_BinOp(self, node: ast.BinOp) -> ast.expr:
        """Fold binary operations on constants."""
        node = self.generic_visit(node)

        if not (
            isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant)
        ):
            return node

        left, right = node.left.value, node.right.value
        op_type = type(node.op)

        # Table-driven: numeric operations
        if op_type in NUMERIC_BINARY_OPS:
            if isinstance(left, Number) and isinstance(right, Number):
                return self._compute_binary(
                    NUMERIC_BINARY_OPS[op_type], left, right, node
                )

        # Pattern matching: string operations
        match (op_type, left, right):
            case (ast.Add, str(), str()):
                return self._make_constant(left + right, node)
            case (ast.Mult, str(), int()) if right >= 0:
                return self._make_constant(left * right, node)
            case (ast.Mult, int(), str()) if left >= 0:
                return self._make_constant(left * right, node)

        return node

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.expr:
        """Fold unary operations on constants."""
        node = self.generic_visit(node)

        if not isinstance(node.operand, ast.Constant):
            return node

        value = node.operand.value

        match node.op:
            case ast.Not():
                return self._make_constant(not value, node)
            case ast.Invert() if isinstance(value, int):
                return self._make_constant(~value, node)

        return node

    def visit_BoolOp(self, node: ast.BoolOp) -> ast.expr:
        """Fold boolean operations on constants."""
        node = self.generic_visit(node)

        if len(node.values) != 2:
            return node

        left, right = node.values
        is_and = isinstance(node.op, ast.And)

        # Both constants: compute result
        if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
            if is_and:
                return self._make_constant(left.value and right.value, node)
            return self._make_constant(left.value or right.value, node)

        # Partial evaluation: left is constant
        if isinstance(left, ast.Constant):
            if is_and:
                return left if not left.value else right  # False and x → False
            return left if left.value else right  # True or x → True

        return node

    def visit_Compare(self, node: ast.Compare) -> ast.expr:
        """Fold comparison operations on constants."""
        node = self.generic_visit(node)

        if len(node.ops) != 1 or len(node.comparators) != 1:
            return node

        if not (
            isinstance(node.left, ast.Constant)
            and isinstance(node.comparators[0], ast.Constant)
        ):
            return node

        left, right = node.left.value, node.comparators[0].value
        op = node.ops[0]
        op_type = type(op)

        # Table-driven: standard comparisons
        if op_type in COMPARE_OPS:
            try:
                return self._make_constant(COMPARE_OPS[op_type](left, right), node)
            except TypeError:
                return node

        # Pattern matching: special comparisons
        match op:
            case ast.In() if isinstance(left, str) and isinstance(right, str):
                return self._make_constant(left in right, node)
            case ast.NotIn() if isinstance(left, str) and isinstance(right, str):
                return self._make_constant(left not in right, node)
            case ast.Is() if left is None or right is None:
                return self._make_constant(left is right, node)
            case ast.IsNot() if left is None or right is None:
                return self._make_constant(left is not right, node)

        return node

    def visit_IfExp(self, node: ast.IfExp) -> ast.expr:
        """Fold conditional expressions with constant conditions."""
        node = self.generic_visit(node)

        if isinstance(node.test, ast.Constant):
            return node.body if node.test.value else node.orelse

        return node

    def visit_Subscript(self, node: ast.Subscript) -> ast.expr:
        """Fold subscript operations on constant sequences."""
        node = self.generic_visit(node)

        if not isinstance(node.slice, ast.Constant):
            return node

        index = node.slice.value
        if not isinstance(index, int):
            return node

        # Extract sequence value
        match node.value:
            case ast.Constant(value=v):
                seq = v
            case ast.List(elts=elts) | ast.Tuple(elts=elts):
                if not all(isinstance(el, ast.Constant) for el in elts):
                    return node
                seq = [el.value for el in elts]
            case _:
                return node

        try:
            return self._make_constant(seq[index], node)
        except (IndexError, TypeError):
            return node

    def visit_Call(self, node: ast.Call) -> ast.expr:
        """Inline simple builtin function calls on constant arguments."""
        node = self.generic_visit(node)

        if not isinstance(node.func, ast.Name) or node.keywords:
            return node

        name, args = node.func.id, node.args

        # Try table-driven simple functions first
        if len(args) == 1 and isinstance(args[0], ast.Constant):
            result = self._try_simple_function(name, args[0].value)
            if result is not None:
                return self._make_constant(result, node)

        # Pattern matching for complex cases
        try:
            match (name, args):
                # len() on various types
                case ("len", [ast.Constant(value=v)]) if isinstance(v, Text):
                    return self._make_constant(len(v), node)
                case ("len", [ast.List(elts=e) | ast.Tuple(elts=e) | ast.Set(elts=e)]):
                    return self._make_constant(len(e), node)
                case ("len", [ast.Dict(keys=k)]):
                    return self._make_constant(len(k), node)

                # min/max with variadic args
                case (("min" | "max") as fn, args) if args:
                    if values := self._extract_numbers(args):
                        func = min if fn == "min" else max
                        return self._make_constant(func(values), node)

                # sum() with optional start
                case ("sum", [ast.List(elts=e) | ast.Tuple(elts=e)]):
                    values = self._const_list(e, Number)
                    if values is not None:
                        return self._make_constant(sum(values), node)
                case (
                    "sum",
                    [ast.List(elts=e) | ast.Tuple(elts=e), ast.Constant(value=start)],
                ):
                    values = self._const_list(e, Number)
                    if values is not None:
                        return self._make_constant(sum(values, start), node)

                # bool() on collections
                case ("bool", [ast.List(elts=e) | ast.Tuple(elts=e)]):
                    return self._make_constant(len(e) > 0, node)

                # round() with optional ndigits
                case ("round", [ast.Constant(value=v)]) if isinstance(v, Number):
                    return self._make_constant(round(v), node)
                case (
                    "round",
                    [ast.Constant(value=v), ast.Constant(value=n)],
                ) if isinstance(v, Number) and isinstance(n, int):
                    return self._make_constant(round(v, n), node)

                # int() with base
                case (
                    "int",
                    [ast.Constant(value=s), ast.Constant(value=base)],
                ) if isinstance(s, str) and isinstance(base, int):
                    return self._make_constant(int(s, base), node)

        except (ValueError, TypeError, OverflowError):
            pass

        return node

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _try_simple_function(self, name: str, value: Any) -> Any | None:
        """Try to apply a simple function rule from the table."""
        for func_name, types, compute, guard in SIMPLE_FUNCTIONS:
            if name == func_name and isinstance(value, types):
                if guard is None or guard(value):
                    try:
                        return compute(value)
                    except (ValueError, TypeError, OverflowError):
                        pass
        return None

    def _compute_binary(
        self, op_func: Callable, left: Any, right: Any, node: ast.BinOp
    ) -> ast.expr:
        """Compute a binary operation, raising compile-time errors."""
        try:
            return self._make_constant(op_func(left, right), node)
        except ZeroDivisionError:
            line = getattr(node, "lineno", "?")
            raise JSError(f"Division by zero at line {line}: {left} / {right}")
        except OverflowError:
            line = getattr(node, "lineno", "?")
            op_name = type(node.op).__name__
            raise JSError(f"Numeric overflow at line {line}: {left} {op_name} {right}")
        except ValueError as e:
            line = getattr(node, "lineno", "?")
            raise JSError(f"Invalid operation at line {line}: {e}")

    def _extract_numbers(self, args: list[ast.expr]) -> list | None:
        """Extract numeric values from args. Handles variadic and single-list."""
        values = []
        for arg in args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, Number):
                values.append(arg.value)
            elif isinstance(arg, (ast.List, ast.Tuple)):
                inner = self._const_list(arg.elts, Number)
                if inner is None:
                    return None
                # Single list arg: return its contents
                if len(args) == 1:
                    return inner
                values.append(inner)
            else:
                return None
        return values if values else None

    def _const_list(self, elts: list[ast.expr], types: type | tuple) -> list | None:
        """Extract constant values from a list of elements matching types."""
        values = []
        for el in elts:
            if isinstance(el, ast.Constant) and isinstance(el.value, types):
                values.append(el.value)
            else:
                return None
        return values

    def _make_constant(self, value: Any, original: ast.AST) -> ast.Constant:
        """Create a Constant node preserving source location."""
        return _ast.copy_location(ast.Constant(value=value), original)
