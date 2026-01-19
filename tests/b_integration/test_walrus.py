"""Tests for walrus operator (:=)."""

from __future__ import annotations

from prescrypt import py2js


def js(code: str) -> str:
    """Compile Python to JavaScript without stdlib."""
    return py2js(code, include_stdlib=False)


class TestWalrusBasic:
    """Basic walrus operator tests."""

    def test_simple_walrus(self):
        """Simple walrus operator (x := 4)"""
        code = "(x := 4)"
        result = js(code)
        # Variable should be declared before use
        assert "let x;" in result
        assert "(x = 4)" in result

    def test_walrus_in_if(self):
        """Walrus in if condition"""
        code = """
if x := get_value():
    print(x)
"""
        result = js(code)
        assert "x =" in result

    def test_walrus_in_while(self):
        """Walrus in while condition"""
        code = """
while x := next_item():
    process(x)
"""
        result = js(code)
        assert "x =" in result

    def test_walrus_existing_var(self):
        """Walrus with existing variable"""
        code = """
x = 0
if x := 5:
    print(x)
"""
        result = js(code)
        # Should only have one var x declaration
        assert result.count("var x") <= 1

    def test_walrus_in_expression(self):
        """Walrus in complex expression"""
        code = "y = (x := 3) + 1"
        result = js(code)
        assert "x = 3" in result


class TestWalrusScope:
    """Walrus operator scoping tests."""

    def test_walrus_in_function(self):
        """Walrus in function creates local variable"""
        code = """
def f():
    if x := get():
        return x
    return None
"""
        result = js(code)
        assert "var x" in result or "let x" in result or "x =" in result

    def test_multiple_walrus_same_var(self):
        """Multiple walrus with same variable"""
        code = """
if (x := 1) and (x := 2):
    print(x)
"""
        result = js(code)
        # Second walrus shouldn't re-declare
        assert "x = 1" in result
        assert "x = 2" in result
