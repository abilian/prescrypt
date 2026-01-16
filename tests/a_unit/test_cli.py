"""Tests for the CLI."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from prescrypt.main import compile_directory, compile_file, create_parser


class TestArgumentParser:
    """Test CLI argument parsing."""

    def test_parser_single_file(self):
        """Parse single file input."""
        parser = create_parser()
        args = parser.parse_args(["input.py"])
        assert args.input == Path("input.py")
        assert args.output is None
        assert args.module_mode is False

    def test_parser_with_output(self):
        """Parse with output option."""
        parser = create_parser()
        args = parser.parse_args(["input.py", "-o", "output.js"])
        assert args.input == Path("input.py")
        assert args.output == Path("output.js")

    def test_parser_module_mode(self):
        """Parse module mode flag."""
        parser = create_parser()
        args = parser.parse_args(["input.py", "-m"])
        assert args.module_mode is True

        args = parser.parse_args(["input.py", "--module-mode"])
        assert args.module_mode is True

    def test_parser_module_paths(self):
        """Parse module path options."""
        parser = create_parser()
        args = parser.parse_args(["input.py", "-M", "lib/", "-M", "vendor/"])
        assert args.module_paths == [Path("lib/"), Path("vendor/")]

    def test_parser_no_stdlib(self):
        """Parse no-stdlib flag."""
        parser = create_parser()
        args = parser.parse_args(["input.py", "--no-stdlib"])
        assert args.no_stdlib is True

    def test_parser_no_tree_shake(self):
        """Parse no-tree-shake flag."""
        parser = create_parser()
        args = parser.parse_args(["input.py", "--no-tree-shake"])
        assert args.no_tree_shake is True

    def test_parser_no_optimize(self):
        """Parse no-optimize flag."""
        parser = create_parser()
        args = parser.parse_args(["input.py", "--no-optimize"])
        assert args.no_optimize is True

    def test_parser_verbose(self):
        """Parse verbose flag."""
        parser = create_parser()
        args = parser.parse_args(["input.py", "-v"])
        assert args.verbose is True

    def test_parser_quiet(self):
        """Parse quiet flag."""
        parser = create_parser()
        args = parser.parse_args(["input.py", "-q"])
        assert args.quiet is True

    def test_parser_source_maps(self):
        """Parse source-maps flag."""
        parser = create_parser()
        args = parser.parse_args(["input.py", "-s"])
        assert args.source_maps is True

        args = parser.parse_args(["input.py", "--source-maps"])
        assert args.source_maps is True


class TestCompileFile:
    """Test single file compilation."""

    def test_compile_simple_file(self):
        """Compile a simple Python file."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_file = tmppath / "test.py"
            dst_file = tmppath / "test.js"

            src_file.write_text("x = 1 + 2")

            success = compile_file(src_file, dst_file, quiet=True)

            assert success is True
            assert dst_file.exists()
            js_content = dst_file.read_text()
            assert "x = " in js_content
            assert "3" in js_content  # Constant folding: 1 + 2 = 3

    def test_compile_with_module_mode(self):
        """Compile with module mode enabled."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_file = tmppath / "test.py"
            dst_file = tmppath / "test.js"

            src_file.write_text("def greet(name):\n    return name")

            success = compile_file(src_file, dst_file, module_mode=True, quiet=True)

            assert success is True
            js_content = dst_file.read_text()
            assert "export function greet" in js_content

    def test_compile_without_stdlib(self):
        """Compile without stdlib preamble."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_file = tmppath / "test.py"
            dst_file = tmppath / "test.js"

            src_file.write_text("x = 1")

            success = compile_file(src_file, dst_file, include_stdlib=False, quiet=True)

            assert success is True
            js_content = dst_file.read_text()
            # Should not have stdlib preamble
            assert "_pyfunc_" not in js_content

    def test_compile_error_handling(self):
        """Handle compilation errors gracefully."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_file = tmppath / "test.py"
            dst_file = tmppath / "test.js"

            # Write code with unsupported feature
            src_file.write_text("def gen():\n    yield 1")

            success = compile_file(src_file, dst_file, quiet=True)

            assert success is False
            assert not dst_file.exists()

    def test_compile_creates_parent_dirs(self):
        """Creates parent directories for output file."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_file = tmppath / "test.py"
            dst_file = tmppath / "out" / "sub" / "test.js"

            src_file.write_text("x = 1")

            success = compile_file(src_file, dst_file, include_stdlib=False, quiet=True)

            assert success is True
            assert dst_file.exists()

    def test_compile_with_source_maps(self):
        """Compile with source map generation."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_file = tmppath / "test.py"
            dst_file = tmppath / "test.js"
            map_file = tmppath / "test.js.map"

            src_file.write_text("x = 1\ny = 2\nprint(x + y)")

            success = compile_file(
                src_file, dst_file, include_stdlib=False, source_maps=True, quiet=True
            )

            assert success is True
            assert dst_file.exists()
            assert map_file.exists()

            # Check JS has sourceMappingURL comment
            js_content = dst_file.read_text()
            assert "//# sourceMappingURL=test.js.map" in js_content

    def test_source_map_content(self):
        """Verify source map JSON content."""
        import json

        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_file = tmppath / "test.py"
            dst_file = tmppath / "test.js"
            map_file = tmppath / "test.js.map"

            src_file.write_text("x = 1\ny = 2")

            success = compile_file(
                src_file, dst_file, include_stdlib=False, source_maps=True, quiet=True
            )

            assert success is True

            # Parse and verify source map
            map_content = json.loads(map_file.read_text())
            assert map_content["version"] == 3
            assert map_content["file"] == "test.js"
            assert "test.py" in map_content["sources"][0]
            assert "mappings" in map_content
            assert "sourcesContent" in map_content


class TestCompileDirectory:
    """Test directory compilation."""

    def test_compile_directory_basic(self):
        """Compile all files in a directory."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dst_dir = tmppath / "dist"
            src_dir.mkdir()

            # Create some Python files
            (src_dir / "main.py").write_text("x = 1")
            (src_dir / "utils.py").write_text("def helper():\n    pass")

            success_count, error_count = compile_directory(
                src_dir, dst_dir, include_stdlib=False, quiet=True
            )

            assert success_count == 2
            assert error_count == 0
            assert (dst_dir / "main.js").exists()
            assert (dst_dir / "utils.js").exists()

    def test_compile_directory_nested(self):
        """Compile nested directory structure."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dst_dir = tmppath / "dist"

            # Create nested structure
            (src_dir / "app").mkdir(parents=True)
            (src_dir / "app" / "models").mkdir()

            (src_dir / "main.py").write_text("x = 1")
            (src_dir / "app" / "routes.py").write_text("y = 2")
            (src_dir / "app" / "models" / "user.py").write_text("z = 3")

            success_count, error_count = compile_directory(
                src_dir, dst_dir, include_stdlib=False, quiet=True
            )

            assert success_count == 3
            assert error_count == 0
            assert (dst_dir / "main.js").exists()
            assert (dst_dir / "app" / "routes.js").exists()
            assert (dst_dir / "app" / "models" / "user.js").exists()

    def test_compile_directory_init_py(self):
        """Convert __init__.py to index.js."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dst_dir = tmppath / "dist"

            # Create package with __init__.py
            (src_dir / "mypackage").mkdir(parents=True)
            (src_dir / "mypackage" / "__init__.py").write_text("VERSION = '1.0'")
            (src_dir / "mypackage" / "core.py").write_text("x = 1")

            success_count, error_count = compile_directory(
                src_dir, dst_dir, include_stdlib=False, quiet=True
            )

            assert success_count == 2
            assert error_count == 0
            # __init__.py should become index.js
            assert (dst_dir / "mypackage" / "index.js").exists()
            assert not (dst_dir / "mypackage" / "__init__.js").exists()
            assert (dst_dir / "mypackage" / "core.js").exists()

    def test_compile_directory_skips_pycache(self):
        """Skip __pycache__ directories."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dst_dir = tmppath / "dist"

            src_dir.mkdir()
            (src_dir / "__pycache__").mkdir()
            (src_dir / "main.py").write_text("x = 1")
            (src_dir / "__pycache__" / "main.cpython-310.pyc").write_text("fake")

            success_count, error_count = compile_directory(
                src_dir, dst_dir, include_stdlib=False, quiet=True
            )

            assert success_count == 1
            assert error_count == 0
            assert not (dst_dir / "__pycache__").exists()

    def test_compile_directory_skips_hidden(self):
        """Skip hidden directories."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dst_dir = tmppath / "dist"

            src_dir.mkdir()
            (src_dir / ".hidden").mkdir()
            (src_dir / "main.py").write_text("x = 1")
            (src_dir / ".hidden" / "secret.py").write_text("y = 2")

            success_count, error_count = compile_directory(
                src_dir, dst_dir, include_stdlib=False, quiet=True
            )

            assert success_count == 1
            assert error_count == 0
            assert not (dst_dir / ".hidden").exists()

    def test_compile_directory_empty(self):
        """Handle empty directory."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dst_dir = tmppath / "dist"

            src_dir.mkdir()

            success_count, error_count = compile_directory(
                src_dir, dst_dir, include_stdlib=False, quiet=True
            )

            assert success_count == 0
            assert error_count == 0

    def test_compile_directory_with_errors(self):
        """Handle compilation errors in directory."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dst_dir = tmppath / "dist"

            src_dir.mkdir()
            (src_dir / "good.py").write_text("x = 1")
            (src_dir / "bad.py").write_text("def gen():\n    yield 1")  # Unsupported

            success_count, error_count = compile_directory(
                src_dir, dst_dir, include_stdlib=False, quiet=True
            )

            assert success_count == 1
            assert error_count == 1
            assert (dst_dir / "good.js").exists()
            assert not (dst_dir / "bad.js").exists()

    def test_compile_directory_module_mode(self):
        """Compile directory with module mode."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dst_dir = tmppath / "dist"

            src_dir.mkdir()
            (src_dir / "main.py").write_text("from utils import helper\nx = 1")
            (src_dir / "utils.py").write_text("def helper():\n    pass")

            success_count, error_count = compile_directory(
                src_dir, dst_dir, module_mode=True, include_stdlib=False, quiet=True
            )

            assert success_count == 2
            assert error_count == 0

            # Check main.js has ES6 import
            main_js = (dst_dir / "main.js").read_text()
            assert "import { helper } from './utils.js'" in main_js
            assert "export" in main_js

            # Check utils.js has export
            utils_js = (dst_dir / "utils.js").read_text()
            assert "export function helper" in utils_js
