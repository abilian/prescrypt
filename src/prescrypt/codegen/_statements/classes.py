from __future__ import annotations

import re
from dataclasses import dataclass as dc_dataclass

from prescrypt.codegen.main import CodeGen, gen_stmt
from prescrypt.codegen.utils import flatten, js_repr
from prescrypt.exceptions import JSError
from prescrypt.front import ast

# Regex to match valid JavaScript identifier (allows underscores and dots for namespaced names)
_VALID_BASE_CLASS_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_.]*$")


@dc_dataclass
class DataclassField:
    """Represents a field in a dataclass."""

    name: str
    has_default: bool
    default_value: ast.expr | None = None


def _is_dataclass(node: ast.ClassDef) -> bool:
    """Check if a class has a @dataclass decorator."""
    for dec in node.decorator_list:
        # @dataclass
        if isinstance(dec, ast.Name) and dec.id == "dataclass":
            return True
        # @dataclass()
        if isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name) and dec.func.id == "dataclass":
                return True
    return False


def _get_dataclass_options(node: ast.ClassDef) -> dict:
    """Extract dataclass options from decorator."""
    options = {"eq": True, "repr": True, "frozen": False}

    for dec in node.decorator_list:
        if isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name) and dec.func.id == "dataclass":
                for kw in dec.keywords:
                    if kw.arg in options:
                        if isinstance(kw.value, ast.Constant):
                            options[kw.arg] = kw.value.value
    return options


def _extract_dataclass_fields(node: ast.ClassDef) -> list[DataclassField]:
    """Extract field definitions from a dataclass body."""
    fields = []
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            field = DataclassField(
                name=stmt.target.id,
                has_default=stmt.value is not None,
                default_value=stmt.value,
            )
            fields.append(field)
    return fields


def _extract_slots(node: ast.ClassDef) -> list[str] | None:
    """Extract __slots__ from a class definition.

    Returns a list of slot names, or None if no __slots__ defined.
    """
    for stmt in node.body:
        # __slots__ = ['x', 'y']
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == "__slots__":
                    return _parse_slots_value(stmt.value)

        # __slots__: list[str] = ['x', 'y']
        if isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Name) and stmt.target.id == "__slots__":
                if stmt.value:
                    return _parse_slots_value(stmt.value)

    return None


def _parse_slots_value(node: ast.expr) -> list[str]:
    """Parse the value of __slots__ assignment."""
    slots = []

    if isinstance(node, (ast.List, ast.Tuple)):
        for elt in node.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                slots.append(elt.value)
            else:
                msg = "__slots__ must contain only string literals"
                raise JSError(msg, elt)
    elif isinstance(node, ast.Constant) and isinstance(node.value, str):
        # Single slot as string: __slots__ = 'x'
        slots.append(node.value)
    else:
        msg = "__slots__ must be a list, tuple, or string of attribute names"
        raise JSError(msg, node)

    return slots


def _is_slots_assignment(stmt: ast.stmt) -> bool:
    """Check if a statement is a __slots__ assignment."""
    if isinstance(stmt, ast.Assign):
        for target in stmt.targets:
            if isinstance(target, ast.Name) and target.id == "__slots__":
                return True
    if isinstance(stmt, ast.AnnAssign):
        if isinstance(stmt.target, ast.Name) and stmt.target.id == "__slots__":
            return True
    return False


@gen_stmt.register
def gen_classdef(node: ast.ClassDef, codegen: CodeGen):
    # Check for dataclass decorator
    if _is_dataclass(node):
        return gen_dataclass(node, codegen)

    name_node = node.name
    base_nodes = node.bases
    keyword_nodes = node.keywords
    body_nodes = node.body
    decorator_nodes = node.decorator_list

    # Checks
    if len(base_nodes) > 1:
        msg = "Multiple inheritance not (yet) supported"
        raise JSError(
            msg,
            node,
            hint="Use composition or mixins instead of multiple inheritance.",
        )
    if keyword_nodes:
        msg = "Metaclasses not supported"
        raise JSError(
            msg,
            node,
            hint="JavaScript doesn't have metaclasses. Consider using decorators or factory functions.",
        )

    # Get base class (not the constructor)
    base_class = "Object"
    if base_nodes:
        base_class = codegen.gen_expr_str(base_nodes[0])
    if not _VALID_BASE_CLASS_RE.match(base_class):
        msg = "Base classes must be simple names"
        raise JSError(msg, base_nodes[0])
    if base_class.lower() == "object":  # maybe Python "object"
        base_class = "Object"
    else:
        base_class += ".prototype"

    # Extract __slots__ if present
    slots = _extract_slots(node)

    # Define function that acts as class constructor
    code = []
    docstring = ""
    code.append(
        make_class_definition(
            node.name,
            base_class,
            docstring,
            codegen.function_prefix,
            export=codegen.should_export(node.name),
        )
    )
    codegen.call_std_function("op_instantiate", [])

    # Add __slots__ to prototype if defined
    if slots is not None:
        slots_js = "[" + ", ".join(js_repr(s) for s in slots) + "]"
        code.append(f"{node.name}.prototype.__slots__ = {slots_js};")

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
        # Skip __slots__ - already handled above
        if _is_slots_assignment(sub):
            continue
        code += codegen.gen_stmt(sub)

    # Emit property definitions
    for prop_name, prop_info in properties.items():
        code.append(
            _make_property_definition(class_name, prop_name, prop_info, codegen)
        )

    code.append("\n")
    codegen.pop_ns()

    # Apply decorators (in reverse order, innermost first)
    if decorator_nodes:
        for decorator in reversed(decorator_nodes):
            dec_code = codegen.gen_expr_str(decorator)
            code.append(f"{class_name} = {dec_code}({class_name});\n")

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
    """Generate Object.defineProperty() call for a property.

    Note: JavaScript property descriptors don't support a 'delete' handler.
    We store deleters as __deleter_propname__ methods on the prototype and
    the runtime op_delattr checks for them.
    """
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
    elif "getter" in prop_info:
        # Read-only property: add a setter that throws AttributeError
        parts.append(
            f"    set: function(v) {{ throw _pyfunc_op_error('AttributeError', "
            f"\"property '{prop_name}' has no setter\"); }},"
        )

    parts.append("    configurable: true")
    parts.append("});")

    result = "\n".join(parts)

    # Handle deleter separately - store as __deleter_propname__ method
    if "deleter" in prop_info:
        deleter_body = _gen_property_function_body(prop_info["deleter"], codegen)
        deleter_name = f"__deleter_{prop_name}__"
        result += f"\n{class_name}.prototype.{deleter_name} = function() {{ {deleter_body} }};"

    return result


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
    # Non-exported classes need 'var' to avoid strict mode errors
    decl = "export const " if export else "var "
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


