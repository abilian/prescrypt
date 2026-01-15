from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_stmt
from prescrypt.codegen.utils import flatten
from prescrypt.front import ast


@gen_stmt.register
def _gen_pass(node: ast.Pass, codegen: CodeGen):
    return "/* pass */" + "\n"


@gen_stmt.register
def _gen_expr(node: ast.Expr, codegen: CodeGen):
    return flatten(codegen.gen_expr(node.value)) + ";\n"


@gen_stmt.register
def _gen_return(node: ast.Return, codegen: CodeGen):
    if node.value is None:
        return "return null;\n"
    js_value = flatten(codegen.gen_expr(node.value))
    return f"return {js_value};\n"


@gen_stmt.register
def _gen_global(node: ast.Global, codegen: CodeGen):
    # JavaScript doesn't have a global declaration - variables are either
    # local (let/const) or implicitly global. We emit a comment for clarity.
    names = ", ".join(node.names)
    return f"/* global {names} */\n"


@gen_stmt.register
def _gen_nonlocal(node: ast.Nonlocal, codegen: CodeGen):
    # JavaScript closures automatically capture outer variables.
    # We emit a comment for clarity.
    names = ", ".join(node.names)
    return f"/* nonlocal {names} */\n"


def _module_to_js_path(module: str, level: int = 0) -> str:
    """Convert a Python module path to a JavaScript file path.

    Args:
        module: Python module name (e.g., 'foo.bar.baz')
        level: Number of dots for relative imports (0=absolute, 1=current dir, 2=parent, etc.)

    Returns:
        JavaScript module path (e.g., './foo/bar/baz.js' or '../foo.js')
    """
    # Handle relative imports
    if level > 0:
        # level=1 means "from . import" -> "./"
        # level=2 means "from .. import" -> "../"
        prefix = "../" * (level - 1) if level > 1 else "./"
    else:
        # Absolute import - use relative path from current directory
        prefix = "./"

    # Convert module path (foo.bar) to file path (foo/bar.js)
    if module:
        path_parts = module.split(".")
        return prefix + "/".join(path_parts) + ".js"
    else:
        # Just relative import with no module (from . import foo)
        return prefix


@gen_stmt.register
def _gen_import_from(node: ast.ImportFrom, codegen: CodeGen):
    # Silently ignore "from __future__ import annotations" - it's the default behavior
    if node.module == "__future__":
        return ""

    # In module mode, generate ES6 imports
    if codegen.module_mode:
        module = node.module or ""
        level = node.level  # Number of dots for relative import

        # Handle "from . import foo" (relative import with no module)
        if not module and level > 0:
            # Each name becomes a separate import
            result = []
            prefix = "../" * (level - 1) if level > 1 else "./"
            for alias in node.names:
                name = alias.name
                local_name = alias.asname or name
                js_path = prefix + name + ".js"
                result.append(f"import * as {local_name} from '{js_path}';\n")
            return "".join(result)

        # Calculate JS path
        js_path = _module_to_js_path(module, level)

        # Build import statement
        names = []
        for alias in node.names:
            if alias.name == "*":
                # Star import: import * as _module from '...'; Object.assign(globalThis, _module);
                safe_name = "_" + module.replace(".", "_") if module else "_module"
                return (
                    f"import * as {safe_name} from '{js_path}';\n"
                    f"Object.assign(globalThis, {safe_name});\n"
                )
            name = alias.name
            local_name = alias.asname or name
            if name == local_name:
                names.append(name)
            else:
                names.append(f"{name} as {local_name}")

        return f"import {{ {', '.join(names)} }} from '{js_path}';\n"

    # Non-module mode: emit a comment
    names = ", ".join(alias.name for alias in node.names)
    module_str = node.module or "."
    return f"/* from {module_str} import {names} */\n"


@gen_stmt.register
def _gen_import(node: ast.Import, codegen: CodeGen):
    # In module mode, generate ES6 imports
    if codegen.module_mode:
        result = []
        for alias in node.names:
            module_name = alias.name
            # Use asname if provided, otherwise use the first part of the module name
            # e.g., "import foo.bar" -> local name is "foo"
            local_name = alias.asname or module_name.split(".")[0]

            # Convert module path to JS file path
            js_path = _module_to_js_path(module_name)

            result.append(f"import * as {local_name} from '{js_path}';\n")
        return "".join(result)

    # Non-module mode: emit a comment
    names = ", ".join(alias.name for alias in node.names)
    return f"/* import {names} */\n"
