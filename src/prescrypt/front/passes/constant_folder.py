"""Constant folding optimization pass.

Evaluates constant expressions at compile time to reduce code size
and improve performance of generated JavaScript.

Architecture:
- Unified value extraction from AST nodes
- Declarative rule tables for all folding operations
- Structure-based rules (AST) vs value-based rules (Python values)
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
Seq = (list, tuple)

# Sentinel for non-extractable values
_NOT_EXTRACTABLE = object()


# =============================================================================
# Value Extraction
# =============================================================================


def _extract(node: ast.expr) -> Any:
    """Extract Python value from AST node, or _NOT_EXTRACTABLE if not possible."""
    match node:
        case ast.Constant(value=val):
            return val
        case ast.List(elts=elts) | ast.Tuple(elts=elts):
            values = [_extract(elem) for elem in elts]
            return values if _NOT_EXTRACTABLE not in values else _NOT_EXTRACTABLE
        case ast.Dict(keys=keys, values=vals):
            extracted_keys = [_extract(key) for key in keys]
            extracted_vals = [_extract(val) for val in vals]
            if _NOT_EXTRACTABLE in extracted_keys or _NOT_EXTRACTABLE in extracted_vals:
                return _NOT_EXTRACTABLE
            return dict(zip(extracted_keys, extracted_vals))
        case _:
            return _NOT_EXTRACTABLE


# =============================================================================
# Rule Tables
# =============================================================================

# Binary operations: op_type -> operator function
BINARY_OPS: dict[type, Callable] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

# Comparison operations: op_type -> operator function
COMPARE_OPS: dict[type, Callable] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}

# Function rules: (name, arity, validator, computer)
# - arity: exact count, or -1 for variadic (1+ args)
# - validator: fn(values) -> bool (values is list of extracted Python values)
# - computer: fn(values) -> result
FUNC_RULES: list[tuple[str, int, Callable[[list], bool], Callable[[list], Any]]] = [
    # Length
    (
        "len",
        1,
        lambda args: isinstance(args[0], (str, bytes, list, tuple, dict)),
        lambda args: len(args[0]),
    ),
    # Math
    ("abs", 1, lambda args: isinstance(args[0], Number), lambda args: abs(args[0])),
    ("round", 1, lambda args: isinstance(args[0], Number), lambda args: round(args[0])),
    (
        "round",
        2,
        lambda args: isinstance(args[0], Number) and isinstance(args[1], int),
        lambda args: round(*args),
    ),
    # Aggregations - variadic
    ("min", -1, lambda args: all(isinstance(item, Number) for item in args), min),
    ("max", -1, lambda args: all(isinstance(item, Number) for item in args), max),
    # Aggregations - single sequence
    (
        "min",
        1,
        lambda args: isinstance(args[0], Seq)
        and args[0]
        and all(isinstance(item, Number) for item in args[0]),
        lambda args: min(args[0]),
    ),
    (
        "max",
        1,
        lambda args: isinstance(args[0], Seq)
        and args[0]
        and all(isinstance(item, Number) for item in args[0]),
        lambda args: max(args[0]),
    ),
    (
        "sum",
        1,
        lambda args: isinstance(args[0], Seq)
        and all(isinstance(item, Number) for item in args[0]),
        lambda args: sum(args[0]),
    ),
    (
        "sum",
        2,
        lambda args: isinstance(args[0], Seq)
        and all(isinstance(item, Number) for item in args[0])
        and isinstance(args[1], Number),
        lambda args: sum(args[0], args[1]),
    ),
    # Type conversions
    ("bool", 1, lambda _: True, lambda args: bool(args[0])),
    (
        "int",
        1,
        lambda args: isinstance(args[0], (int, float, str)),
        lambda args: int(args[0]),
    ),
    (
        "int",
        2,
        lambda args: isinstance(args[0], str) and isinstance(args[1], int),
        lambda args: int(args[0], args[1]),
    ),
    (
        "float",
        1,
        lambda args: isinstance(args[0], (int, float, str)),
        lambda args: float(args[0]),
    ),
    (
        "str",
        1,
        lambda args: isinstance(args[0], (int, float, str))
        and not isinstance(args[0], bool),
        lambda args: str(args[0]),
    ),
    # Character conversions
    (
        "chr",
        1,
        lambda args: isinstance(args[0], int) and 0 <= args[0] <= 0x10FFFF,
        lambda args: chr(args[0]),
    ),
    (
        "ord",
        1,
        lambda args: isinstance(args[0], str) and len(args[0]) == 1,
        lambda args: ord(args[0]),
    ),
]

# Index FUNC_RULES by name for faster lookup
_FUNC_INDEX: dict[str, list[tuple[int, Callable, Callable]]] = {}
for _rule_name, _rule_arity, _rule_validator, _rule_computer in FUNC_RULES:
    _FUNC_INDEX.setdefault(_rule_name, []).append(
        (_rule_arity, _rule_validator, _rule_computer)
    )


# =============================================================================
# Public API
# =============================================================================


def fold_constants(tree: ast.Module) -> ast.Module:
    """Apply constant folding to an AST tree."""
    return _ast.fix_missing_locations(ConstantFolder().visit(tree))


# =============================================================================
# Constant Folder
# =============================================================================


class ConstantFolder(ast.NodeTransformer):
    """Fold constant expressions at compile time."""

    def visit_BinOp(self, node: ast.BinOp) -> ast.expr:
        node = self.generic_visit(node)

        if not isinstance(node.left, ast.Constant) or not isinstance(
            node.right, ast.Constant
        ):
            return node

        left, right = node.left.value, node.right.value
        op_type = type(node.op)

        # Numeric operations
        if (
            op_type in BINARY_OPS
            and isinstance(left, Number)
            and isinstance(right, Number)
        ):
            return self._compute_binary(BINARY_OPS[op_type], left, right, node)

        # String operations
        if op_type is ast.Add and isinstance(left, str) and isinstance(right, str):
            return self._make_constant(left + right, node)
        if op_type is ast.Mult:
            if isinstance(left, str) and isinstance(right, int) and right >= 0:
                return self._make_constant(left * right, node)
            if isinstance(left, int) and isinstance(right, str) and left >= 0:
                return self._make_constant(left * right, node)

        return node

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.expr:
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
        node = self.generic_visit(node)

        if len(node.values) != 2:
            return node

        left, right = node.values
        is_and = isinstance(node.op, ast.And)

        # Both constants
        if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
            result = left.value and right.value if is_and else left.value or right.value
            return self._make_constant(result, node)

        # Partial evaluation
        if isinstance(left, ast.Constant):
            if is_and:
                return left if not left.value else right
            return left if left.value else right

        return node

    def visit_Compare(self, node: ast.Compare) -> ast.expr:
        node = self.generic_visit(node)

        if len(node.ops) != 1 or len(node.comparators) != 1:
            return node
        if not isinstance(node.left, ast.Constant) or not isinstance(
            node.comparators[0], ast.Constant
        ):
            return node

        left, right = node.left.value, node.comparators[0].value
        op = node.ops[0]

        # Standard comparisons
        if type(op) in COMPARE_OPS:
            try:
                return self._make_constant(COMPARE_OPS[type(op)](left, right), node)
            except TypeError:
                return node

        # Special comparisons
        if isinstance(op, ast.In) and isinstance(left, str) and isinstance(right, str):
            return self._make_constant(left in right, node)
        if (
            isinstance(op, ast.NotIn)
            and isinstance(left, str)
            and isinstance(right, str)
        ):
            return self._make_constant(left not in right, node)
        if isinstance(op, ast.Is) and (left is None or right is None):
            return self._make_constant(left is right, node)
        if isinstance(op, ast.IsNot) and (left is None or right is None):
            return self._make_constant(left is not right, node)

        return node

    def visit_IfExp(self, node: ast.IfExp) -> ast.expr:
        node = self.generic_visit(node)
        if isinstance(node.test, ast.Constant):
            return node.body if node.test.value else node.orelse
        return node

    def visit_Subscript(self, node: ast.Subscript) -> ast.expr:
        node = self.generic_visit(node)

        if not isinstance(node.slice, ast.Constant) or not isinstance(
            node.slice.value, int
        ):
            return node

        index = node.slice.value
        match node.value:
            case ast.Constant(value=val):
                seq = val
            case ast.List(elts=elts) | ast.Tuple(elts=elts) if all(
                isinstance(elem, ast.Constant) for elem in elts
            ):
                seq = [elem.value for elem in elts]
            case _:
                return node

        try:
            return self._make_constant(seq[index], node)
        except (IndexError, TypeError):
            return node

    def visit_Call(self, node: ast.Call) -> ast.expr:
        node = self.generic_visit(node)

        if not isinstance(node.func, ast.Name) or node.keywords:
            return node

        func_name, func_args = node.func.id, node.args

        # Structure-based rules (don't need value extraction)
        match (func_name, func_args):
            case (
                "len",
                [ast.List(elts=elts) | ast.Tuple(elts=elts) | ast.Set(elts=elts)],
            ):
                return self._make_constant(len(elts), node)
            case ("len", [ast.Dict(keys=keys)]):
                return self._make_constant(len(keys), node)
            case ("bool", [ast.List(elts=elts) | ast.Tuple(elts=elts)]):
                return self._make_constant(len(elts) > 0, node)

        # Value-based rules (need value extraction)
        if func_name not in _FUNC_INDEX:
            return node

        extracted_values = [_extract(arg) for arg in func_args]
        if _NOT_EXTRACTABLE in extracted_values:
            return node

        for arity, validator, computer in _FUNC_INDEX[func_name]:
            if (arity == -1 and len(extracted_values) >= 1) or arity == len(
                extracted_values
            ):
                if validator(extracted_values):
                    try:
                        return self._make_constant(computer(extracted_values), node)
                    except (ValueError, TypeError, OverflowError):
                        pass

        return node

    # =========================================================================
    # Helpers
    # =========================================================================

    def _make_constant(self, value: Any, node: ast.AST) -> ast.Constant:
        """Create constant node preserving source location."""
        return _ast.copy_location(ast.Constant(value=value), node)

    def _compute_binary(
        self, op_func: Callable, left: Any, right: Any, node: ast.BinOp
    ) -> ast.expr:
        """Compute binary op, raising compile-time errors for invalid operations."""
        try:
            return self._make_constant(op_func(left, right), node)
        except ZeroDivisionError:
            raise JSError(
                f"Division by zero at line {getattr(node, 'lineno', '?')}: {left} / {right}"
            )
        except OverflowError:
            raise JSError(
                f"Numeric overflow at line {getattr(node, 'lineno', '?')}: {left} {type(node.op).__name__} {right}"
            )
        except ValueError as err:
            raise JSError(
                f"Invalid operation at line {getattr(node, 'lineno', '?')}: {err}"
            )
