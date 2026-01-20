"""Tests for tuple/list unpacking and multiple assignment."""

from __future__ import annotations

from prescrypt import py2js


def js(code: str) -> str:
    """Compile Python to JavaScript without stdlib."""
    return py2js(code, include_stdlib=False)


class TestBasicUnpack:
    """Basic tuple unpacking tests."""

    def test_unpack_tuple(self):
        """Basic tuple unpacking a, b = 1, 2"""
        code = "a, b = 1, 2"
        result = js(code)
        assert "let [a, b] = [1, 2]" in result

    def test_unpack_list(self):
        """Unpacking from list a, b = [1, 2]"""
        code = "a, b = [1, 2]"
        result = js(code)
        # List is marked with _is_list for proper repr()
        assert "let [a, b] = Object.assign([1, 2], {_is_list: true})" in result

    def test_unpack_three(self):
        """Unpack three values"""
        code = "a, b, c = 1, 2, 3"
        result = js(code)
        assert "let [a, b, c] = [1, 2, 3]" in result

    def test_unpack_parens(self):
        """Unpacking with parentheses (a, b) = (1, 2)"""
        code = "(a, b) = (1, 2)"
        result = js(code)
        assert "[a, b] = [1, 2]" in result


class TestReassignment:
    """Tests for unpacking with reassignment."""

    def test_swap(self):
        """Variable swap a, b = b, a"""
        code = "a = 1; b = 2; a, b = b, a"
        result = js(code)
        # First assignments use let
        assert "let a = 1" in result
        assert "let b = 2" in result
        # Swap uses no declaration (reassignment)
        assert "[a, b] = [b, a]" in result

    def test_rotate(self):
        """Three-way rotate a, b, c = b, c, a"""
        code = "a = 1; b = 2; c = 3; a, b, c = b, c, a"
        result = js(code)
        assert "[a, b, c] = [b, c, a]" in result


class TestMultipleAssignment:
    """Tests for multiple assignment a = b = c = 3."""

    def test_double_assign(self):
        """Double assignment a = b = 2"""
        code = "a = b = 2"
        result = js(code)
        # Should declare both variables with value 2
        assert "b = 2" in result
        assert "a = 2" in result

    def test_triple_assign(self):
        """Triple assignment a = b = c = 3"""
        code = "a = b = c = 3"
        result = js(code)
        # All variables should be assigned value 3
        assert "c = 3" in result
        assert "b = 3" in result
        assert "a = 3" in result


class TestNestedUnpack:
    """Tests for nested unpacking."""

    def test_nested_basic(self):
        """Nested unpacking (a, b), c = ((1, 2), 3)"""
        code = "(a, b), c = ((1, 2), 3)"
        result = js(code)
        assert "[[a, b], c]" in result

    def test_nested_deep(self):
        """Deeper nested unpacking"""
        code = "((a, b), c), d = (((1, 2), 3), 4)"
        result = js(code)
        assert "[[[a, b], c], d]" in result


class TestStarredUnpack:
    """Tests for starred unpacking."""

    def test_starred_end(self):
        """Starred at end: first, *rest = items"""
        code = "first, *rest = [1, 2, 3]"
        result = js(code)
        assert "[first, ...rest]" in result

    def test_starred_start(self):
        """Starred at start: *start, last = items"""
        code = "*start, last = [1, 2, 3]"
        result = js(code)
        # Needs temp variable for pop
        assert "pop()" in result
        assert "start" in result
        assert "last" in result

    def test_starred_middle(self):
        """Starred in middle: a, *middle, z = items"""
        code = "a, *middle, z = [1, 2, 3, 4, 5]"
        result = js(code)
        assert "pop()" in result
        assert "middle" in result


class TestChainedSubscriptAssign:
    """Tests for chained assignment with subscripts and attributes."""

    def test_chained_subscript(self):
        """Chained assignment with subscripts: a[0] = a[1] = value"""
        from prescrypt.testing import js_eval

        code = "a = [True, True]; a[0] = a[1] = False; a"
        result = js_eval(py2js(code))
        assert result == [False, False]

    def test_chained_subscript_int(self):
        """Chained assignment with subscripts using integers."""
        from prescrypt.testing import js_eval

        code = "a = [0, 0, 0]; a[0] = a[1] = a[2] = 5; a"
        result = js_eval(py2js(code))
        assert result == [5, 5, 5]

    def test_chained_attr(self):
        """Chained assignment with attributes: c.x = c.y = value"""
        from prescrypt.testing import js_eval

        code = """
class C:
    x = 0
    y = 0
c = C()
c.x = c.y = 5
[c.x, c.y]
"""
        result = js_eval(py2js(code))
        assert result == [5, 5]

    def test_mixed_chained(self):
        """Chained assignment mixing names, subscripts, and attributes."""
        from prescrypt.testing import js_eval

        code = """
class C:
    x = 0
c = C()
b = [0]
a = b[0] = c.x = 3
[a, b[0], c.x]
"""
        result = js_eval(py2js(code))
        assert result == [3, 3, 3]

    def test_chained_dict_subscript(self):
        """Chained assignment with dict subscripts."""
        from prescrypt.testing import js_eval

        code = "d = {}; d['a'] = d['b'] = 10; [d['a'], d['b']]"
        result = js_eval(py2js(code))
        assert result == [10, 10]
