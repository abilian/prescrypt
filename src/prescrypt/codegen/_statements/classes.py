from __future__ import annotations

from prescrypt.exceptions import JSError
from prescrypt.front import ast
from prescrypt.stdlib_js import FUNCTION_PREFIX

from prescrypt.codegen.main import CodeGen, gen_stmt
from prescrypt.codegen.utils import flatten, js_repr


@gen_stmt.register
def gen_classdef(node: ast.ClassDef, codegen: CodeGen):
    name_node = node.name
    base_nodes = node.bases
    keyword_nodes = node.keywords
    body_nodes = node.body
    decorator_nodes = node.decorator_list

    # Checks
    if len(base_nodes) > 1:
        raise JSError("Multiple inheritance not (yet) supported.")
    if keyword_nodes:
        raise JSError("Metaclasses not supported.")
    if decorator_nodes:
        raise JSError("Class decorators not supported.")

    # Get base class (not the constructor)
    base_class = "Object"
    if base_nodes:
        base_class = flatten(codegen.gen_expr(base_nodes[0]))
    if not base_class.replace(".", "_").isalnum():
        raise JSError("Base classes must be simple names")
    elif base_class.lower() == "object":  # maybe Python "object"
        base_class = "Object"
    else:
        base_class += ".prototype"

    # Define function that acts as class constructor
    code = []
    docstring = ""
    # docstring = self.pop_docstring(node)
    # docstring = docstring if self._docstrings else ""
    code.append(make_class_definition(node.name, base_class, docstring))
    codegen.call_std_function("op_instantiate", [])

    # Body ...
    class_name = node.name
    codegen.add_var(class_name)
    codegen.push_ns("class", class_name)
    # self._seen_class_names.add(node.name)
    for sub in body_nodes:
        code += codegen.gen_stmt(sub)
    code.append("\n")
    codegen.pop_ns()
    # no need to declare variables, because they're prefixed

    return code


def make_class_definition(name, base="Object", docstring=""):
    """Get a list of lines that defines a class in JS.

    Used in the parser as well as by flexx.app.Component.
    """
    lines = [f"{name} = function () {{"]

    # for line in docstring.splitlines():
    #     code.append("    // " + line)
    lines.append(f"    {FUNCTION_PREFIX}op_instantiate(this, arguments);")
    lines.append("}")

    if base != "Object":
        lines.append(f"{name}.prototype = Object.create({base});")
    lines.append(f"{name}.prototype._base_class = {base};")
    lines.append(f"{name}.prototype.__name__ = {js_repr(name.split('.')[-1])};")

    lines.append("")
    return "\n".join(lines)
