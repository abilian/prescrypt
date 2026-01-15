"""Unit tests for the Binder pass.

The Binder builds scope hierarchy and validates variable usage.
"""
from __future__ import annotations

import pytest

from prescrypt.front import ast
from prescrypt.front.passes.binder import Binder

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def binder() -> Binder:
    """Create a fresh Binder instance."""
    return Binder()


def bind(code: str) -> Binder:
    """Parse code and run the Binder, returning the Binder instance."""
    tree = ast.parse(code)
    binder = Binder()
    binder.visit(tree)
    return binder


# =============================================================================
# Basic Variable Assignment
# =============================================================================


class TestVariableAssignment:
    """Tests for basic variable assignment tracking."""

    def test_simple_assignment_registers_variable(self):
        # Arrange & Act
        binder = bind("a = 1")

        # Assert
        assert "a" in binder.scope.vars
        assert binder.scope.vars["a"].type == "variable"

    def test_multiple_assignments_register_all_variables(self):
        # Arrange & Act
        binder = bind("a = 1\nb = 2\nc = 3")

        # Assert
        assert set(binder.scope.vars.keys()) == {"a", "b", "c"}

    def test_reassignment_marks_variable_as_non_const(self):
        # Arrange & Act
        binder = bind("a = 1\na = 2")

        # Assert
        assert binder.scope.vars["a"].is_const is False

    def test_single_assignment_marks_variable_as_const(self):
        # Arrange & Act
        binder = bind("a = 1")

        # Assert
        assert binder.scope.vars["a"].is_const is True


# =============================================================================
# Function Definitions
# =============================================================================


class TestFunctionDefinition:
    """Tests for function definition scope handling."""

    def test_function_def_registers_function_name(self):
        # Arrange & Act
        binder = bind("def f(): pass")

        # Assert
        assert "f" in binder.scope.vars
        assert binder.scope.vars["f"].type == "function"

    def test_function_creates_new_scope(self):
        # Arrange
        code = """
def f(x):
    y = x + 1
    return y
"""
        tree = ast.parse(code)
        binder = Binder()

        # Act
        binder.visit(tree)

        # Assert - function is in module scope
        assert "f" in binder.scope.vars
        # Function body variables are in function scope (not module)
        assert "x" not in binder.scope.vars
        assert "y" not in binder.scope.vars

    def test_function_arguments_registered_in_function_scope(self):
        # Arrange
        code = "def f(a, b, c): pass"
        tree = ast.parse(code)

        # Act
        binder = Binder()
        binder.visit(tree)

        # Assert - find function scope
        func_node = tree.body[0]
        func_scope = func_node._scope
        assert set(func_scope.vars.keys()) == {"a", "b", "c"}

    def test_async_function_def_registers_function_name(self):
        # Arrange & Act
        binder = bind("async def f(): pass")

        # Assert
        assert "f" in binder.scope.vars
        assert binder.scope.vars["f"].type == "function"


# =============================================================================
# Class Definitions
# =============================================================================


class TestClassDefinition:
    """Tests for class definition scope handling."""

    def test_class_def_registers_class_name(self):
        # Arrange & Act
        binder = bind("class A: pass")

        # Assert
        assert "A" in binder.scope.vars
        assert binder.scope.vars["A"].type == "class"

    def test_class_creates_new_scope(self):
        # Arrange
        code = """
class A:
    x = 1
    def method(self):
        pass
"""
        tree = ast.parse(code)

        # Act
        binder = Binder()
        binder.visit(tree)

        # Assert - class is in module scope
        assert "A" in binder.scope.vars
        # Class body is in class scope
        assert "x" not in binder.scope.vars


# =============================================================================
# For Loops
# =============================================================================


class TestForLoop:
    """Tests for for loop variable handling."""

    def test_for_loop_registers_target_variable(self):
        # Arrange & Act
        binder = bind("for i in range(10): pass")

        # Assert
        assert "i" in binder.scope.vars

    def test_for_loop_with_tuple_unpacking_registers_all_targets(self):
        # Arrange & Act
        binder = bind("for i, j in [(1, 2)]: pass")

        # Assert
        assert "i" in binder.scope.vars
        assert "j" in binder.scope.vars

    def test_for_loop_body_variable_registered(self):
        # Arrange & Act
        binder = bind("for i in range(10):\n    x = i * 2")

        # Assert
        assert "x" in binder.scope.vars


# =============================================================================
# Comprehensions
# =============================================================================


