"""E2E tests for multi-file ES6 module compilation.

These tests compile multi-file Python projects to ES6 modules,
then run the generated JavaScript in Node.js to verify everything works.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from prescrypt.main import bundle_file, compile_directory


def run_node_module(dist_dir: Path, entry_point: str = "main.js") -> str:
    """Run a Node.js ES6 module and return stdout.

    Creates a package.json with type: module to enable ES6 imports.
    """
    # Create package.json for ES6 module support
    package_json = dist_dir / "package.json"
    package_json.write_text(json.dumps({"type": "module"}, indent=2))

    # Run the entry point
    result = subprocess.run(
        ["node", str(dist_dir / entry_point)],
        capture_output=True,
        text=True,
        cwd=str(dist_dir),
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Node.js failed:\n{result.stderr}")

    return result.stdout.strip()


class TestMultiFileModules:
    """Test multi-file project compilation and execution."""

    def test_simple_import(self):
        """Test simple import between two files."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dist_dir = tmppath / "dist"
            src_dir.mkdir()

            # Create source files
            (src_dir / "utils.py").write_text(
                """
def greet(name):
    return "Hello, " + name + "!"
"""
            )

            (src_dir / "main.py").write_text(
                """
from utils import greet

message = greet("World")
print(message)
"""
            )

            # Compile
            success, errors = compile_directory(
                src_dir, dist_dir, module_mode=True, quiet=True
            )
            assert success == 2
            assert errors == 0

            # Run and verify
            output = run_node_module(dist_dir)
            assert output == "Hello, World!"

    def test_multiple_imports(self):
        """Test importing from multiple modules."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dist_dir = tmppath / "dist"
            src_dir.mkdir()

            (src_dir / "math_utils.py").write_text(
                """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
"""
            )

            (src_dir / "string_utils.py").write_text(
                """
def uppercase(s):
    return s.upper()
"""
            )

            (src_dir / "main.py").write_text(
                """
from math_utils import add, multiply
from string_utils import uppercase

result = add(2, 3)
product = multiply(4, 5)
text = uppercase("hello")
print(result)
print(product)
print(text)
"""
            )

            success, errors = compile_directory(
                src_dir, dist_dir, module_mode=True, quiet=True
            )
            assert success == 3
            assert errors == 0

            output = run_node_module(dist_dir)
            assert output == "5\n20\nHELLO"

    def test_nested_imports(self):
        """Test imports in nested directory structure."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dist_dir = tmppath / "dist"

            # Create nested structure
            (src_dir / "lib").mkdir(parents=True)

            (src_dir / "lib" / "helpers.py").write_text(
                """
def format_name(first, last):
    return first + " " + last
"""
            )

            (src_dir / "main.py").write_text(
                """
from lib.helpers import format_name

name = format_name("John", "Doe")
print(name)
"""
            )

            success, errors = compile_directory(
                src_dir, dist_dir, module_mode=True, quiet=True
            )
            assert success == 2
            assert errors == 0

            output = run_node_module(dist_dir)
            assert output == "John Doe"

    def test_class_import(self):
        """Test importing and using classes across modules."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dist_dir = tmppath / "dist"
            src_dir.mkdir()

            (src_dir / "models.py").write_text(
                """
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        return "Hi, I am " + self.name
"""
            )

            (src_dir / "main.py").write_text(
                """
from models import Person

p = Person("Alice", 30)
print(p.name)
print(p.age)
print(p.greet())
"""
            )

            success, errors = compile_directory(
                src_dir, dist_dir, module_mode=True, quiet=True
            )
            assert success == 2
            assert errors == 0

            output = run_node_module(dist_dir)
            assert output == "Alice\n30\nHi, I am Alice"

    def test_constant_export(self):
        """Test exporting and importing constants."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dist_dir = tmppath / "dist"
            src_dir.mkdir()

            (src_dir / "config.py").write_text(
                """
VERSION = "1.0.0"
DEBUG = False
MAX_ITEMS = 100
"""
            )

            (src_dir / "main.py").write_text(
                """
from config import VERSION, MAX_ITEMS

print(VERSION)
print(MAX_ITEMS)
"""
            )

            success, errors = compile_directory(
                src_dir, dist_dir, module_mode=True, quiet=True
            )
            assert success == 2
            assert errors == 0

            output = run_node_module(dist_dir)
            assert output == "1.0.0\n100"

    def test_relative_import_same_dir(self):
        """Test relative imports within same directory."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dist_dir = tmppath / "dist"

            # Create package structure
            (src_dir / "mypackage").mkdir(parents=True)

            (src_dir / "mypackage" / "utils.py").write_text(
                """
def helper():
    return "helper called"
"""
            )

            (src_dir / "mypackage" / "core.py").write_text(
                """
from .utils import helper

def run():
    return helper()
