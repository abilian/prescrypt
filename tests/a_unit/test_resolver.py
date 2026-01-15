"""Tests for module resolution."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from prescrypt.front.passes.resolver import ModuleResolver, ResolvedModule


class TestModuleResolverBasic:
    """Test basic module resolution without file system verification."""

    def test_absolute_import_simple(self):
        """import foo -> ./foo.js"""
        resolver = ModuleResolver(source_dir=Path("/src"))
        result = resolver.resolve("foo", level=0)
        assert result.js_path == "./foo.js"
        assert result.found is True

    def test_absolute_import_nested(self):
        """import foo.bar.baz -> ./foo/bar/baz.js"""
        resolver = ModuleResolver(source_dir=Path("/src"))
        result = resolver.resolve("foo.bar.baz", level=0)
        assert result.js_path == "./foo/bar/baz.js"

    def test_relative_import_current(self):
        """from . import foo (level=1) -> ./foo.js (empty module)"""
        resolver = ModuleResolver(source_dir=Path("/src"))
        result = resolver.resolve("", level=1)
        # Empty module returns just the prefix
        assert result.js_path == "./"

    def test_relative_import_current_with_module(self):
        """from .foo import bar (level=1, module='foo') -> ./foo.js"""
        resolver = ModuleResolver(source_dir=Path("/src"))
        result = resolver.resolve("foo", level=1)
        assert result.js_path == "./foo.js"

    def test_relative_import_parent(self):
        """from .. import foo (level=2, module='') -> ../"""
        resolver = ModuleResolver(source_dir=Path("/src/sub"))
        result = resolver.resolve("", level=2)
        assert result.js_path == "../"

    def test_relative_import_parent_with_module(self):
        """from ..foo import bar (level=2, module='foo') -> ../foo.js"""
        resolver = ModuleResolver(source_dir=Path("/src/sub"))
        result = resolver.resolve("foo", level=2)
        assert result.js_path == "../foo.js"

    def test_relative_import_grandparent(self):
        """from ... import foo (level=3) -> ../../"""
        resolver = ModuleResolver(source_dir=Path("/src/a/b"))
        result = resolver.resolve("", level=3)
        assert result.js_path == "../../"

    def test_relative_import_grandparent_with_module(self):
        """from ...foo import bar (level=3, module='foo') -> ../../foo.js"""
        resolver = ModuleResolver(source_dir=Path("/src/a/b"))
        result = resolver.resolve("foo", level=3)
        assert result.js_path == "../../foo.js"

    def test_relative_import_nested_module(self):
        """from .foo.bar import baz -> ./foo/bar.js"""
        resolver = ModuleResolver(source_dir=Path("/src"))
        result = resolver.resolve("foo.bar", level=1)
        assert result.js_path == "./foo/bar.js"


class TestModuleResolverImportName:
    """Test resolving individual import names (for 'from . import foo')."""

    def test_import_name_current(self):
        """from . import foo -> ./foo.js"""
        resolver = ModuleResolver(source_dir=Path("/src"))
        result = resolver.resolve_import_name("foo", level=1)
        assert result.js_path == "./foo.js"

    def test_import_name_parent(self):
        """from .. import foo -> ../foo.js"""
        resolver = ModuleResolver(source_dir=Path("/src/sub"))
        result = resolver.resolve_import_name("foo", level=2)
        assert result.js_path == "../foo.js"

    def test_import_name_grandparent(self):
        """from ... import foo -> ../../foo.js"""
        resolver = ModuleResolver(source_dir=Path("/src/a/b"))
        result = resolver.resolve_import_name("foo", level=3)
        assert result.js_path == "../../foo.js"


class TestModuleResolverWithFileSystem:
    """Test module resolution with file system verification."""

    def test_module_file_found(self):
        """Resolve to existing module file."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Create foo.py
            (tmppath / "foo.py").write_text("# module foo")

            resolver = ModuleResolver(source_dir=tmppath, verify_exists=True)
            result = resolver.resolve("foo", level=0)

            assert result.js_path == "./foo.js"
            assert result.found is True
            assert result.is_package is False
            assert result.source_path == tmppath / "foo.py"

    def test_package_found(self):
        """Resolve to existing package (__init__.py -> index.js)."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Create foo/__init__.py
            (tmppath / "foo").mkdir()
            (tmppath / "foo" / "__init__.py").write_text("# package foo")

            resolver = ModuleResolver(source_dir=tmppath, verify_exists=True)
            result = resolver.resolve("foo", level=0)

            assert result.js_path == "./foo/index.js"
            assert result.found is True
            assert result.is_package is True
            assert result.source_path == tmppath / "foo" / "__init__.py"

    def test_module_not_found(self):
        """Module not found returns found=False."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            resolver = ModuleResolver(source_dir=tmppath, verify_exists=True)
            result = resolver.resolve("nonexistent", level=0)

            assert result.js_path == "./nonexistent.js"
            assert result.found is False

    def test_nested_module_found(self):
        """Resolve nested module path."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Create foo/bar.py
            (tmppath / "foo").mkdir()
            (tmppath / "foo" / "bar.py").write_text("# module bar")

            resolver = ModuleResolver(source_dir=tmppath, verify_exists=True)
            result = resolver.resolve("foo.bar", level=0)

            assert result.js_path == "./foo/bar.js"
            assert result.found is True

    def test_module_paths_search(self):
        """Search in additional module paths."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            lib_dir = tmppath / "lib"
            src_dir.mkdir()
            lib_dir.mkdir()

            # Create module in lib directory
            (lib_dir / "mylib.py").write_text("# library module")

            resolver = ModuleResolver(
                source_dir=src_dir, module_paths=[lib_dir], verify_exists=True
            )
            result = resolver.resolve("mylib", level=0)

            # Should find it in lib_dir
            assert result.found is True


class TestModuleResolverIntegration:
    """Test module resolution through py2js."""

    def test_py2js_with_source_dir(self):
        """py2js accepts source_dir parameter."""
        from prescrypt.compiler import py2js

        code = "from foo import bar"
        js = py2js(
            code,
            include_stdlib=False,
            module_mode=True,
            source_dir=Path("/project/src"),
        )
        assert "import { bar } from './foo.js'" in js

    def test_py2js_default_source_dir(self):
        """py2js works without source_dir (defaults to cwd)."""
        from prescrypt.compiler import py2js

        code = "import foo"
        js = py2js(code, include_stdlib=False, module_mode=True)
        assert "import * as foo from './foo.js'" in js
