"""Regression tests for bugs fixed in Stage 2.

These tests document specific bugs that were found and fixed,
to prevent them from recurring.
"""
from __future__ import annotations

import pytest

from prescrypt import py2js

from .utils import check_gen_exec


class TestForElseBreakDetection:
    """Regression tests for for-else break detection bug.

    Bug: The for-else handling searched for exact string match `part == "break;"`
    but the break statement was returned as `"break;\n"` or could be embedded
    in a larger code string, causing the else clause to always execute.

    Fix: Changed to `if "break;" in part` and use string replacement.

    Commit: Stage 2 (2025-01-10)
    """

    def test_for_else_break_sets_flag(self):
        """Break should set the else flag to false, preventing else execution."""
        code = """
result = 'initial'
for i in range(5):
    if i == 2:
        result = 'found'
        break
else:
    result = 'not found'
result
"""
        # If the bug is present, result would be 'not found' (else always runs)
        check_gen_exec(code, "found")

    def test_for_else_break_in_nested_if(self):
        """Break inside nested if should still set the else flag."""
        code = """
result = 'initial'
for i in range(10):
    if i > 5:
        if i == 7:
            result = 'found 7'
            break
else:
    result = 'completed'
result
"""
        check_gen_exec(code, "found 7")

    def test_for_else_multiple_breaks(self):
        """Multiple break statements should all be properly handled."""
        code = """
result = 'initial'
for i in range(10):
    if i == 3:
        result = 'early'
        break
    if i == 7:
        result = 'late'
        break
else:
    result = 'completed'
result
"""
        # Should hit the first break at i=3
        check_gen_exec(code, "early")

    def test_for_else_no_break_runs_else(self):
        """Without break, the else clause should run."""
        code = """
result = 'initial'
for i in range(3):
    result = 'in loop'
else:
    result = 'completed'
result
"""
        check_gen_exec(code, "completed")

    def test_while_else_break_sets_flag(self):
        """While-else should also properly handle break (same bug pattern)."""
        code = """
result = 'initial'
i = 0
while i < 10:
    if i == 5:
        result = 'found'
        break
    i = i + 1
else:
    result = 'completed'
result
"""
        check_gen_exec(code, "found")


class TestIfElifStringSlicing:
    """Regression tests for if-elif string slicing bug.

    Bug: The elif handling assumed gen_stmt returned a list and used [1:-1]
    slicing to skip the first and last elements. But gen_stmt returns a
    flattened string, so [1:-1] was character slicing, resulting in
    malformed JS like `} else if (if ((x < 7)) {`.

    Fix: Parse the returned string to properly extract the condition and body,
    removing the leading "if (" and trailing "}".

    Commit: Stage 2 (2025-01-10)
    """

    def test_elif_generates_valid_js(self):
        """elif should generate valid JavaScript without doubled 'if'."""
        code = """
x = 5
result = ''
if x < 3:
    result = 'small'
elif x < 7:
    result = 'medium'
else:
    result = 'big'
result
"""
        js = py2js(code)
        # Should NOT contain 'else if (if' - that's the bug pattern
        assert "else if (if" not in js
        # Should contain proper 'else if (' pattern
        assert "else if (" in js
        check_gen_exec(code, "medium")

    def test_multiple_elif_chain(self):
        """Multiple elif clauses should all generate valid JS."""
        code = """
x = 50
result = ''
if x < 10:
    result = 'tiny'
elif x < 25:
    result = 'small'
elif x < 75:
    result = 'medium'
elif x < 100:
    result = 'large'
else:
    result = 'huge'
result
"""
        js = py2js(code)
        # Extract just the user code portion (after the stdlib)
        user_code = js[js.find("const x = 50;"):]
        # Count the elif clauses - should have 3 'else if' patterns
        assert user_code.count("else if (") == 3
        # No malformed patterns
        assert "else if (if" not in js
        check_gen_exec(code, "medium")

    def test_elif_with_complex_condition(self):
        """elif with complex conditions should work correctly."""
        code = """
x = 5
y = 10
result = ''
if x > 10 and y > 10:
    result = 'both big'
elif x < 10 or y < 5:
    result = 'at least one small'
else:
    result = 'neither'
result
"""
        js = py2js(code)
        assert "else if (if" not in js
        check_gen_exec(code, "at least one small")


class TestGlobalNonlocalConstness:
    """Regression tests for global/nonlocal variable constness.

    Bug: Variables declared at module level were marked as 'const' if only
    assigned once at that level. But if they were modified via 'global'
    declaration in a function, the 'const' declaration would cause a
    "read-only" error in JavaScript.

    Fix: The Binder now marks the outer scope variable as mutable (is_const=False)
    when it encounters a 'global' or 'nonlocal' declaration.

    Commit: Stage 2 (2025-01-10)
    """

    def test_global_var_uses_let(self):
        """Global variable modified via 'global' should use 'let' not 'const'."""
        code = """
counter = 0

def increment():
    global counter
    counter = counter + 1

increment()
increment()
counter
"""
        js = py2js(code)
        # counter should be 'let' because it's modified via global
        assert "let counter = 0;" in js
        # Should NOT be const
        assert "const counter = 0;" not in js
        check_gen_exec(code, 2)

    def test_global_var_without_global_is_const(self):
        """Variable not modified via 'global' should still use 'const'."""
        code = """
x = 42

def foo():
    return x + 1

result = foo()
result
"""
        js = py2js(code)
        # x should be 'const' because it's never modified
        assert "const x = 42;" in js
        check_gen_exec(code, 43)

    def test_nonlocal_var_uses_let(self):
        """Enclosing variable modified via 'nonlocal' should use 'let'."""
        code = """
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count = count + 1
        return count
    return increment

counter = make_counter()
a = counter()
b = counter()
c = counter()
c
"""
        js = py2js(code)
        # count in outer function should be 'let'
        assert "let count = 0;" in js
        check_gen_exec(code, 3)

    def test_multiple_global_declarations(self):
        """Multiple functions using 'global' on same variable."""
        code = """
value = 10

def double_it():
    global value
    value = value * 2

def halve_it():
    global value
    value = value / 2

double_it()
double_it()
halve_it()
value
"""
        js = py2js(code)
        assert "let value = 10;" in js
        check_gen_exec(code, 20)