"""
            )

            (src_dir / "main.py").write_text(
                """
from mypackage.core import run

result = run()
print(result)
"""
            )

            success, errors = compile_directory(
                src_dir, dist_dir, module_mode=True, quiet=True
            )
            assert success == 3
            assert errors == 0

            output = run_node_module(dist_dir)
            assert output == "helper called"

    def test_chained_imports(self):
        """Test chain of imports: A imports B, B imports C."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dist_dir = tmppath / "dist"
            src_dir.mkdir()

            (src_dir / "level3.py").write_text(
                """
def base_value():
    return 10
"""
            )

            (src_dir / "level2.py").write_text(
                """
from level3 import base_value

def doubled():
    return base_value() * 2
"""
            )

            (src_dir / "level1.py").write_text(
                """
from level2 import doubled

def tripled():
    return doubled() + base_value()

from level3 import base_value
"""
            )

            (src_dir / "main.py").write_text(
                """
from level1 import tripled

result = tripled()
print(result)
"""
            )

            success, errors = compile_directory(
                src_dir, dist_dir, module_mode=True, quiet=True
            )
            assert success == 4
            assert errors == 0

            output = run_node_module(dist_dir)
            # doubled() returns 20, base_value() returns 10, so tripled() = 30
            assert output == "30"

    def test_package_init_py(self):
        """Test __init__.py package initialization."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dist_dir = tmppath / "dist"

            # Create package with __init__.py
            (src_dir / "mylib").mkdir(parents=True)

            (src_dir / "mylib" / "__init__.py").write_text(
                """
VERSION = "2.0"

def get_version():
    return VERSION
"""
            )

            (src_dir / "main.py").write_text(
                """
from mylib import get_version, VERSION

print(VERSION)
print(get_version())
"""
            )

            success, errors = compile_directory(
                src_dir, dist_dir, module_mode=True, quiet=True
            )
            assert success == 2
            assert errors == 0

            # Verify __init__.py became index.js
            assert (dist_dir / "mylib" / "index.js").exists()
            assert not (dist_dir / "mylib" / "__init__.js").exists()

            output = run_node_module(dist_dir)
            assert output == "2.0\n2.0"

    def test_import_alias(self):
        """Test import with alias (as keyword)."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dist_dir = tmppath / "dist"
            src_dir.mkdir()

            (src_dir / "utilities.py").write_text(
                """
def long_function_name():
    return "result"
"""
            )

            (src_dir / "main.py").write_text(
                """
from utilities import long_function_name as fn

result = fn()
print(result)
"""
            )

            success, errors = compile_directory(
                src_dir, dist_dir, module_mode=True, quiet=True
            )
            assert success == 2
            assert errors == 0

            output = run_node_module(dist_dir)
            assert output == "result"

    def test_mixed_content(self):
        """Test file with functions, classes, and variables."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dist_dir = tmppath / "dist"
            src_dir.mkdir()

            (src_dir / "module.py").write_text(
                """
CONSTANT = 42

class MyClass:
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

def create_instance(val):
    return MyClass(val)
"""
            )

            (src_dir / "main.py").write_text(
                """
from module import CONSTANT, MyClass, create_instance

print(CONSTANT)
obj1 = MyClass(100)
print(obj1.get_value())
obj2 = create_instance(200)
print(obj2.get_value())
"""
            )

            success, errors = compile_directory(
                src_dir, dist_dir, module_mode=True, quiet=True
            )
            assert success == 2
            assert errors == 0

            output = run_node_module(dist_dir)
            assert output == "42\n100\n200"


class TestModuleEdgeCases:
    """Test edge cases in module compilation."""

    def test_empty_module(self):
        """Test importing from an empty module (just pass)."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dist_dir = tmppath / "dist"
            src_dir.mkdir()

            (src_dir / "empty.py").write_text("pass\n")

            (src_dir / "main.py").write_text(
                """
import empty
print("done")
"""
            )

            success, errors = compile_directory(
                src_dir, dist_dir, module_mode=True, quiet=True
            )
            assert success == 2
            assert errors == 0

            output = run_node_module(dist_dir)
            assert output == "done"

    def test_module_level_code(self):
        """Test that module-level code executes on import."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            dist_dir = tmppath / "dist"
            src_dir.mkdir()

            (src_dir / "module_with_init.py").write_text(
                """
print("module loading")
VALUE = 1 + 1
print("module loaded")
"""
            )

            (src_dir / "main.py").write_text(
                """
