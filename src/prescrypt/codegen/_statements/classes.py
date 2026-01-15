from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_stmt
from prescrypt.codegen.utils import flatten, js_repr
from prescrypt.exceptions import JSError
from prescrypt.front import ast


@gen_stmt.register
def gen_classdef(node: ast.ClassDef, codegen: CodeGen):
    name_node = node.name
    base_nodes = node.bases
    keyword_nodes = node.keywords
    body_nodes = node.body
    decorator_nodes = node.decorator_list

    # Checks
    if len(base_nodes) > 1:
        raise JSError("Multiple inheritance not (yet) supported", node)
    if keyword_nodes:
        raise JSError("Metaclasses not supported", node)
    if decorator_nodes:
        raise JSError("Class decorators not supported", decorator_nodes[0])

    # Get base class (not the constructor)
    base_class = "Object"
    if base_nodes:
        base_class = flatten(codegen.gen_expr(base_nodes[0]))
    if not base_class.replace(".", "_").isalnum():
        raise JSError("Base classes must be simple names", base_nodes[0])
    elif base_class.lower() == "object":  # maybe Python "object"
        base_class = "Object"
    else:
        base_class += ".prototype"

    # Define function that acts as class constructor
    code = []
    docstring = ""
    code.append(
        make_class_definition(
            node.name,
            base_class,
            docstring,
            codegen.function_prefix,
            export=codegen.should_export(),
        )
    )
    codegen.call_std_function("op_instantiate", [])

    # Collect property definitions
    properties = _collect_properties(body_nodes)

    # Body ...
    class_name = node.name
    codegen.add_var(class_name)
    codegen.push_ns("class", class_name)

    for sub in body_nodes:
        # Skip property methods - they'll be emitted via Object.defineProperty
        if isinstance(sub, ast.FunctionDef) and _is_property_method(sub):
            continue
        code += codegen.gen_stmt(sub)

    # Emit property definitions
    for prop_name, prop_info in properties.items():
        code.append(
            _make_property_definition(class_name, prop_name, prop_info, codegen)
        )

    code.append("\n")
    codegen.pop_ns()

    return code


def _is_property_method(node: ast.FunctionDef) -> bool:
    """Check if a function has @property or @xxx.setter/deleter decorators."""
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name) and dec.id == "property":
            return True
        if isinstance(dec, ast.Attribute) and dec.attr in ("setter", "deleter"):
            return True
    return False


def _collect_properties(body_nodes: list) -> dict:
    """Collect property definitions from class body.

    Returns a dict mapping property name to {getter, setter, deleter} functions.
    """
    properties = {}

    for node in body_nodes:
        if not isinstance(node, ast.FunctionDef):
            continue

        for dec in node.decorator_list:
            if isinstance(dec, ast.Name) and dec.id == "property":
                # @property decorator - this is the getter
                prop_name = node.name
                if prop_name not in properties:
                    properties[prop_name] = {}
                properties[prop_name]["getter"] = node

            elif isinstance(dec, ast.Attribute) and dec.attr in ("setter", "deleter"):
                # @xxx.setter or @xxx.deleter
                if isinstance(dec.value, ast.Name):
                    prop_name = dec.value.id
                    if prop_name not in properties:
                        properties[prop_name] = {}
                    properties[prop_name][dec.attr] = node

    return properties


def _make_property_definition(
    class_name: str, prop_name: str, prop_info: dict, codegen
) -> str:
    """Generate Object.defineProperty() call for a property."""
    parts = []
    parts.append(
        f"Object.defineProperty({class_name}.prototype, {js_repr(prop_name)}, {{"
    )

    if "getter" in prop_info:
        getter_body = _gen_property_function_body(prop_info["getter"], codegen)
        parts.append(f"    get: function() {{ {getter_body} }},")

    if "setter" in prop_info:
        setter_node = prop_info["setter"]
        # Get the value parameter name (second param after self)
        if setter_node.args.args and len(setter_node.args.args) > 1:
            value_param = setter_node.args.args[1].arg
        else:
            value_param = "value"
        setter_body = _gen_property_function_body(setter_node, codegen)
        parts.append(f"    set: function({value_param}) {{ {setter_body} }},")

    if "deleter" in prop_info:
        deleter_body = _gen_property_function_body(prop_info["deleter"], codegen)
        parts.append(f"    delete: function() {{ {deleter_body} }},")

    parts.append("    configurable: true")
    parts.append("});")

    return "\n".join(parts)


def _gen_property_function_body(node: ast.FunctionDef, codegen) -> str:
    """Generate the body of a property getter/setter function."""
    # Push function namespace
    codegen.push_ns("function", node.name)

    # Use function's binding scope
    old_binding_scope = codegen._binding_scope
    codegen._binding_scope = getattr(node, "_scope", None)

    # Generate body statements
    body_parts = []
    for stmt in node.body:
        result = codegen.gen_stmt(stmt)
        if isinstance(result, list):
            body_parts.extend(result)
        else:
            body_parts.append(result)

    # Restore state
    codegen._binding_scope = old_binding_scope
    codegen.pop_ns()

    return " ".join(flatten(body_parts).split())


def make_class_definition(
    name, base="Object", docstring="", function_prefix="_pyfunc_", export=False
):
    """Get a list of lines that defines a class in JS.

    Used in the parser as well as by flexx.app.Component.
    """
    # Create constructor that works with or without 'new' keyword
    # ES6 export requires 'const' keyword: export const X = ...
    decl = "export const " if export else ""
    lines = [f"{decl}{name} = function () {{"]
    # Auto-instantiate if called without 'new'
    lines.append(f"    if (!(this instanceof {name})) {{")
    lines.append(f"        return new {name}(...arguments);")
    lines.append("    }")
    # for line in docstring.splitlines():
    #     code.append("    // " + line)
    lines.append(f"    {function_prefix}op_instantiate(this, arguments);")
    lines.append("}")

    if base != "Object":
        lines.append(f"{name}.prototype = Object.create({base});")
    lines.append(f"{name}.prototype._base_class = {base};")
    lines.append(f"{name}.prototype.__name__ = {js_repr(name.split('.')[-1])};")

    lines.append("")
    return "\n".join(lines)
