"""Tests for try-else clause and bare raise."""

from __future__ import annotations

from prescrypt import py2js


def js(code: str) -> str:
    """Compile Python to JavaScript without stdlib."""
    return py2js(code, include_stdlib=False)


class TestTryElse:
    """Tests for try-else clause."""

    def test_try_else_basic(self):
        """Basic try-else clause."""
        code = """
try:
    result = 1
except ValueError:
    result = -1
else:
    result = result + 1
"""
        result = js(code)
        assert "_no_exc_" in result
        assert "if (_no_exc_" in result
        assert "= false" in result

    def test_try_else_no_exception_type(self):
        """try-else with bare except."""
        code = """
try:
    x = risky()
except:
    x = 0
else:
    x = 1
"""
        result = js(code)
        assert "_no_exc_" in result
        assert "if (_no_exc_" in result

    def test_try_else_finally(self):
        """try-else-finally combination."""
        code = """
try:
    x = risky()
except Exception:
    x = 0
else:
    x = 1
finally:
    cleanup()
"""
        result = js(code)
        assert "_no_exc_" in result
        assert "if (_no_exc_" in result
        assert "finally" in result
        assert "cleanup()" in result

    def test_try_else_multiple_handlers(self):
        """try-else with multiple except handlers."""
        code = """
try:
    x = risky()
except ValueError:
    x = 1
except TypeError:
    x = 2
else:
    x = 0
"""
        result = js(code)
        assert "_no_exc_" in result
        assert "ValueError" in result
        assert "TypeError" in result

    def test_try_without_else(self):
        """Regular try without else should not have flag."""
        code = """
try:
    x = risky()
except Exception:
    x = 0
"""
        result = js(code)
        assert "_no_exc_" not in result


class TestBareRaise:
    """Tests for bare raise (re-raise)."""

    def test_bare_raise_basic(self):
        """Bare raise re-throws current exception."""
        code = """
try:
    risky()
except ValueError as e:
    log(e)
    raise
"""
        result = js(code)
        assert "throw err_" in result
        # Should have two throws: the bare raise and the rethrow for non-matching
        assert result.count("throw") >= 1

    def test_bare_raise_without_as(self):
        """Bare raise without 'as' clause."""
        code = """
try:
    risky()
except ValueError:
    cleanup()
    raise
"""
        result = js(code)
        assert "throw err_" in result

    def test_bare_raise_nested(self):
        """Bare raise in nested try-except."""
        code = """
try:
    try:
        risky()
    except ValueError:
        raise
except Exception:
    handle()
"""
        result = js(code)
        # Should compile without error
        assert "catch" in result

    def test_bare_raise_with_else(self):
        """Bare raise combined with else clause."""
        code = """
try:
    risky()
except ValueError:
    raise
else:
    success()
"""
        result = js(code)
        assert "_no_exc_" in result
        assert "throw" in result


class TestExceptionHandling:
    """Combined exception handling tests."""

    def test_exception_name_binding(self):
        """Exception bound to variable name."""
        code = """
try:
    risky()
except ValueError as exc:
    print(exc)
"""
        result = js(code)
        assert "exc = err_" in result

    def test_multiple_except_with_names(self):
        """Multiple except clauses with different names."""
        code = """
try:
    risky()
except ValueError as ve:
    handle_value(ve)
except TypeError as te:
    handle_type(te)
"""
        result = js(code)
        assert "ve = err_" in result
        assert "te = err_" in result
