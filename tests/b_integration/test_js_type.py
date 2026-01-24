"""Tests for JS type annotation feature.

Tests that variables annotated with `JS` or `JSObject` type bypass
Python stdlib transformations and use native JS method calls.

Usage:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from prescrypt import JS

    result: JS = some_js_api_call()
    value = result.get("key")  # Native JS .get(), not _pymeth_get
"""

from __future__ import annotations

from prescrypt import py2js


class TestJSTypeBasic:
    """Basic tests for JS type annotation."""

    def test_js_type_imported_in_types(self):
        """JSObject and JS should be importable from types module."""
        from prescrypt.front.passes.types import JS, JSObject

        assert JS is JSObject

    def test_js_annotated_var_method_bypass(self):
        """Method calls on JS-typed variables should bypass _pymeth_ prefix."""
        code = """
obj: JS = get_js_object()
value = obj.get("key")
"""
        js = py2js(code, include_stdlib=False)
        # Should NOT use _pymeth_get for JS-typed object
        assert "_pymeth_get" not in js
        # Should be native .get() call
        assert ".get(" in js

    def test_jsobject_annotated_var_method_bypass(self):
        """Method calls on JSObject-typed variables should bypass _pymeth_ prefix."""
        code = """
obj: JSObject = get_js_object()
value = obj.get("key")
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_get" not in js
        assert ".get(" in js

    def test_js_type_in_function_param(self):
        """Function parameters typed as JS should bypass stdlib."""
        code = """
def process(obj: JS):
    value = obj.get("key")
    return value
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_get" not in js

    def test_js_type_preserves_native_methods(self):
        """JS-typed objects should use native keys(), values(), items()."""
        code = """
obj: JS = get_js_object()
k = obj.keys()
v = obj.values()
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_keys" not in js
        assert "_pymeth_values" not in js
        assert ".keys()" in js
        assert ".values()" in js


class TestJSTypeWithStdlib:
    """Tests that verify JS type bypass works for common patterns."""

    def test_js_type_clear_method(self):
        """JS-typed objects should use native .clear()."""
        code = """
storage: JS = get_storage()
storage.clear()
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_clear" not in js
        assert ".clear()" in js

    def test_js_type_update_method(self):
        """JS-typed objects should use native .update()."""
        code = """
obj: JS = get_object()
obj.update(data)
"""
        js = py2js(code, include_stdlib=False)
        assert "_pymeth_update" not in js
        assert ".update(" in js


class TestJSTypeVsRegularDict:
    """Compare behavior between JS-typed and regular dict."""

    def test_regular_dict_uses_pymeth(self):
        """Regular dicts should still use _pymeth_ methods."""
        code = """
obj = {"key": "value"}
value = obj.get("key")
"""
        js = py2js(code, include_stdlib=False)
        # Regular dict should use _pymeth_get
        assert "_pymeth_get" in js

    def test_annotated_dict_still_uses_pymeth(self):
        """Variables typed as dict should still use _pymeth_."""
        code = """
obj: dict = {"key": "value"}
value = obj.get("key")
"""
        js = py2js(code, include_stdlib=False)
        # dict-typed should still use _pymeth_get for Python compatibility
        assert "_pymeth_get" in js


class TestJSTypeTypeChecking:
    """Test JS type with TYPE_CHECKING guard."""

    def test_js_type_with_type_checking_guard(self):
        """JS type should work with TYPE_CHECKING import pattern."""
        code = """
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from prescrypt import JS

result: JS = fetch_data()
value = result.get("key")
"""
        js = py2js(code, include_stdlib=False)
        # The TYPE_CHECKING block is compile-time only
        # The annotation should still take effect
        assert "_pymeth_get" not in js


class TestFromJsImport:
    """Test 'from js import X' syntax."""

    def test_from_js_import_basic(self):
        """'from js import document' should make document a JS FFI name."""
        code = """
from js import document
element = document.getElementById("myid")
"""
        js = py2js(code, include_stdlib=False)
        # No import statement should be generated
        assert "import" not in js.lower() or "/* from" in js
        # document should be used directly
        assert "document.getElementById" in js
        # Should NOT be treated as Python method
        assert "_pymeth_" not in js

    def test_from_js_import_multiple(self):
        """Multiple imports from js should all work."""
        code = """
from js import document, console, fetch
console.log("hello")
doc = document.body
result = fetch("/api")
"""
        js = py2js(code, include_stdlib=False)
        assert "console.log" in js
        assert "document.body" in js
        assert "fetch(" in js
        assert "_pymeth_" not in js

    def test_from_js_import_with_alias(self):
        """'from js import X as Y' should work with alias."""
        code = """
from js import document as doc
element = doc.querySelector(".class")
"""
        js = py2js(code, include_stdlib=False)
        assert "doc.querySelector" in js
        assert "_pymeth_" not in js

    def test_from_js_import_method_bypass(self):
        """Methods on js-imported names should bypass Python stdlib."""
        code = """
from js import storage
value = storage.get("key")
storage.set("key", "value")
keys = storage.keys()
"""
        js = py2js(code, include_stdlib=False)
        # All methods should be native, not _pymeth_
        assert "_pymeth_get" not in js
        assert "_pymeth_set" not in js
        assert "_pymeth_keys" not in js
        assert "storage.get(" in js
        assert "storage.set(" in js
        assert "storage.keys()" in js

    def test_from_js_import_chained_access(self):
        """Chained access on js-imported names should work."""
        code = """
from js import chrome
result = chrome.storage.local.get("repos")
"""
        js = py2js(code, include_stdlib=False)
        assert "chrome.storage.local.get" in js
        assert "_pymeth_" not in js

    def test_from_js_import_new_method(self):
        """'.new()' on js-imported names should create new instances."""
        code = """
from js import Date, RegExp
today = Date.new()
pattern = RegExp.new("[a-z]+", "gi")
"""
        js = py2js(code, include_stdlib=False)
        assert "new Date()" in js
        # Check for RegExp constructor (quotes may vary)
        assert "new RegExp(" in js
        assert "[a-z]+" in js