print("main start")
from module_with_init import VALUE
print("value is " + str(VALUE))
print("main end")
"""
            )

            success, errors = compile_directory(
                src_dir, dist_dir, module_mode=True, quiet=True
            )
            assert success == 2
            assert errors == 0

            output = run_node_module(dist_dir)
            lines = output.split("\n")
            # ES6 modules execute imports first
            assert "module loading" in output
            assert "module loaded" in output
            assert "main start" in output
            assert "value is 2" in output
            assert "main end" in output


def run_node_script(script_path: Path) -> str:
    """Run a Node.js script (not a module) and return stdout."""
    result = subprocess.run(
        ["node", str(script_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Node.js failed:\n{result.stderr}")

    return result.stdout.strip()


class TestBundling:
    """Test bundling multiple modules into a single file."""

    def test_simple_bundle(self):
        """Test bundling two files into one."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            src_dir.mkdir()

            (src_dir / "utils.py").write_text(
                """
def greet(name):
    return "Hello, " + name + "!"
"""
            )

            (src_dir / "main.py").write_text(
                """
from utils import greet

message = greet("World")
print(message)
"""
            )

            out_file = tmppath / "out.js"

            success = bundle_file(
                src_dir / "main.py",
                out_file,
                module_paths=[src_dir],
                quiet=True,
            )
            assert success

            output = run_node_script(out_file)
            assert output == "Hello, World!"

    def test_bundle_combined_tree_shake(self):
        """Test that stdlib is tree-shaken based on all bundled modules."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            src_dir.mkdir()

            # base.py uses create_dict (for empty dict)
            (src_dir / "base.py").write_text(
                """
def create_obj():
    return {}

class Animal:
    def __init__(self, name):
        self.name = name
"""
            )

            # main.py uses op_setitem (for dict assignment)
            (src_dir / "main.py").write_text(
                """
from base import Animal, create_obj

def run():
    obj = create_obj()
    obj["key"] = "value"
    animal = Animal("dog")
    return animal.name

print(run())
"""
            )

            out_file = tmppath / "out.js"

            success = bundle_file(
                src_dir / "main.py",
                out_file,
                module_paths=[src_dir],
                quiet=True,
            )
            assert success

            # Read the output and verify both stdlib functions are present
            js_code = out_file.read_text()
            assert "_pyfunc_create_dict" in js_code
            assert "_pyfunc_op_setitem" in js_code
            assert "_pyfunc_op_instantiate" in js_code

            output = run_node_script(out_file)
            assert output == "dog"

    def test_bundle_chained_imports(self):
        """Test bundling with chained imports: A imports B, B imports C."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            src_dir.mkdir()

            (src_dir / "level3.py").write_text(
                """
def base_value():
    return 10
"""
            )

            (src_dir / "level2.py").write_text(
                """
from level3 import base_value

def doubled():
    return base_value() * 2
"""
            )

            (src_dir / "main.py").write_text(
                """
from level2 import doubled
from level3 import base_value

result = doubled() + base_value()
print(result)
"""
            )

            out_file = tmppath / "out.js"

            success = bundle_file(
                src_dir / "main.py",
                out_file,
                module_paths=[src_dir],
                quiet=True,
            )
            assert success

            output = run_node_script(out_file)
            # doubled() returns 20, base_value() returns 10, result = 30
            assert output == "30"

    def test_bundle_class_inheritance(self):
        """Test bundling with class inheritance across modules."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"
            src_dir.mkdir()

            (src_dir / "base.py").write_text(
                """
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."
"""
            )

            (src_dir / "dog.py").write_text(
                """
from base import Animal

class Dog(Animal):
    def speak(self):
        return self.name + " says woof!"
"""
            )

            (src_dir / "main.py").write_text(
                """
from dog import Dog

dog = Dog("Buddy")
print(dog.speak())
"""
            )

            out_file = tmppath / "out.js"

            success = bundle_file(
                src_dir / "main.py",
                out_file,
                module_paths=[src_dir],
                quiet=True,
            )
            assert success

            output = run_node_script(out_file)
            assert output == "Buddy says woof!"

    def test_bundle_nested_packages(self):
        """Test bundling with nested package structure."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            src_dir = tmppath / "src"

            # Create nested structure
            (src_dir / "providers").mkdir(parents=True)

            (src_dir / "providers" / "base.py").write_text(
                """
class CIProvider:
    name = "base"

    def get_builds(self):
        return []
"""
            )

            (src_dir / "providers" / "github.py").write_text(
                """
from providers.base import CIProvider

class GitHubProvider(CIProvider):
    name = "github"

    def get_builds(self):
        return ["build1", "build2"]
"""
            )

            (src_dir / "main.py").write_text(
                """
from providers.github import GitHubProvider

provider = GitHubProvider()
print(provider.name)
builds = provider.get_builds()
print(len(builds))
"""
            )

            out_file = tmppath / "out.js"

            success = bundle_file(
                src_dir / "main.py",
                out_file,
                module_paths=[src_dir],
                quiet=True,
            )
            assert success

            output = run_node_script(out_file)
            assert output == "github\n2"
