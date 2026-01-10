from __future__ import annotations

import pytest

from .utils import check_gen_exec


class TestTryExcept:
    """Test try/except code generation."""

    def test_try_except_basic(self):
        """Test basic try/except."""
        code = """
result = 'no error'
try:
    raise ValueError('test')
except:
    result = 'caught'
result
"""
        check_gen_exec(code, "caught")

    def test_try_except_specific_type(self):
        """Test try/except with specific exception type."""
        code = """
result = 'no error'
try:
    raise ValueError('test')
except ValueError:
    result = 'caught ValueError'
result
"""
        check_gen_exec(code, "caught ValueError")

    def test_try_except_wrong_type(self):
        """Test try/except with non-matching exception type (should re-raise)."""
        code = """
result = 'no error'
try:
    try:
        raise TypeError('test')
    except ValueError:
        result = 'caught ValueError'
except:
    result = 'caught other'
result
"""
        check_gen_exec(code, "caught other")

    def test_try_except_finally(self):
        """Test try/except/finally."""
        code = """
result = []
try:
    result.append('try')
    raise ValueError('error')
except ValueError:
    result.append('except')
finally:
    result.append('finally')
result
"""
        check_gen_exec(code, ["try", "except", "finally"])

    def test_try_finally_no_except(self):
        """Test try/finally without except."""
        code = """
result = []
try:
    result.append('try')
finally:
    result.append('finally')
result
"""
        check_gen_exec(code, ["try", "finally"])

    def test_multiple_except_clauses(self):
        """Test multiple except clauses."""
        code = """
result = 'no match'
try:
    raise TypeError('test')
except ValueError:
    result = 'ValueError'
except TypeError:
    result = 'TypeError'
result
"""
        check_gen_exec(code, "TypeError")

    def test_except_catch_all_last(self):
        """Test catch-all except clause at the end."""
        code = """
result = 'no match'
try:
    raise KeyError('test')
except ValueError:
    result = 'ValueError'
except:
    result = 'other'
result
"""
        check_gen_exec(code, "other")


class TestRaise:
    """Test raise statement code generation."""

    def test_raise_exception(self):
        """Test raise with exception type and message."""
        code = """
result = 'no error'
try:
    raise ValueError('test message')
except ValueError:
    result = 'caught'
result
"""
        check_gen_exec(code, "caught")

    def test_raise_exception_no_message(self):
        """Test raise with exception type only."""
        code = """
result = 'no error'
try:
    raise ValueError
except ValueError:
    result = 'caught'
result
"""
        check_gen_exec(code, "caught")


class TestAssert:
    """Test assert statement code generation."""

    def test_assert_true(self):
        """Test assert with true condition."""
        code = """
result = 'passed'
assert True
result
"""
        check_gen_exec(code, "passed")

    def test_assert_false(self):
        """Test assert with false condition (should raise)."""
        code = """
result = 'not raised'
try:
    assert False
except:
    result = 'raised'
result
"""
        check_gen_exec(code, "raised")