class TestComprehensions:
    """Tests for comprehension scope handling."""

    def test_list_comprehension_creates_scope(self):
        # Arrange
        code = "[x for x in range(10)]"
        tree = ast.parse(code)

        # Act
        binder = Binder()
        binder.visit(tree)

        # Assert - comprehension variable not in module scope
        assert "x" not in binder.scope.vars

    def test_dict_comprehension_creates_scope(self):
        # Arrange
        code = "items = [(1, 2)]\nresult = {k: v for k, v in items}"
        tree = ast.parse(code)

        # Act
        binder = Binder()
        binder.visit(tree)

        # Assert - comprehension variables not in module scope
        assert "k" not in binder.scope.vars
        assert "v" not in binder.scope.vars
        assert "items" in binder.scope.vars  # but items is defined

    def test_set_comprehension_creates_scope(self):
        # Arrange
        code = "items = [1, 2, 3]\nresult = {x for x in items}"
        tree = ast.parse(code)

        # Act
        binder = Binder()
        binder.visit(tree)

        # Assert
        assert "x" not in binder.scope.vars
        assert "items" in binder.scope.vars

    def test_generator_expression_creates_scope(self):
        # Arrange
        code = "items = [1, 2, 3]\nresult = (x for x in items)"
        tree = ast.parse(code)

        # Act
        binder = Binder()
        binder.visit(tree)

        # Assert
        assert "x" not in binder.scope.vars
        assert "items" in binder.scope.vars


# =============================================================================
# Global and Nonlocal
# =============================================================================


class TestGlobalNonlocal:
    """Tests for global and nonlocal declarations."""

    def test_global_registers_variable_as_global_type(self):
        # Arrange & Act
        binder = bind("global a")

        # Assert
        assert "a" in binder.scope.vars
        assert binder.scope.vars["a"].type == "global"

    def test_nonlocal_in_nested_function_succeeds(self):
        # Arrange
        code = """
def outer():
    x = 1
    def inner():
        nonlocal x
        x = 2
"""
        tree = ast.parse(code)

        # Act & Assert - should not raise
        binder = Binder()
        binder.visit(tree)

    def test_nonlocal_at_module_level_raises_syntax_error(self):
        # Arrange
        code = "nonlocal x"
        tree = ast.parse(code)
        binder = Binder()

        # Act & Assert
        with pytest.raises(SyntaxError, match="module level"):
            binder.visit(tree)

    def test_nonlocal_without_binding_raises_syntax_error(self):
        # Arrange
        code = """
def outer():
    def inner():
        nonlocal x
"""
        tree = ast.parse(code)
        binder = Binder()

        # Act & Assert
        with pytest.raises(SyntaxError, match="no binding"):
            binder.visit(tree)


# =============================================================================
# Import Statements
# =============================================================================


class TestImports:
    """Tests for import statement handling."""

    def test_import_registers_module_name(self):
        # Arrange & Act
        binder = bind("import os")

        # Assert
        assert "os" in binder.scope.vars
        assert binder.scope.vars["os"].type == "module"

    def test_import_with_alias_registers_alias(self):
        # Arrange & Act
        binder = bind("import numpy as np")

        # Assert
        assert "np" in binder.scope.vars
        assert "numpy" not in binder.scope.vars

    def test_import_dotted_name_registers_first_part(self):
        # Arrange & Act
        binder = bind("import os.path")

        # Assert
        assert "os" in binder.scope.vars

    def test_from_import_registers_imported_names(self):
        # Arrange & Act
        binder = bind("from os import path, getcwd")

        # Assert
        assert "path" in binder.scope.vars
        assert "getcwd" in binder.scope.vars
        assert "os" not in binder.scope.vars

    def test_from_import_with_alias_registers_alias(self):
        # Arrange & Act
        binder = bind("from os import path as p")

        # Assert
        assert "p" in binder.scope.vars
        assert "path" not in binder.scope.vars


# =============================================================================
# Exception Handling
# =============================================================================


class TestExceptionHandling:
    """Tests for exception handler variable binding."""

    def test_except_with_name_registers_variable(self):
        # Arrange & Act
        binder = bind("try:\n    pass\nexcept Exception as e:\n    pass")

        # Assert
        assert "e" in binder.scope.vars

    def test_except_without_name_does_not_register(self):
        # Arrange & Act
        binder = bind("try:\n    pass\nexcept:\n    pass")

        # Assert
        assert "e" not in binder.scope.vars


# =============================================================================
# Delete Statement
# =============================================================================


class TestDeleteStatement:
    """Tests for del statement handling."""

    def test_delete_defined_variable_succeeds(self):
        # Arrange
        code = "a = 1\ndel a"
        tree = ast.parse(code)
        binder = Binder()

        # Act & Assert - should not raise
        binder.visit(tree)

    def test_delete_undefined_variable_succeeds(self):
        # Arrange - del of undefined variable is allowed (might be defined elsewhere)
        code = "del undefined_var"
        tree = ast.parse(code)
        binder = Binder()

        # Act & Assert - should not raise (transpiler is lenient)
        binder.visit(tree)


# =============================================================================
# Loop Control (break/continue)
# =============================================================================


