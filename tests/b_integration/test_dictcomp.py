"""Tests for dict comprehensions."""

from __future__ import annotations

from prescrypt import py2js


def js(code: str) -> str:
    """Compile Python to JavaScript without stdlib."""
    return py2js(code, include_stdlib=False)


class TestDictCompBasic:
    """Basic dict comprehension tests."""

    def test_basic(self):
        """Basic dict comprehension {x: x*x for x in items}"""
        code = "{x: x*x for x in range(5)}"
        result = js(code)
        assert "dict_comprehension" in result
        assert "res = {}" in result
        assert "res[x]" in result

    def test_key_value_tuple(self):
        """Dict comprehension from key-value pairs {k: v for k, v in items}"""
        code = "{k: v for k, v in items}"
        result = js(code)
        assert "const k = iter0[i0][0]" in result
        assert "const v = iter0[i0][1]" in result
        assert "res[k] = v" in result


class TestDictCompConditions:
    """Dict comprehensions with conditions."""

    def test_with_if(self):
        """Dict comprehension with condition {k: v for k, v in items if v > 0}"""
        code = "{k: v for k, v in items if v > 0}"
        result = js(code)
        assert "if (!(" in result
        assert "v > 0" in result
        assert "continue" in result

    def test_multiple_ifs(self):
        """Dict comprehension with multiple conditions"""
        code = "{k: v for k, v in items if k > 0 if v < 10}"
        result = js(code)
        assert "k > 0" in result
        assert "v < 10" in result


class TestDictCompNested:
    """Nested dict comprehensions."""

    def test_nested_source(self):
        """Dict comprehension with nested iteration"""
        code = "{i: j for i in a for j in b}"
        result = js(code)
        # Should have two for loops
        assert "for (let i0" in result
        assert "for (let i1" in result


class TestDictCompExpressions:
    """Dict comprehensions with complex expressions."""

    def test_complex_key(self):
        """Dict comprehension with complex key expression"""
        code = "{str(x): x for x in items}"
        result = js(code)
        assert "res[" in result

    def test_complex_value(self):
        """Dict comprehension with complex value expression"""
        code = "{x: x + 1 for x in items}"
        result = js(code)
        assert "res[x]" in result