def gen_dataclass(node: ast.ClassDef, codegen: CodeGen) -> list[str]:
    """Generate JavaScript code for a dataclass.

    Dataclasses auto-generate:
    - __init__ with all fields as parameters
    - __repr__ showing class name and all fields
    - __eq__ comparing all fields (if eq=True)
    """
    name = node.name
    options = _get_dataclass_options(node)
    fields = _extract_dataclass_fields(node)

    # Check for base class
    base_class = "Object"
    if node.bases:
        if len(node.bases) > 1:
            msg = "Dataclass with multiple inheritance not supported"
            raise JSError(msg, node)
        base_class = codegen.gen_expr_str(node.bases[0])
        if base_class.lower() == "object":
            base_class = "Object"
        else:
            base_class += ".prototype"

    code = []

    # Separate fields with and without defaults
    fields_no_default = [f for f in fields if not f.has_default]
    fields_with_default = [f for f in fields if f.has_default]

    # Generate parameter list (fields without defaults first)
    params = []
    for field in fields_no_default:
        params.append(field.name)
    for field in fields_with_default:
        default_js = codegen.gen_expr_str(field.default_value)
        params.append(f"{field.name} = {default_js}")

    params_str = ", ".join(params)

    # Generate constructor
    decl = "export const " if codegen.should_export(name) else "var "
    code.append(f"{decl}{name} = function ({params_str}) {{")
    code.append(f"    if (!(this instanceof {name})) {{")
    code.append(f"        return new {name}(...arguments);")
    code.append("    }")

    # Assign fields
    for field in fields:
        code.append(f"    this.{field.name} = {field.name};")

    # Freeze if frozen=True
    if options.get("frozen"):
        code.append("    Object.freeze(this);")

    code.append("};")

    # Set up prototype chain
    if base_class != "Object":
        code.append(f"{name}.prototype = Object.create({base_class});")
    code.append(f"{name}.prototype._base_class = {base_class};")
    code.append(f"{name}.prototype.__name__ = {js_repr(name)};")

    # Generate __repr__
    if options.get("repr", True):
        field_reprs = []
        for field in fields:
            field_reprs.append(f"'{field.name}=' + _pyfunc_repr(this.{field.name})")
        if field_reprs:
            separator = ' + ", " + '
            repr_body = f"'{name}(' + {separator.join(field_reprs)} + ')'"
        else:
            repr_body = f"'{name}()'"
        code.append(
            f"{name}.prototype.__repr__ = function() {{ return {repr_body}; }};"
        )
        codegen.call_std_function("repr", [])

    # Generate __eq__
    if options.get("eq", True):
        eq_checks = [f"other instanceof {name}"]
        for field in fields:
            eq_checks.append(
                f"_pyfunc_op_equals(this.{field.name}, other.{field.name})"
            )
        eq_body = " && ".join(eq_checks)
        code.append(
            f"{name}.prototype.__eq__ = function(other) {{ return {eq_body}; }};"
        )
        codegen.call_std_function("op_equals", [])

    # Generate __hash__ = None for mutable dataclasses (default)
    if not options.get("frozen"):
        code.append(f"{name}.prototype.__hash__ = null;")

    # Process other methods in the body (non-field definitions)
    codegen.add_var(name)
    codegen.push_ns("class", name)

    for stmt in node.body:
        # Skip annotated assignments (these are field definitions)
        if isinstance(stmt, ast.AnnAssign):
            continue
        # Skip docstrings
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            if isinstance(stmt.value.value, str):
                continue
        # Generate other methods
        code += codegen.gen_stmt(stmt)

    codegen.pop_ns()
    code.append("")

    return code
