from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_stmt
from prescrypt.codegen.utils import flatten
from prescrypt.front import ast


@gen_stmt.register
def _gen_pass(node: ast.Pass, codegen: CodeGen):
    return "/* pass */" + "\n"


@gen_stmt.register
def _gen_expr(node: ast.Expr, codegen: CodeGen):
    js_expr = flatten(codegen.gen_expr(node.value))
    # Flush any pending declarations (e.g., from walrus operator)
    pending_decls = codegen.flush_pending_declarations()
    if pending_decls:
        return pending_decls + js_expr + ";\n"
    return js_expr + ";\n"


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


@gen_stmt.register
def _gen_import_from(node: ast.ImportFrom, codegen: CodeGen):
    # Silently ignore "from __future__ import annotations" - it's the default behavior
    if node.module == "__future__":
        return ""

    # Handle "from js import X" - JS FFI imports
    # Each imported name becomes a direct JS global reference
    if node.module == "js":
        for alias in node.names:
            # Register the local name (or original name) as a direct JS global
            # This is different from 'import js' - the name IS the JS global, not a prefix
            local_name = alias.asname or alias.name
            codegen.add_js_ffi_global(local_name)
        return ""  # No output needed - names are used directly as JS globals

    # In module mode, generate ES6 imports
    if codegen.module_mode:
        module = node.module or ""
        level = node.level  # Number of dots for relative import

        # Handle "from . import foo" (relative import with no module)
        if not module and level > 0:
            # Each name becomes a separate import
            result = []
            for alias in node.names:
                name = alias.name
                local_name = alias.asname or name
                js_path = codegen.resolve_import_name(name, level)
                result.append(f"import * as {local_name} from '{js_path}';\n")
            return "".join(result)

        # Calculate JS path using resolver
        js_path = codegen.resolve_module(module, level)

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
    # Handle "import js" - the JS FFI module
    # This is a magic import that allows access to JavaScript globals
    # We suppress output and mark the module as FFI
    js_imports = [alias for alias in node.names if alias.name == "js"]
    other_imports = [alias for alias in node.names if alias.name != "js"]

    if js_imports:
        # Mark 'js' (or its alias) as an FFI module
        for alias in js_imports:
            local_name = alias.asname or "js"
            codegen.add_js_ffi_name(local_name)

    # If only js imports, return empty
    if not other_imports:
        return ""

    # In module mode, generate ES6 imports for non-js imports
    if codegen.module_mode:
        result = []
        for alias in other_imports:
            module_name = alias.name
            # Use asname if provided, otherwise use the first part of the module name
            # e.g., "import foo.bar" -> local name is "foo"
            local_name = alias.asname or module_name.split(".")[0]

            # Resolve module path to JS file path
            js_path = codegen.resolve_module(module_name)

            result.append(f"import * as {local_name} from '{js_path}';\n")
        return "".join(result)

    # Non-module mode: emit a comment
    names = ", ".join(alias.name for alias in other_imports)
    return f"/* import {names} */\n"
