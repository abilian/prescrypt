"""PScript standard functions.

Functions are declared as ... functions. Methods are written as methods
(using this), but declared as functions, and then "apply()-ed" to the
instance of interest. Declaring methods on Object is a bad idea (breaks
Bokeh, jquery).
"""

import re
from pathlib import Path

FUNCTION_PREFIX = "_pyfunc_"
METHOD_PREFIX = "_pymeth_"


# ----- Functions & methods


def get_functions(filename: str) -> dict[str, str]:
    result = {}
    path = (Path(__file__).parent) / "stdlibjs" / filename
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
            .replace("FUNCTION_PREFIX", FUNCTION_PREFIX)
            .replace("METHOD_PREFIX", METHOD_PREFIX)
        )

    return result


FUNCTIONS = get_functions("functions.js")
METHODS = get_functions("methods.js")


# Functions not covered by this lib:
# isinstance, issubclass, print, len, max, min, callable, chr, ord


def get_std_info(code):
    """Given the JS code for a std function or method, determine the number of
    arguments, function_deps and method_deps."""
    _, _, nargs = code.splitlines()[0].partition("nargs:")
    nargs = [int(i.strip()) for i in nargs.strip().replace(",", " ").split(" ") if i]
    # Collect dependencies on other funcs/methods
    sep = FUNCTION_PREFIX
    function_deps = [part.split("(")[0].strip() for part in code.split(sep)[1:]]
    sep = METHOD_PREFIX
    method_deps = [part.split(".")[0].strip() for part in code.split(sep)[1:]]
    # Reduce and sort
    function_deps = sorted(set(function_deps))
    method_deps = sorted(set(method_deps))
    # Filter
    function_deps = [dep for dep in function_deps if dep not in method_deps]
    function_deps = {dep for dep in function_deps if dep in FUNCTIONS}
    method_deps = {dep for dep in method_deps if dep in METHODS}
    # Recurse
    for dep in list(function_deps):
        _update_deps(FUNCTIONS[dep], function_deps, method_deps)
    for dep in list(method_deps):
        _update_deps(METHODS[dep], function_deps, method_deps)

    return nargs, sorted(function_deps), sorted(method_deps)


def _update_deps(code, function_deps, method_deps):
    """Given the code of a dependency, recursively resolve additional
    dependencies."""
    # Collect deps
    sep = FUNCTION_PREFIX
    new_function_deps = [part.split("(")[0].strip() for part in code.split(sep)[1:]]
    sep = METHOD_PREFIX
    new_method_deps = [part.split(".")[0].strip() for part in code.split(sep)[1:]]
    # Update
    new_function_deps = set(new_function_deps).difference(function_deps)
    new_method_deps = set(new_method_deps).difference(method_deps)
    function_deps.update(new_function_deps)
    method_deps.update(new_method_deps)
    # Recurse
    for dep in new_function_deps:
        _update_deps(FUNCTIONS[dep], function_deps, method_deps)
    for dep in new_method_deps:
        _update_deps(METHODS[dep], function_deps, method_deps)
    return function_deps, method_deps


def get_partial_std_lib(
    func_names, method_names, indent=0, func_prefix=None, method_prefix=None
):
    """Get the code for the PScript standard library consisting of the given
    function and method names.

    The given indent specifies how many sets of 4 spaces to prepend.
    """
    func_prefix = "var " + FUNCTION_PREFIX if (func_prefix is None) else func_prefix
    method_prefix = "var " + METHOD_PREFIX if (method_prefix is None) else method_prefix
    lines = []
    for name in sorted(func_names):
        code = FUNCTIONS[name].strip()
        if "\n" not in code:
            code = code.rsplit("//", 1)[0].rstrip()  # strip comment from one-liners
        lines.append(f"{func_prefix}{name} = {code};")
    for name in sorted(method_names):
        code = METHODS[name].strip()
        # lines.append('Object.prototype.%s%s = %s;' % (METHOD_PREFIX, name, code))
        lines.append(f"{method_prefix}{name} = {code};")
    code = "\n".join(lines)
    if indent:
        lines = ["    " * indent + line for line in code.splitlines()]
        code = "\n".join(lines)
    return code


def get_full_std_lib(indent=0):
    """Get the code for the full PScript standard library.

    The given indent specifies how many sets of 4 spaces to prepend. If
    the full stdlib is made available in JavaScript, multiple snippets
    of code can be transpiled without inlined stdlib parts by using
    ``py2js(..., inline_stdlib=False)``.
    """
    return get_partial_std_lib(FUNCTIONS.keys(), METHODS.keys(), indent)


# todo: now that we have modules, we can have shorter/no prefixes, right?
# -> though maybe we use them for string replacement somewhere?
def get_all_std_names():
    """Get list if function names and methods names in std lib."""
    return (
        [FUNCTION_PREFIX + f for f in FUNCTIONS],
        [METHOD_PREFIX + f for f in METHODS],
    )
