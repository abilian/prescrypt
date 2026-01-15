"""Tests for ES6 module export generation."""

from __future__ import annotations

import pytest

from prescrypt.compiler import py2js


class TestModuleModeExports:
    """Test that module_mode=True generates ES6 exports."""

    def test_variable_export(self):
        """Module-level variables should be exported."""
        code = "x = 1"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "export" in js
        assert "export const x = 1" in js or "export let x = 1" in js

    def test_const_variable_export(self):
        """Constant variables should use export const."""
        code = "PI = 3.14"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "export const PI = 3.14" in js

    def test_let_variable_export(self):
        """Reassigned variables should use export let."""
        code = "x = 1\nx = 2"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "export let x = 1" in js

    def test_function_export(self):
        """Module-level functions should be exported."""
        code = "def greet(name):\n    return name"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "export function greet" in js

    def test_async_function_export(self):
        """Async functions should be exported."""
        code = "async def fetch_data():\n    return 1"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "export async function fetch_data" in js

    def test_class_export(self):
        """Module-level classes should be exported."""
        code = "class MyClass:\n    pass"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "export MyClass = function" in js

    def test_nested_function_not_exported(self):
        """Nested functions inside functions should not be exported."""
        code = """
def outer():
    def inner():
        pass
    return inner
"""
        js = py2js(code, include_stdlib=False, module_mode=True)
        # Only outer should be exported
        assert js.count("export") == 1
        assert "export function outer" in js
        # inner should not have export
        assert "export function inner" not in js
        assert "export let inner" not in js

    def test_class_method_not_exported(self):
        """Methods inside classes should not be exported."""
        code = """
class MyClass:
    def method(self):
        pass
"""
        js = py2js(code, include_stdlib=False, module_mode=True)
        # Only class should be exported
        assert "export MyClass = function" in js
        # Method should not have export
        assert "export" in js
        lines_with_export = [line for line in js.split("\n") if "export" in line]
        assert len(lines_with_export) == 1

    def test_class_attribute_not_exported(self):
        """Class attributes should not be exported separately."""
        code = """
class MyClass:
    value = 42
"""
        js = py2js(code, include_stdlib=False, module_mode=True)
        # Only class should be exported
        assert "export MyClass = function" in js
        # Class attribute should not have export
        lines_with_export = [line for line in js.split("\n") if "export" in line]
        assert len(lines_with_export) == 1


class TestModuleModeDisabled:
    """Test that module_mode=False (default) does not generate exports."""

    def test_variable_no_export_default(self):
        """Variables should not be exported by default."""
        code = "x = 1"
        js = py2js(code, include_stdlib=False)  # module_mode=False by default
        assert "export" not in js

    def test_function_no_export_default(self):
        """Functions should not be exported by default."""
        code = "def greet(name):\n    return name"
        js = py2js(code, include_stdlib=False)
        assert "export" not in js

    def test_class_no_export_default(self):
        """Classes should not be exported by default."""
        code = "class MyClass:\n    pass"
        js = py2js(code, include_stdlib=False)
        assert "export" not in js

    def test_explicit_module_mode_false(self):
        """Explicit module_mode=False should not generate exports."""
        code = "x = 1\ndef f(): pass\nclass C: pass"
        js = py2js(code, include_stdlib=False, module_mode=False)
        assert "export" not in js


class TestModuleModeWithStdlib:
    """Test module mode with stdlib included."""

    def test_stdlib_functions_not_exported(self):
        """Stdlib functions should not be exported."""
        code = "print('hello')"
        js = py2js(code, include_stdlib=True, module_mode=True)
        # The preamble stdlib functions should not have export
        # Only the user code might have exports (but there's nothing to export here)
        # Check that _pyfunc_ functions don't have export
        assert "export var _pyfunc_" not in js
        assert "export function _pyfunc_" not in js

    def test_user_code_exported_with_stdlib(self):
        """User code should be exported even when stdlib is included."""
        code = "x = len([1, 2, 3])"
        js = py2js(code, include_stdlib=True, module_mode=True)
        # The variable assignment should be exported
        assert "export" in js
        # Check that it's the user code being exported, not stdlib
        lines = js.split("\n")
        export_lines = [line for line in lines if line.strip().startswith("export")]
        assert any("x =" in line for line in export_lines)


