"""Module bundling for Prescrypt.

Bundles multiple Python modules into a single JavaScript file with combined
tree-shaking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .codegen import CodeGen
from .compiler import Compiler, get_stdlib_js
from .front import ast
from .front.passes.binder import Binder
from .front.passes.constant_folder import fold_constants
from .front.passes.desugar import desugar
from .front.passes.resolver import ModuleResolver, ResolvedModule
from .front.passes.type_inference import TypeInference
from .stdlib_js import FUNCTION_PREFIX, METHOD_PREFIX


@dataclass
class ParsedModule:
    """A parsed Python module with its AST and metadata."""

    # Absolute path to the source file
    source_path: Path

    # The Python AST
    tree: ast.Module

    # Modules this module imports (resolved paths)
    imports: list[Path] = field(default_factory=list)

    # Generated JavaScript code (without stdlib)
    js_code: str = ""

    # Set of stdlib functions used
    used_std_functions: set[str] = field(default_factory=set)

    # Set of stdlib methods used
    used_std_methods: set[str] = field(default_factory=set)


class Bundler:
    """Bundles multiple Python modules into a single JavaScript file.

    Handles:
    - Recursive import resolution
    - Topological sorting by dependencies
    - Combined tree-shaking across all modules
    """

    def __init__(
        self,
        entry_file: Path,
        module_paths: list[Path] | None = None,
        function_prefix: str = FUNCTION_PREFIX,
        method_prefix: str = METHOD_PREFIX,
        optimize: bool = True,
        verbosity: int = 0,
    ):
        """Initialize the bundler.

        Args:
            entry_file: The main entry point Python file
            module_paths: Additional directories to search for modules
            function_prefix: Prefix for stdlib functions
            method_prefix: Prefix for stdlib methods
            optimize: Whether to apply compile-time optimizations
            verbosity: Verbosity level for output
        """
        self.entry_file = entry_file.resolve()
        self.module_paths = [p.resolve() for p in (module_paths or [])]
        self.function_prefix = function_prefix
        self.method_prefix = method_prefix
        self.optimize = optimize
        self.verbosity = verbosity

        # Parsed modules by absolute path
        self._modules: dict[Path, ParsedModule] = {}

        # Track all used stdlib items across modules
        self._all_used_functions: set[str] = set()
        self._all_used_methods: set[str] = set()

    def bundle(self) -> str:
        """Bundle the entry file and all its dependencies.

        Returns:
            Complete JavaScript code with stdlib preamble
        """
        # Phase 1: Parse entry file and collect all dependencies
        self._parse_recursive(self.entry_file)

        # Phase 2: Topologically sort modules by dependencies
        sorted_modules = self._topological_sort()

        if self.verbosity >= 1:
            print(f"Bundling {len(sorted_modules)} modules:")
            for mod in sorted_modules:
                print(f"  - {mod.source_path}")

        # Phase 3: Generate code for each module (in dependency order)
        for module in sorted_modules:
            self._generate_module_code(module)

        # Phase 4: Combine all module code
        code_parts = []
        for module in sorted_modules:
            # Add a comment header for each module
            rel_path = self._get_relative_path(module.source_path)
            code_parts.append(f"// === Module: {rel_path} ===\n")
            code_parts.append(module.js_code)
            code_parts.append("\n")

        combined_code = "".join(code_parts)

        # Phase 5: Generate combined tree-shaken stdlib
        preamble = self._generate_stdlib_preamble()

        return preamble + "\n" + combined_code

    def _parse_recursive(self, file_path: Path) -> ParsedModule:
        """Parse a module and recursively parse its imports.

        Args:
            file_path: Absolute path to the Python file

        Returns:
            ParsedModule with AST and import information
        """
        file_path = file_path.resolve()

        # Check if already parsed (avoid cycles)
        if file_path in self._modules:
            return self._modules[file_path]

        if self.verbosity >= 2:
            print(f"Parsing: {file_path}")

        # Read and parse the source
        source = file_path.read_text()
        tree = ast.parse(source)

        # Create module entry
        module = ParsedModule(source_path=file_path, tree=tree)
        self._modules[file_path] = module

        # Extract and resolve imports
        imports = self._extract_imports(tree, file_path.parent)
        for imp_path in imports:
            if imp_path is not None and imp_path.exists():
                module.imports.append(imp_path)
                # Recursively parse imported module
                self._parse_recursive(imp_path)

        return module

    def _extract_imports(self, tree: ast.Module, source_dir: Path) -> list[Path | None]:
        """Extract import statements and resolve to file paths.

        Args:
            tree: The AST of the module
            source_dir: Directory containing the source file

        Returns:
            List of resolved absolute paths (None for unresolvable imports)
        """
        resolver = ModuleResolver(
            source_dir=source_dir,
            module_paths=self.module_paths,
            verify_exists=True,
        )

        imports: list[Path | None] = []

        # Walk through all statements in the module
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "js":
                        continue  # Skip JS FFI imports
                    result = resolver.resolve(alias.name)
                    if result.found and result.source_path:
                        imports.append(result.source_path.resolve())

            elif isinstance(node, ast.ImportFrom):
                if node.module == "js" or node.module == "__future__":
                    continue  # Skip JS FFI and __future__ imports

                module = node.module or ""
                level = node.level

                if module:
                    result = resolver.resolve(module, level)
                    if result.found and result.source_path:
                        imports.append(result.source_path.resolve())
                else:
                    # 'from . import name' - each name is a separate module
                    for alias in node.names:
                        result = resolver.resolve_import_name(alias.name, level)
                        if result.found and result.source_path:
                            imports.append(result.source_path.resolve())

        return imports

    def _topological_sort(self) -> list[ParsedModule]:
        """Sort modules in dependency order (dependencies first).

        Returns:
            List of modules sorted so that a module appears after all
            modules it depends on.
        """
        sorted_list: list[ParsedModule] = []
        visited: set[Path] = set()
        visiting: set[Path] = set()  # For cycle detection

        def visit(path: Path) -> None:
            if path in visited:
                return
            if path in visiting:
                # Cycle detected - just skip (allow forward references)
                return

            visiting.add(path)
            module = self._modules.get(path)
            if module:
                for imp_path in module.imports:
                    visit(imp_path)
                sorted_list.append(module)

            visiting.discard(path)
            visited.add(path)

        # Visit all modules starting from entry file
        for path in self._modules:
            visit(path)

        return sorted_list

    def _generate_module_code(self, module: ParsedModule) -> None:
        """Generate JavaScript code for a module.

        This compiles the module without stdlib, collecting used stdlib items.

        Args:
            module: The parsed module to compile
        """
        tree = module.tree

        # Apply compiler passes
        tree = desugar(tree)
        if self.optimize:
            tree = fold_constants(tree)
        Binder().visit(tree)
        TypeInference().visit(tree)

        # Generate code with bundling mode (imports become comments)
        codegen = CodeGen(
            tree,
            self.function_prefix,
            self.method_prefix,
            module_mode=False,  # Not using ES6 imports
            source_dir=module.source_path.parent,
            module_paths=self.module_paths,
            source_map=None,
            bundle_mode=True,  # New flag to suppress import output
        )
        module.js_code = codegen.gen()

        # Collect used stdlib items
        module.used_std_functions = codegen.used_std_functions.copy()
        module.used_std_methods = codegen.used_std_methods.copy()

        # Accumulate across all modules
        self._all_used_functions.update(module.used_std_functions)
        self._all_used_methods.update(module.used_std_methods)

    def _generate_stdlib_preamble(self) -> str:
        """Generate tree-shaken stdlib for all bundled modules.

        Returns:
            JavaScript stdlib code with only the functions used by any module
        """
        compiler = Compiler()
        return compiler.get_partial_preamble(
            self._all_used_functions,
            self._all_used_methods,
            self.function_prefix,
            self.method_prefix,
        )

    def _get_relative_path(self, path: Path) -> str:
        """Get a relative path for display purposes."""
        try:
            return str(path.relative_to(self.entry_file.parent))
        except ValueError:
            return str(path)


def bundle_files(
    entry_file: Path,
    module_paths: list[Path] | None = None,
    function_prefix: str = FUNCTION_PREFIX,
    method_prefix: str = METHOD_PREFIX,
    optimize: bool = True,
    verbosity: int = 0,
) -> str:
    """Bundle a Python entry file and all its dependencies.

    Args:
        entry_file: Path to the main Python file
        module_paths: Additional directories to search for modules
        function_prefix: Prefix for stdlib functions
        method_prefix: Prefix for stdlib methods
        optimize: Whether to apply compile-time optimizations
        verbosity: Verbosity level

    Returns:
        Bundled JavaScript code with tree-shaken stdlib
    """
    bundler = Bundler(
        entry_file=entry_file,
        module_paths=module_paths,
        function_prefix=function_prefix,
        method_prefix=method_prefix,
        optimize=optimize,
        verbosity=verbosity,
    )
    return bundler.bundle()
