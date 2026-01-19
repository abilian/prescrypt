"""Tests for starred expressions in function calls."""

from __future__ import annotations

from prescrypt import py2js


def js(code: str) -> str:
    """Compile Python to JavaScript without stdlib."""
    return py2js(code, include_stdlib=False)


class TestStarredBasic:
    """Basic starred expression tests."""

    def test_starred_in_call(self):
        """Starred in function call f(*args)"""
        code = "f(*args)"
        result = js(code)
        # Regular function calls use .apply() for starred args
        assert "apply" in result and "args" in result

    def test_starred_tuple(self):
        """Starred tuple f(*(1, 2))"""
        code = "f(*(1, 2))"
        result = js(code)
        # Should use apply with concat
        assert "[1, 2]" in result

    def test_starred_with_regular_args(self):
        """Starred with regular args f(a, *args, b)"""
        code = "f(a, *args, b)"
        result = js(code)
        assert "concat" in result


class TestStarredStdlib:
    """Starred expressions with stdlib functions."""

    def test_round_starred(self):
        """round(*t) should compile"""
        code = "round(*t)"
        result = js(code)
        assert "_pyfunc_round" in result
        assert "...t" in result

    def test_len_starred(self):
        """len(*args) - though unusual"""
        code = "len(*args)"
        result = js(code)
        assert "...args" in result


class TestDoubleStarred:
    """Double-starred (kwargs) expressions."""

    def test_kwargs_only(self):
        """f(**kwargs) now uses call_kwargs helper"""
        code = "f(**kwargs)"
        result = js(code)
        # Now uses call_kwargs for proper kwargs unpacking
        assert "call_kwargs" in result
        assert "kwargs" in result

    def test_args_and_kwargs(self):
        """f(*args, **kwargs) now uses call_kwargs helper"""
        code = "f(*args, **kwargs)"
        result = js(code)
        # Now uses call_kwargs for proper kwargs unpacking
        assert "call_kwargs" in result
        assert "args" in result
        assert "kwargs" in result


class TestStarredInList:
    """Starred in list literals [*a, *b]."""

    def test_starred_in_list(self):
        """[*a, *b] should use spread"""
        code = "[*a, *b]"
        result = js(code)
        assert "...a" in result
        assert "...b" in result

    def test_mixed_list(self):
        """[1, *a, 2] mixed list"""
        code = "[1, *a, 2]"
        result = js(code)
        assert "...a" in result
