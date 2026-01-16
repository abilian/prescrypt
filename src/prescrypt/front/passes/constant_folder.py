"""Constant folding optimization pass.

Evaluates constant expressions at compile time to reduce code size
and improve performance of generated JavaScript.

Architecture:
- Unified value extraction from AST nodes
- Pattern matching for type-safe rule application
- Structure-based rules (AST) vs value-based rules (Python values)
"""

from __future__ import annotations

import ast as _ast
import operator
from collections.abc import Callable
from typing import Any

from prescrypt.exceptions import JSError
from prescrypt.front import ast

# =============================================================================
# Type Aliases
# =============================================================================

Number = (int, float)

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


def _all_numbers(seq: list | tuple) -> bool:
    """Check if all elements in a sequence are numbers."""
    return all(isinstance(item, Number) for item in seq)


# =============================================================================
# Rule Tables (for simple operator mappings)
# =============================================================================

BINARY_OPS: dict[type, Callable] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

COMPARE_OPS: dict[type, Callable] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}


# =============================================================================
# Function Folding (pattern matching based)
# =============================================================================


def _fold_function(name: str, values: list) -> Any:
    """Apply function folding rules using pattern matching.

    Returns the computed result, or _NOT_EXTRACTABLE if no rule matches.
    Type checks are implicit in pattern syntax (e.g., int() | float()).
    """
    match (name, values):
        # len
        case ("len", [str() | bytes() | list() | tuple() | dict() as val]):
            return len(val)

        # abs
        case ("abs", [int() | float() as val]):
            return abs(val)

        # round
        case ("round", [int() | float() as val]):
            return round(val)
        case ("round", [int() | float() as val, int() as ndigits]):
            return round(val, ndigits)

        # min - variadic numbers
        case ("min", [int() | float(), *rest]) if _all_numbers(rest):
            return min(values)
        # min - single sequence of numbers
        case ("min", [list() | tuple() as seq]) if seq and _all_numbers(seq):
            return min(seq)

        # max - variadic numbers
        case ("max", [int() | float(), *rest]) if _all_numbers(rest):
            return max(values)
        # max - single sequence of numbers
        case ("max", [list() | tuple() as seq]) if seq and _all_numbers(seq):
            return max(seq)

        # sum
        case ("sum", [list() | tuple() as seq]) if _all_numbers(seq):
            return sum(seq)
        case ("sum", [list() | tuple() as seq, int() | float() as start]) if (
            _all_numbers(seq)
        ):
            return sum(seq, start)

        # bool - accepts anything
        case ("bool", [val]):
            return bool(val)

        # int
        case ("int", [int() | float() | str() as val]):
            return int(val)
        case ("int", [str() as val, int() as base]):
            return int(val, base)

        # float
        case ("float", [int() | float() | str() as val]):
            return float(val)

        # str - but not bool (JS uses "true"/"false", Python uses "True"/"False")
        case ("str", [bool()]):
            return _NOT_EXTRACTABLE
        case ("str", [int() | float() | str() as val]):
            return str(val)

        # chr
        case ("chr", [int() as val]) if 0 <= val <= 0x10FFFF:
            return chr(val)

        # ord
        case ("ord", [str() as val]) if len(val) == 1:
            return ord(val)

        case _:
            return _NOT_EXTRACTABLE


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

        match (node.left, node.right):
            case (ast.Constant(value=left), ast.Constant(value=right)):
                return self._fold_binary(left, right, node)
        return node

    def _fold_binary(self, left: Any, right: Any, node: ast.BinOp) -> ast.expr:
        """Fold binary operation on constant values."""
        op_type = type(node.op)

        # Numeric operations (table-driven)
        match (left, right):
            case (int() | float(), int() | float()) if op_type in BINARY_OPS:
                return self._compute_binary(BINARY_OPS[op_type], left, right, node)

        # String operations (pattern-based)
        match (op_type, left, right):
            case (ast.Add, str(), str()):
                return self._make_constant(left + right, node)
            case (ast.Mult, str(), int()) if right >= 0:
                return self._make_constant(left * right, node)
            case (ast.Mult, int(), str()) if left >= 0:
                return self._make_constant(left * right, node)

        return node

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.expr:
        node = self.generic_visit(node)

        match (node.op, node.operand):
            case (ast.Not(), ast.Constant(value=val)):
                return self._make_constant(not val, node)
            case (ast.Invert(), ast.Constant(value=int() as val)):
                return self._make_constant(~val, node)
        return node

    def visit_BoolOp(self, node: ast.BoolOp) -> ast.expr:
        node = self.generic_visit(node)

        if len(node.values) != 2:
            return node

        left, right = node.values
        is_and = isinstance(node.op, ast.And)

        match (left, right):
            # Both constants
            case (ast.Constant(value=left_val), ast.Constant(value=right_val)):
                result = left_val and right_val if is_and else left_val or right_val
                return self._make_constant(result, node)
            # Partial evaluation: left is constant
            case (ast.Constant(value=left_val), _):
                if is_and:
                    return left if not left_val else right
                return left if left_val else right

        return node

    def visit_Compare(self, node: ast.Compare) -> ast.expr:
        node = self.generic_visit(node)

        if len(node.ops) != 1 or len(node.comparators) != 1:
            return node

        match (node.left, node.comparators[0]):
            case (ast.Constant(value=left), ast.Constant(value=right)):
                return self._fold_compare(left, right, node.ops[0], node)
        return node

    def _fold_compare(
        self, left: Any, right: Any, op: ast.cmpop, node: ast.Compare
    ) -> ast.expr:
        """Fold comparison operation on constant values."""
        # Standard comparisons (table-driven)
        if type(op) in COMPARE_OPS:
            try:
                return self._make_constant(COMPARE_OPS[type(op)](left, right), node)
            except TypeError:
                return node

        # Special comparisons (pattern-based)
        match (op, left, right):
            case (ast.In(), str(), str()):
                return self._make_constant(left in right, node)
            case (ast.NotIn(), str(), str()):
                return self._make_constant(left not in right, node)
            case (ast.Is(), _, _) if left is None or right is None:
                return self._make_constant(left is right, node)
            case (ast.IsNot(), _, _) if left is None or right is None:
                return self._make_constant(left is not right, node)

        return node

    def visit_IfExp(self, node: ast.IfExp) -> ast.expr:
        node = self.generic_visit(node)
        match node.test:
            case ast.Constant(value=val):
                return node.body if val else node.orelse
        return node

    def visit_Subscript(self, node: ast.Subscript) -> ast.expr:
        node = self.generic_visit(node)

        match (node.value, node.slice):
            case (ast.Constant(value=seq), ast.Constant(value=int() as index)):
                try:
                    return self._make_constant(seq[index], node)
                except (IndexError, TypeError):
                    pass
            case (
                ast.List(elts=elts) | ast.Tuple(elts=elts),
                ast.Constant(value=int() as index),
            ) if all(isinstance(elem, ast.Constant) for elem in elts):
                try:
                    return self._make_constant(elts[index].value, node)
                except IndexError:
                    pass
        return node

    def visit_Call(self, node: ast.Call) -> ast.expr:
        node = self.generic_visit(node)

        match node.func:
            case ast.Name(id=func_name) if not node.keywords:
                return self._fold_call(func_name, node.args, node)
        return node

    def _fold_call(
        self, func_name: str, func_args: list[ast.expr], node: ast.Call
    ) -> ast.expr:
        """Fold function call on constant arguments."""
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
        extracted = [_extract(arg) for arg in func_args]
        if _NOT_EXTRACTABLE in extracted:
            return node

        try:
            result = _fold_function(func_name, extracted)
            if result is not _NOT_EXTRACTABLE:
                return self._make_constant(result, node)
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
            msg = f"Division by zero at line {getattr(node, 'lineno', '?')}: {left} / {right}"
            raise JSError(msg)
        except OverflowError:
            msg = f"Numeric overflow at line {getattr(node, 'lineno', '?')}: {left} {type(node.op).__name__} {right}"
            raise JSError(msg)
        except ValueError as err:
            msg = f"Invalid operation at line {getattr(node, 'lineno', '?')}: {err}"
            raise JSError(msg)