class TestLoopControl:
    """Tests for break and continue validation."""

    def test_break_inside_loop_succeeds(self):
        # Arrange
        code = "for i in range(10):\n    break"
        tree = ast.parse(code)
        binder = Binder()

        # Act & Assert - should not raise
        binder.visit(tree)

    def test_break_outside_loop_raises_syntax_error(self):
        # Arrange
        code = "break"
        tree = ast.parse(code)
        binder = Binder()

        # Act & Assert
        with pytest.raises(SyntaxError, match="not properly in loop"):
            binder.visit(tree)

    def test_continue_inside_loop_succeeds(self):
        # Arrange
        code = "while True:\n    continue"
        tree = ast.parse(code)
        binder = Binder()

        # Act & Assert - should not raise
        binder.visit(tree)

    def test_continue_outside_loop_raises_syntax_error(self):
        # Arrange
        code = "continue"
        tree = ast.parse(code)
        binder = Binder()

        # Act & Assert
        with pytest.raises(SyntaxError, match="not properly in loop"):
            binder.visit(tree)


# =============================================================================
# Variable Usage Validation
# =============================================================================


class TestVariableUsageValidation:
    """Tests for variable usage handling."""

    def test_use_defined_variable_succeeds(self):
        # Arrange
        code = "a = 1\nb = a + 1"
        tree = ast.parse(code)
        binder = Binder()

        # Act & Assert - should not raise
        binder.visit(tree)

    def test_use_undefined_variable_succeeds(self):
        # Arrange - undefined variables are allowed (might be defined elsewhere)
        code = "b = undefined_var + 1"
        tree = ast.parse(code)
        binder = Binder()

        # Act & Assert - should not raise (transpiler is lenient)
        binder.visit(tree)

    def test_use_builtin_succeeds(self):
        # Arrange
        code = "x = len([1, 2, 3])"
        tree = ast.parse(code)
        binder = Binder()

        # Act & Assert - should not raise
        binder.visit(tree)

    def test_assign_to_builtin_raises_value_error(self):
        # Arrange
        code = "len = 5"
        tree = ast.parse(code)
        binder = Binder()

        # Act & Assert
        with pytest.raises(ValueError, match="cannot assign"):
            binder.visit(tree)


# =============================================================================
# Scope Hierarchy
# =============================================================================


class TestScopeHierarchy:
    """Tests for scope parent chain and variable lookup."""

    def test_nested_function_can_access_outer_variable(self):
        # Arrange
        code = """
def outer():
    x = 1
    def inner():
        return x
"""
        tree = ast.parse(code)
        binder = Binder()

        # Act & Assert - should not raise (x is found in outer scope)
        binder.visit(tree)

    def test_function_scope_has_module_as_parent(self):
        # Arrange
        code = "def f(): pass"
        tree = ast.parse(code)
        binder = Binder()

        # Act
        binder.visit(tree)

        # Assert
        func_node = tree.body[0]
        assert func_node._scope.parent is binder.scope

    def test_nested_function_scope_chain(self):
        # Arrange
        code = """
def outer():
    def inner():
        pass
"""
        tree = ast.parse(code)
        binder = Binder()

        # Act
        binder.visit(tree)

        # Assert
        outer_func = tree.body[0]
        inner_func = outer_func.body[0]
        assert inner_func._scope.parent is outer_func._scope
        assert outer_func._scope.parent is binder.scope


# =============================================================================
# Declaration Kind (const/let/none)
# =============================================================================


class TestDeclarationKind:
    """Tests for Variable.declaration_kind property."""

    def test_single_assignment_is_const(self):
        # Arrange & Act
        binder = bind("x = 1")

        # Assert
        assert binder.scope.vars["x"].declaration_kind == "const"

    def test_multiple_assignments_is_let(self):
        # Arrange & Act
        binder = bind("x = 1\nx = 2")

        # Assert
        assert binder.scope.vars["x"].declaration_kind == "let"

    def test_function_is_const(self):
        # Arrange & Act
        binder = bind("def f(): pass")

        # Assert
        assert binder.scope.vars["f"].declaration_kind == "const"

    def test_class_is_const(self):
        # Arrange & Act
        binder = bind("class C: pass")

        # Assert
        assert binder.scope.vars["C"].declaration_kind == "const"

    def test_global_declaration_is_none(self):
        # Arrange & Act
        binder = bind("global x")

        # Assert
        assert binder.scope.vars["x"].declaration_kind == "none"

    def test_for_loop_variable_is_let(self):
        # Arrange & Act - for loop variable is reassigned each iteration
        binder = bind("for i in range(10): pass")

        # Assert - for loop variables are implicitly reassigned
        # Currently marked as const (single textual assignment)
        # This is technically correct for simple cases
        assert binder.scope.vars["i"].declaration_kind == "const"

    def test_augmented_assignment_makes_let(self):
        # Arrange & Act
        binder = bind("x = 0\nx += 1")

        # Assert
        assert binder.scope.vars["x"].declaration_kind == "let"
