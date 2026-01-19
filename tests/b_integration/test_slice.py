"""Tests for slice expressions."""

from __future__ import annotations

from prescrypt import py2js


def js(code: str) -> str:
    """Compile Python to JavaScript without stdlib."""
    return py2js(code, include_stdlib=False)


class TestSliceBasic:
    """Basic slice tests - use native .slice()"""

    def test_slice_full(self):
        """Full slice a[:]"""
        code = "a = [1, 2, 3]; b = a[:]"
        result = js(code)
        assert "a.slice()" in result

    def test_slice_start(self):
        """Slice from start a[1:]"""
        code = "a = [1, 2, 3]; b = a[1:]"
        result = js(code)
        assert "a.slice(1)" in result

    def test_slice_end(self):
        """Slice to end a[:2]"""
        code = "a = [1, 2, 3]; b = a[:2]"
        result = js(code)
        assert "a.slice(0, 2)" in result

    def test_slice_both(self):
        """Slice with start and end a[1:3]"""
        code = "a = [1, 2, 3, 4, 5]; b = a[1:3]"
        result = js(code)
        assert "a.slice(1, 3)" in result

    def test_slice_negative_start(self):
        """Slice with negative start a[-2:]"""
        code = "a = [1, 2, 3, 4, 5]; b = a[-2:]"
        result = js(code)
        assert "a.slice(-2)" in result

    def test_slice_negative_end(self):
        """Slice with negative end a[:-1]"""
        code = "a = [1, 2, 3, 4, 5]; b = a[:-1]"
        result = js(code)
        assert "a.slice(0, -1)" in result

    def test_slice_both_negative(self):
        """Slice with both negative a[-3:-1]"""
        code = "a = [1, 2, 3, 4, 5]; b = a[-3:-1]"
        result = js(code)
        assert "a.slice(-3, -1)" in result


class TestSliceStep:
    """Slice with step - uses _pyfunc_slice"""

    def test_slice_step_only(self):
        """Slice with step only a[::2]"""
        code = "a = [1, 2, 3, 4, 5]; b = a[::2]"
        result = js(code)
        assert "_pyfunc_slice(a, null, null, 2)" in result

    def test_slice_reverse(self):
        """Reverse slice a[::-1]"""
        code = "a = [1, 2, 3]; b = a[::-1]"
        result = js(code)
        assert "_pyfunc_slice(a, null, null, -1)" in result

    def test_slice_start_step(self):
        """Slice with start and step a[1::2]"""
        code = "a = [1, 2, 3, 4, 5]; b = a[1::2]"
        result = js(code)
        assert "_pyfunc_slice(a, 1, null, 2)" in result

    def test_slice_end_step(self):
        """Slice with end and step a[:4:2]"""
        code = "a = [1, 2, 3, 4, 5]; b = a[:4:2]"
        result = js(code)
        assert "_pyfunc_slice(a, null, 4, 2)" in result

    def test_slice_all_three(self):
        """Slice with start, end, and step a[1:5:2]"""
        code = "a = [1, 2, 3, 4, 5, 6]; b = a[1:5:2]"
        result = js(code)
        assert "_pyfunc_slice(a, 1, 5, 2)" in result


class TestSliceEmpty:
    """Edge cases with empty slices"""

    def test_empty_slice(self):
        """Empty slice with :: is same as [:]"""
        code = "a = [1, 2, 3]; b = a[::]"
        result = js(code)
        assert "a.slice()" in result


class TestSliceAssignment:
    """Slice assignment tests"""

    def test_slice_assign_basic(self):
        """Basic slice assignment a[1:3] = [10, 20]"""
        code = "a = [1, 2, 3, 4, 5]; a[1:3] = [10, 20]"
        result = js(code)
        # List literals are marked with _is_list for proper repr()
        assert (
            "a.splice(1, 3 - 1, ...Object.assign([10, 20], {_is_list: true}))" in result
        )

    def test_slice_assign_from_start(self):
        """Slice assignment from start a[:2] = [10, 20]"""
        code = "a = [1, 2, 3, 4, 5]; a[:2] = [10, 20]"
        result = js(code)
        assert (
            "a.splice(0, 2 - 0, ...Object.assign([10, 20], {_is_list: true}))" in result
        )

    def test_slice_assign_to_end(self):
        """Slice assignment to end a[2:] = [10, 20]"""
        code = "a = [1, 2, 3, 4, 5]; a[2:] = [10, 20]"
        result = js(code)
        assert (
            "a.splice(2, a.length - 2, ...Object.assign([10, 20], {_is_list: true}))"
            in result
        )


class TestSliceStrings:
    """Slice on strings"""

    def test_string_slice(self):
        """String slicing s[1:3]"""
        code = 's = "hello"; b = s[1:3]'
        result = js(code)
        assert "s.slice(1, 3)" in result

    def test_string_slice_reverse_uses_helper(self):
        """String reverse slice s[::-1] uses helper"""
        code = 's = "hello"; b = s[::-1]'
        result = js(code)
        assert "_pyfunc_slice(s, null, null, -1)" in result
