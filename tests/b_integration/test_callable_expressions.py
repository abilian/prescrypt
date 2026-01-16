"""Tests for callable expressions (chained calls, subscript calls, etc.)."""

from __future__ import annotations

from prescrypt import py2js


def js(code: str) -> str:
    """Compile Python to JavaScript without stdlib."""
    return py2js(code, include_stdlib=False)


class TestChainedCalls:
    """Chained function calls: f(x)(y)"""

    def test_simple_chain(self):
        """f(1)(2) - call result of call"""
        code = "f(1)(2)"
        result = js(code)
        assert "(f(1))(2)" in result

    def test_triple_chain(self):
        """f()()(  ) - triple chain"""
        code = "f()()()"
        result = js(code)
        assert "((f())())()" in result

    def test_closure_pattern(self):
        """Closure returning function"""
        code = """
def make_adder(x):
    def add(y):
        return x + y
    return add

result = make_adder(5)(3)
"""
        result = js(code)
        assert "(make_adder(5))(3)" in result


class TestSubscriptCalls:
    """Calling subscript results: items[0]()"""

    def test_dict_call(self):
        """d['key']() - call dict value"""
        code = "d['key']()"
        result = js(code)
        # Should generate something like (d['key'])()
        assert "d" in result and "key" in result

    def test_list_call(self):
        """funcs[0]() - call list element"""
        code = "funcs[0]()"
        result = js(code)
        assert "funcs" in result

    def test_subscript_with_args(self):
        """handlers[name](x, y)"""
        code = "handlers[name](x, y)"
        result = js(code)
        assert "handlers" in result
        assert "x" in result and "y" in result


class TestLiteralCalls:
    """Calling literals (runtime error cases)."""

    def test_int_call(self):
        """1() - calling int (TypeError at runtime)"""
        code = "1()"
        result = js(code)
        assert "(1)()" in result

    def test_string_call(self):
        """ "hello"() - calling string"""
        code = '"hello"()'
        result = js(code)
        assert "hello" in result


class TestConditionalCalls:
    """Calling conditional expression results."""

    def test_ternary_call(self):
        """(foo if cond else bar)()"""
        code = "(foo if cond else bar)()"
        result = js(code)
        assert "cond" in result
        assert "foo" in result
        assert "bar" in result


class TestLambdaCalls:
    """Immediately invoked lambdas."""

    def test_iife_lambda(self):
        """(lambda x: x + 1)(5)"""
        code = "(lambda x: x + 1)(5)"
        result = js(code)
        assert "=>" in result
        assert "5" in result
