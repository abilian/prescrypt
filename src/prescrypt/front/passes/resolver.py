"""Module resolution for Python imports.

Resolves Python module names to JavaScript file paths.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ResolvedModule:
    """Result of resolving a module import."""

    # The JavaScript path to use in the import statement (e.g., './foo/bar.js')
    js_path: str

    # The absolute path to the source .py file (if found)
    source_path: Path | None = None

    # Whether this is a package (directory with __init__.py)
    is_package: bool = False

    # Whether the module was found on disk
    found: bool = True


@dataclass
class ModuleResolver:
    """Resolves Python module imports to JavaScript paths.

    Handles:
    - Relative imports (from . import foo, from .. import bar)
    - Absolute imports (import foo, from foo.bar import baz)
    - Package resolution (__init__.py → index.js)
    """

    # The directory of the source file doing the import
    source_dir: Path

    # Additional directories to search for modules
    module_paths: list[Path] = field(default_factory=list)

    # Whether to verify that modules exist on disk
    verify_exists: bool = False

    def resolve(self, module: str, level: int = 0) -> ResolvedModule:
        """Resolve a module name to a JavaScript path.

        Args:
            module: The module name (e.g., 'foo.bar.baz')
            level: Number of dots for relative import (0=absolute, 1=current, 2=parent)

        Returns:
            ResolvedModule with the JavaScript path
        """
        if level > 0:
            return self._resolve_relative(module, level)
        else:
            return self._resolve_absolute(module)

    def _resolve_relative(self, module: str, level: int) -> ResolvedModule:
        """Resolve a relative import.

        Args:
            module: Module name (may be empty for 'from . import foo')
            level: Number of dots (1=current dir, 2=parent, etc.)
        """
        # Calculate the relative prefix
        # level=1 means "from . import" -> "./"
        # level=2 means "from .. import" -> "../"
        if level > 1:
            prefix = "../" * (level - 1)
        else:
            prefix = "./"

        if not module:
            # Just a relative prefix with no module (handled by caller for each name)
            return ResolvedModule(js_path=prefix, found=True)

        # Convert module path to file path
        path_parts = module.split(".")
        relative_path = "/".join(path_parts)

        # Check if it's a package or module
        if self.verify_exists:
            return self._resolve_with_verification(prefix, relative_path, path_parts)

        # Without verification, assume it's a module file
        js_path = f"{prefix}{relative_path}.js"
        return ResolvedModule(js_path=js_path, found=True)

    def _resolve_absolute(self, module: str) -> ResolvedModule:
        """Resolve an absolute import.

        Searches in:
        1. Same directory as source file
        2. Directories in module_paths
        """
        path_parts = module.split(".")
        relative_path = "/".join(path_parts)

        if self.verify_exists:
            # Try to find the module in search paths
            search_paths = [self.source_dir] + self.module_paths

            for search_dir in search_paths:
                result = self._find_module_in_dir(search_dir, path_parts)
                if result.found:
                    # Convert absolute path to relative JS path
                    return result

        # Without verification or if not found, use relative path from current dir
        js_path = f"./{relative_path}.js"
        return ResolvedModule(js_path=js_path, found=not self.verify_exists)

    def _resolve_with_verification(
        self, prefix: str, relative_path: str, path_parts: list[str]
    ) -> ResolvedModule:
        """Resolve a path and verify it exists on disk."""
        # Calculate the target directory based on prefix
        target_dir = self.source_dir
        if prefix.startswith("../"):
            up_count = prefix.count("../")
            for _ in range(up_count):
                target_dir = target_dir.parent

        return self._find_module_in_dir(target_dir, path_parts, prefix)

    def _find_module_in_dir(
        self, base_dir: Path, path_parts: list[str], prefix: str = "./"
    ) -> ResolvedModule:
        """Find a module in a directory.

        Checks for:
        1. module.py file
        2. module/__init__.py (package)
        """
        relative_path = "/".join(path_parts)

        # Check for module.py
        module_file = base_dir / "/".join(path_parts[:-1]) / f"{path_parts[-1]}.py"
        if len(path_parts) == 1:
            module_file = base_dir / f"{path_parts[0]}.py"

        if module_file.exists():
            js_path = f"{prefix}{relative_path}.js"
            return ResolvedModule(
                js_path=js_path, source_path=module_file, is_package=False, found=True
            )

        # Check for package (__init__.py)
        package_dir = base_dir / "/".join(path_parts)
        init_file = package_dir / "__init__.py"

        if init_file.exists():
            # Package imports use index.js (ES6 convention)
            js_path = f"{prefix}{relative_path}/index.js"
            return ResolvedModule(
                js_path=js_path, source_path=init_file, is_package=True, found=True
            )

        # Not found
        js_path = f"{prefix}{relative_path}.js"
        return ResolvedModule(js_path=js_path, found=False)

    def resolve_import_name(self, name: str, level: int = 0) -> ResolvedModule:
        """Resolve a single import name (for 'from . import name').

        This is used when level > 0 and module is empty.
        """
        if level > 1:
            prefix = "../" * (level - 1)
        else:
            prefix = "./"

        if self.verify_exists:
            # Try to find the module
            target_dir = self.source_dir
            if level > 1:
                for _ in range(level - 1):
                    target_dir = target_dir.parent

            return self._find_module_in_dir(target_dir, [name], prefix)

        # Without verification, assume it's a module file
        js_path = f"{prefix}{name}.js"
        return ResolvedModule(js_path=js_path, found=True)


def module_to_js_path(
    module: str,
    level: int = 0,
    source_dir: Path | None = None,
    module_paths: list[Path] | None = None,
    verify_exists: bool = False,
) -> str:
    """Convenience function to resolve a module to a JS path.

    Args:
        module: Python module name (e.g., 'foo.bar.baz')
        level: Number of dots for relative import
        source_dir: Directory of the importing file
        module_paths: Additional module search paths
        verify_exists: Whether to verify the module exists

    Returns:
        JavaScript import path (e.g., './foo/bar/baz.js')
    """
    if source_dir is None:
        source_dir = Path.cwd()

    resolver = ModuleResolver(
        source_dir=source_dir,
        module_paths=module_paths or [],
        verify_exists=verify_exists,
    )

    result = resolver.resolve(module, level)
    return result.js_path
