"""Tests for code that runs correctly in strict mode.

ES6 modules run in strict mode by default, so generated code must
properly declare all variables with let/const/var.
"""

from __future__ import annotations

import pytest

from prescrypt import py2js
from prescrypt.testing import js_eval


def js_eval_strict(code: str):
    """Evaluate JavaScript code in strict mode."""
    strict_code = '"use strict";\n' + code
    return js_eval(strict_code)


class TestForLoopStrictMode:
    """Test that for loops properly declare temporary variables."""

    def test_for_loop_simple(self):
        """Simple for loop should work in strict mode."""
        code = """
items = [1, 2, 3]
total = 0
for x in items:
    total += x
result = total
"""
        js = py2js(code, include_stdlib=True)
        result = js_eval_strict(js + "\nresult;")
        assert result == 6

    def test_for_loop_with_list_comprehension_in_body(self):
        """For loop with list comprehension in body should work."""
        code = """
items = [1, 2, 3]
results = []
for x in items:
    doubled = [i * 2 for i in [x]]
    results.append(doubled[0])
result = results
"""
        js = py2js(code, include_stdlib=True)
        result = js_eval_strict(js + "\nresult;")
        assert result == [2, 4, 6]

    def test_nested_for_loops(self):
        """Nested for loops should work in strict mode."""
        code = """
matrix = [[1, 2], [3, 4]]
total = 0
for row in matrix:
    for cell in row:
        total += cell
result = total
"""
        js = py2js(code, include_stdlib=True)
        result = js_eval_strict(js + "\nresult;")
        assert result == 10

    def test_for_loop_with_filter_comprehension(self):
        """For loop with filtered comprehension should work."""
        code = """
todos = [
    {"id": 1, "completed": True},
    {"id": 2, "completed": False},
    {"id": 3, "completed": True}
]
completed_count = len([t for t in todos if t["completed"]])
result = completed_count
"""
        js = py2js(code, include_stdlib=True)
        result = js_eval_strict(js + "\nresult;")
        assert result == 2


class TestWhileLoopStrictMode:
    """Test that while loops properly declare variables."""

    def test_while_loop_simple(self):
        """Simple while loop should work in strict mode."""
        code = """
i = 0
total = 0
while i < 5:
    total += i
    i += 1
result = total
"""
        js = py2js(code, include_stdlib=True)
        result = js_eval_strict(js + "\nresult;")
        assert result == 10


class TestModuleModeStrictMode:
    """Test that module mode code works in strict mode."""

    def test_module_for_loop(self):
        """For loop in module mode generates proper variable declarations."""
        code = """
items = [1, 2, 3]
total = 0
for x in items:
    total += x
"""
        js = py2js(code, include_stdlib=True, module_mode=True)
        # Module mode adds exports, which QuickJS eval() doesn't support
        # So we strip exports and check the code is syntactically valid
        js_no_exports = js.replace("export ", "")
        result = js_eval_strict(js_no_exports + "\ntotal;")
        assert result == 6


class TestBrowserDemoPattern:
    """Test patterns from the browser demo that failed."""

    def test_for_loop_over_list_of_dicts(self):
        """For loop over list of dicts with comprehension filter."""
        code = """
todos = [
    {"id": 1, "text": "Learn", "completed": False},
    {"id": 2, "text": "Build", "completed": True},
]

def render():
    for todo in todos:
        pass
    completed = len([t for t in todos if t["completed"]])
    total = len(todos)
    return f"{completed}/{total}"

result = render()
"""
        js = py2js(code, include_stdlib=True)
        result = js_eval_strict(js + "\nresult;")
        assert result == "1/2"

    def test_function_with_for_loop(self):
        """Function containing for loop should declare temp vars."""
        code = """
def process(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result

result = process([1, 2, 3])
"""
        js = py2js(code, include_stdlib=True)
        result = js_eval_strict(js + "\nresult;")
        assert result == [2, 4, 6]
