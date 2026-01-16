"""Tests for bytes literals."""

from __future__ import annotations

from prescrypt import py2js


def js(code: str) -> str:
    """Compile Python to JavaScript without stdlib."""
    return py2js(code, include_stdlib=False)


class TestBytesLiteral:
    """Bytes literal compilation tests."""

    def test_empty_bytes(self):
        """Empty bytes literal b''"""
        code = 'b""'
        result = js(code)
        assert "new Uint8Array([])" in result

    def test_simple_bytes(self):
        """Simple bytes literal b'hello'"""
        code = 'b"hello"'
        result = js(code)
        # h=104, e=101, l=108, l=108, o=111
        assert "new Uint8Array([104, 101, 108, 108, 111])" in result

    def test_bytes_with_numbers(self):
        """Bytes literal with escape sequences"""
        code = r'b"\x00\x01\x02"'
        result = js(code)
        assert "new Uint8Array([0, 1, 2])" in result

    def test_bytes_assignment(self):
        """Bytes assigned to variable"""
        code = 'data = b"abc"'
        result = js(code)
        assert "new Uint8Array(" in result
        # a=97, b=98, c=99
        assert "97" in result

    def test_bytes_in_list(self):
        """Bytes literal in list"""
        code = '[b"a", b"b"]'
        result = js(code)
        assert "new Uint8Array([97])" in result
        assert "new Uint8Array([98])" in result
