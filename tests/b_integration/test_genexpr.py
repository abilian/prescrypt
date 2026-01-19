"""Tests for generator expressions."""

from __future__ import annotations

from prescrypt import py2js


def js(code: str) -> str:
    """Compile Python to JavaScript without stdlib."""
    return py2js(code, include_stdlib=False)


class TestGenExprBasic:
    """Basic generator expression tests."""

    def test_basic(self):
        """Basic generator expression (x*x for x in items)"""
        code = "(x*x for x in range(5))"
        result = js(code)
        assert "function*" in result
        assert "yield" in result
        assert "for (let x of" in result

    def test_with_list(self):
        """Generator expression passed to list()"""
        code = "list(x*x for x in range(5))"
        result = js(code)
        assert "_pyfunc_list" in result
        assert "function*" in result

    def test_assignment(self):
        """Generator expression assigned to variable"""
        code = "gen = (x for x in items)"
        result = js(code)
        assert "const gen" in result
        assert "function*" in result


class TestGenExprConditions:
    """Generator expressions with conditions."""

    def test_with_if(self):
        """Generator expression with condition"""
        code = "(x for x in items if x > 0)"
        result = js(code)
        assert "if (!" in result
        # Accept either native operator or runtime helper for unknown types
        assert "x > 0" in result or "op_gt(x, 0)" in result
        assert "continue" in result

    def test_multiple_ifs(self):
        """Generator expression with multiple conditions"""
        code = "(x for x in items if x > 0 if x < 10)"
        result = js(code)
        # Accept either native operator or runtime helper for unknown types
        assert "x > 0" in result or "op_gt(x, 0)" in result
        assert "x < 10" in result or "op_lt(x, 10)" in result


class TestGenExprNested:
    """Nested generator expressions."""

    def test_nested_loops(self):
        """Generator expression with nested iteration"""
        code = "((i, j) for i in a for j in b)"
        result = js(code)
        # Should have two for...of loops
        assert "for (let i of" in result
        assert "for (let j of" in result

    def test_inner_depends_on_outer(self):
        """Inner loop depends on outer variable"""
        code = "(j for i in range(3) for j in range(i))"
        result = js(code)
        assert "for (let i of" in result
        assert "for (let j of" in result


class TestGenExprUnpacking:
    """Generator expressions with tuple unpacking."""

    def test_tuple_unpacking(self):
        """Generator expression with tuple unpacking"""
        code = "(v for k, v in items)"
        result = js(code)
        assert "for (let [k, v] of" in result
        assert "yield v" in result

    def test_nested_unpacking(self):
        """Generator expression with nested tuple unpacking"""
        code = "(c for (a, b), c in items)"
        result = js(code)
        assert "[[a, b], c]" in result


class TestGenExprComplex:
    """Generator expressions with complex expressions."""

    def test_complex_element(self):
        """Generator expression with complex element expression"""
        code = "(x + 1 for x in items)"
        result = js(code)
        assert "yield" in result

    def test_method_call_element(self):
        """Generator expression with method call in element"""
        code = "(s.upper() for s in items)"
        result = js(code)
        assert "yield" in result

    def test_in_function_call(self):
        """Generator expression in function call"""
        code = "sum(x for x in range(10))"
        result = js(code)
        assert "_pyfunc_sum" in result
        assert "function*" in result

    def test_in_join(self):
        """Generator expression in str.join()"""
        code = "','.join(str(x) for x in items)"
        result = js(code)
        assert "_pymeth_join" in result
        assert "function*" in result