class TestModuleModeImports:
    """Test that module_mode=True generates ES6 imports."""

    def test_simple_import(self):
        """import foo -> import * as foo from './foo.js'"""
        code = "import foo"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import * as foo from './foo.js'" in js

    def test_import_with_alias(self):
        """import foo as f -> import * as f from './foo.js'"""
        code = "import foo as f"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import * as f from './foo.js'" in js

    def test_import_nested_module(self):
        """import foo.bar.baz -> import * as foo from './foo/bar/baz.js'"""
        code = "import foo.bar.baz"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import * as foo from './foo/bar/baz.js'" in js

    def test_import_nested_with_alias(self):
        """import foo.bar as fb -> import * as fb from './foo/bar.js'"""
        code = "import foo.bar as fb"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import * as fb from './foo/bar.js'" in js

    def test_from_import_single(self):
        """from foo import bar -> import { bar } from './foo.js'"""
        code = "from foo import bar"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import { bar } from './foo.js'" in js

    def test_from_import_multiple(self):
        """from foo import bar, baz -> import { bar, baz } from './foo.js'"""
        code = "from foo import bar, baz"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import { bar, baz } from './foo.js'" in js

    def test_from_import_with_alias(self):
        """from foo import bar as b -> import { bar as b } from './foo.js'"""
        code = "from foo import bar as b"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import { bar as b } from './foo.js'" in js

    def test_from_import_mixed_aliases(self):
        """from foo import bar, baz as z -> import { bar, baz as z } from './foo.js'"""
        code = "from foo import bar, baz as z"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import { bar, baz as z } from './foo.js'" in js

    def test_from_import_star(self):
        """from foo import * -> import * as _foo from './foo.js'; Object.assign(...)"""
        code = "from foo import *"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import * as _foo from './foo.js'" in js
        assert "Object.assign(globalThis, _foo)" in js

    def test_from_import_nested_module(self):
        """from foo.bar import baz -> import { baz } from './foo/bar.js'"""
        code = "from foo.bar import baz"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import { baz } from './foo/bar.js'" in js

    def test_relative_import_current_dir(self):
        """from . import foo -> import * as foo from './foo.js'"""
        code = "from . import foo"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import * as foo from './foo.js'" in js

    def test_relative_import_parent_dir(self):
        """from .. import foo -> import * as foo from '../foo.js'"""
        code = "from .. import foo"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import * as foo from '../foo.js'" in js

    def test_relative_import_grandparent_dir(self):
        """from ... import foo -> import * as foo from '../../foo.js'"""
        code = "from ... import foo"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import * as foo from '../../foo.js'" in js

    def test_relative_import_from_submodule(self):
        """from .bar import baz -> import { baz } from './bar.js'"""
        code = "from .bar import baz"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import { baz } from './bar.js'" in js

    def test_relative_import_from_parent_submodule(self):
        """from ..bar import baz -> import { baz } from '../bar.js'"""
        code = "from ..bar import baz"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import { baz } from '../bar.js'" in js

    def test_future_import_ignored(self):
        """from __future__ import annotations should be silently ignored."""
        code = "from __future__ import annotations"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert js.strip() == ""

    def test_multiple_imports(self):
        """Multiple import statements should all be converted."""
        code = "import foo\nimport bar"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import * as foo from './foo.js'" in js
        assert "import * as bar from './bar.js'" in js


class TestModuleModeImportsDisabled:
    """Test that module_mode=False emits comments for imports."""

    def test_import_comment(self):
        """import foo should emit a comment when module_mode=False."""
        code = "import foo"
        js = py2js(code, include_stdlib=False, module_mode=False)
        assert "/* import foo */" in js
        assert "import * as" not in js

    def test_from_import_comment(self):
        """from foo import bar should emit a comment when module_mode=False."""
        code = "from foo import bar"
        js = py2js(code, include_stdlib=False, module_mode=False)
        assert "/* from foo import bar */" in js
        assert "import {" not in js
