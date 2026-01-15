"""Prescrypt standard functions.

- Functions are declared as ... functions.

- Methods are written as methods (using this), but declared as functions,
    and then "apply()-ed" to the instance of interest.
    Declaring methods on Object is a bad idea (breaks Bokeh, jquery).
"""
from __future__ import annotations

import re
from pathlib import Path

FUNCTION_PREFIX = "_pyfunc_"
METHOD_PREFIX = "_pymeth_"


# ----- Functions & methods
class StdlibJs:
    functions: dict[str, str]
    methods: dict[str, str]
    function_deps: dict[str, set[str]]  # function -> set of function dependencies
    method_deps: dict[str, set[str]]  # function -> set of method dependencies

    def __init__(
        self,
        function_prefix: str = FUNCTION_PREFIX,
        method_prefix: str = METHOD_PREFIX,
    ):
        self.function_prefix = function_prefix
        self.method_prefix = method_prefix
        self.functions = self.get_functions("functions.js")
        self.methods = self.get_functions("methods.js")
        # Parse dependencies
        self.function_deps, self.method_deps = self._parse_all_dependencies()

    def get_functions(self, filename: str) -> dict[str, str]:
        result = {}
        path = Path(__file__).parent / "stdlibjs" / filename
        for block in path.read_text().split("// ---\n"):
            block = block.strip()
            if not block:
                continue
            m = re.match("^// (function|method): (.*)", block)
            name = m.group(2)

            # Remove export const
            block = block.replace(f"export const {name} = ", "")
            block = re.sub("(?m)^//.*$", "", block).strip()
            if block.endswith(";"):
                block = block[:-1]

            result[name] = block

        for key in result:
            result[key] = re.subn(
                r"METHOD_PREFIX(.+?)\(", r"METHOD_PREFIX\1.call(", result[key]
            )[0]
            result[key] = (
                result[key]
                .replace("KEY", key)
                .replace("FUNCTION_PREFIX", self.function_prefix)
                .replace("METHOD_PREFIX", self.method_prefix)
            )

        return result

    def _parse_all_dependencies(self) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
        """Parse dependencies for all functions and methods."""
        func_deps = {}
        meth_deps = {}

        # Parse function dependencies
        for name, code in self.functions.items():
            f_deps, m_deps = self._parse_dependencies(code)
            func_deps[name] = f_deps
            meth_deps[name] = m_deps

        # Parse method dependencies
        for name, code in self.methods.items():
            f_deps, m_deps = self._parse_dependencies(code)
            func_deps[name] = f_deps
            meth_deps[name] = m_deps

        return func_deps, meth_deps

    def _parse_dependencies(self, code: str) -> tuple[set[str], set[str]]:
        """Parse a stdlib code block to find dependencies on other stdlib functions/methods."""
        # Find function dependencies (look for _pyfunc_xxx patterns)
        func_pattern = re.escape(self.function_prefix) + r"(\w+)"
        func_deps = set(re.findall(func_pattern, code))

        # Find method dependencies (look for _pymeth_xxx patterns)
        meth_pattern = re.escape(self.method_prefix) + r"(\w+)"
        meth_deps = set(re.findall(meth_pattern, code))

        return func_deps, meth_deps

    def resolve_dependencies(
        self, func_names: set[str], method_names: set[str]
    ) -> tuple[set[str], set[str]]:
        """Resolve all dependencies for the given functions and methods.

        Returns the complete set of functions and methods needed, including
        all transitive dependencies.
        """
        all_funcs = set(func_names)
        all_methods = set(method_names)

        # Keep resolving until no new dependencies are found
        changed = True
        while changed:
            changed = False
            prev_funcs = len(all_funcs)
            prev_methods = len(all_methods)

            # Add dependencies for all known functions
            for name in list(all_funcs):
                if name in self.function_deps:
                    all_funcs.update(self.function_deps[name])
                if name in self.method_deps:
                    all_methods.update(self.method_deps[name])

            # Add dependencies for all known methods
            for name in list(all_methods):
                if name in self.function_deps:
                    all_funcs.update(self.function_deps[name])
                if name in self.method_deps:
                    all_methods.update(self.method_deps[name])

            # Check if anything changed
            if len(all_funcs) != prev_funcs or len(all_methods) != prev_methods:
                changed = True

        # Filter to only include functions/methods that actually exist
        all_funcs = {f for f in all_funcs if f in self.functions}
        all_methods = {m for m in all_methods if m in self.methods}

        return all_funcs, all_methods

    def get_full_std_lib(self, indent=0):
        """Get the code for the full Prescrypt standard library.

        The given indent specifies how many sets of 4 spaces to prepend. If
        the full stdlib is made available in JavaScript, multiple snippets
        of code can be transpiled without inlined stdlib parts by using
        ``py2js(..., inline_stdlib=False)``.
        """
        func_names = self.functions.keys()
        method_names = self.methods.keys()
        return self.get_partial_std_lib(func_names, method_names, indent)

    def get_partial_std_lib(self, func_names, method_names, indent=0):
        """Get the code for the Prescrypt standard library consisting of the given
        function and method names.

        The given indent specifies how many sets of 4 spaces to prepend.
        """
        func_prefix = "var " + self.function_prefix
        method_prefix = "var " + self.method_prefix
        lines = []

        for name in sorted(func_names):
            code = self.functions[name].strip()
            if "\n" not in code:
                code = code.rsplit("//", 1)[0].rstrip()  # strip comment from one-liners
            lines.append(f"{func_prefix}{name} = {code};")

        for name in sorted(method_names):
            code = self.methods[name].strip()
            lines.append(f"{method_prefix}{name} = {code};")

        code = "\n".join(lines)
        if indent:
            lines = ["    " * indent + line for line in code.splitlines()]
            code = "\n".join(lines)
        return code

    # Functions not covered by this lib:
    # isinstance, issubclass, print, len, max, min, callable, chr, ord

    # def get_std_info(self, code):
    #     """Given the JS code for a std function or method, determine the number of
    #     arguments, function_deps and method_deps."""
    #     _, _, nargs = code.splitlines()[0].partition("nargs:")
    #     nargs = [int(i.strip()) for i in nargs.strip().replace(",", " ").split(" ") if i]
    #
    #     # Collect dependencies on other funcs/methods
    #     sep = FUNCTION_PREFIX
    #     function_deps = [part.split("(")[0].strip() for part in code.split(sep)[1:]]
    #     sep = METHOD_PREFIX
    #     method_deps = [part.split(".")[0].strip() for part in code.split(sep)[1:]]
    #
    #     # Reduce and sort
    #     function_deps = sorted(set(function_deps))
    #     method_deps = sorted(set(method_deps))
    #
    #     # Filter
    #     function_deps = [dep for dep in function_deps if dep not in method_deps]
    #     function_deps = {dep for dep in function_deps if dep in FUNCTIONS}
    #     method_deps = {dep for dep in method_deps if dep in METHODS}
    #
    #     # Recurse
    #     for dep in list(function_deps):
    #         self._update_deps(FUNCTIONS[dep], function_deps, method_deps)
    #     for dep in list(method_deps):
    #         self._update_deps(METHODS[dep], function_deps, method_deps)
    #
    #     return nargs, sorted(function_deps), sorted(method_deps)
    #
    # def _update_deps(self, code, function_deps, method_deps):
    #     """Given the code of a dependency, recursively resolve additional
    #     dependencies."""
    #     # Collect deps
    #     sep = FUNCTION_PREFIX
    #     new_function_deps = [part.split("(")[0].strip() for part in code.split(sep)[1:]]
    #     sep = METHOD_PREFIX
    #     new_method_deps = [part.split(".")[0].strip() for part in code.split(sep)[1:]]
    #     # Update
    #     new_function_deps = set(new_function_deps).difference(function_deps)
    #     new_method_deps = set(new_method_deps).difference(method_deps)
    #     function_deps.update(new_function_deps)
    #     method_deps.update(new_method_deps)
    #     # Recurse
    #     for dep in new_function_deps:
    #         _update_deps(FUNCTIONS[dep], function_deps, method_deps)
    #     for dep in new_method_deps:
    #         _update_deps(METHODS[dep], function_deps, method_deps)
    #     return function_deps, method_deps

    # # todo: now that we have modules, we can have shorter/no prefixes, right?
    # # -> though maybe we use them for string replacement somewhere?
    # def get_all_std_names():
    #     """Get list if function names and methods names in std lib."""
    #     return (
    #         [FUNCTION_PREFIX + f for f in FUNCTIONS],
    #         [METHOD_PREFIX + f for f in METHODS],
    #     )
