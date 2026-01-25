"""Tests for loop variable scoping.

Python has function-level scoping, not block-level scoping like JavaScript.
Variables assigned inside loops should be accessible after the loop ends.
"""
from __future__ import annotations

from prescrypt import py2js
from prescrypt.testing import js_eval


class TestForLoopScoping:
    """Test for loop variable accessibility after loop."""

    def test_loop_variable_after_loop(self):
        """Loop variable should be accessible after the loop."""
        code = """
for i in range(3):
    pass
i
"""
        assert js_eval(py2js(code)) == 2

    def test_variable_assigned_in_loop(self):
        """Variables assigned inside loop should be accessible after."""
        code = """
for i in range(3):
    x = i
x
"""
        assert js_eval(py2js(code)) == 2

    def test_multiple_loops_same_variable(self):
        """Same variable name in multiple loops should work."""
        code = """
for i in range(3):
    x = i

for i in range(5):
    y = i

[x, y]
"""
        assert js_eval(py2js(code)) == [2, 4]

    def test_nested_loops(self):
        """Variables from nested loops should all be accessible."""
        code = """
result = []
for i in range(2):
    for j in range(2):
        result.append([i, j])
[i, j, result]
"""
        result = js_eval(py2js(code))
        assert result[0] == 1  # i
        assert result[1] == 1  # j
        assert result[2] == [[0, 0], [0, 1], [1, 0], [1, 1]]

    def test_tuple_unpacking_in_loop(self):
        """Tuple unpacking variables should be accessible after loop."""
        code = """
for i, v in enumerate([10, 20, 30]):
    x = v
[i, x]
"""
        assert js_eval(py2js(code)) == [2, 30]

    def test_loop_with_condition(self):
        """Variables assigned in conditional inside loop should be accessible."""
        code = """
for i in range(5):
    if i > 2:
        x = i
x
"""
        assert js_eval(py2js(code)) == 4


class TestWhileLoopScoping:
    """Test while loop variable accessibility after loop."""

    def test_variable_in_while_loop(self):
        """Variables assigned inside while loop should be accessible after."""
        code = """
i = 0
while i < 3:
    x = i
    i += 1
x
"""
        assert js_eval(py2js(code)) == 2

    def test_multiple_variables_in_while(self):
        """Multiple variables in while should all be accessible."""
        code = """
i = 0
while i < 3:
    x = i
    y = i * 2
    i += 1
[x, y]
"""
        assert js_eval(py2js(code)) == [2, 4]


class TestLoopElseScoping:
    """Test loop else clause scoping."""

    def test_for_else_variable(self):
        """Variables in for-else should be accessible."""
        code = """
for i in range(3):
    x = i
else:
    y = 100
[x, y]
"""
        assert js_eval(py2js(code)) == [2, 100]

    def test_while_else_variable(self):
        """Variables in while-else should be accessible."""
        code = """
i = 0
while i < 2:
    x = i
    i += 1
else:
    y = 200
[x, y]
"""
        assert js_eval(py2js(code)) == [1, 200]
