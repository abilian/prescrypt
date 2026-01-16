from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_stmt
from prescrypt.codegen.utils import flatten
from prescrypt.exceptions import JSError
from prescrypt.front import ast


def gen_slice_assign(
    js_obj: str, slice_node: ast.Slice, js_value: str, codegen: CodeGen
) -> str:
    """Handle slice assignment: a[1:3] = [10, 20]"""
    lower = slice_node.lower
    upper = slice_node.upper
    step = slice_node.step

    # Slice assignment with step is not supported
    if step is not None:
        msg = "Slice assignment with step is not supported"
        raise JSError(msg)

    # Generate splice call: arr.splice(start, deleteCount, ...items)
    js_start = flatten(codegen.gen_expr(lower)) if lower else "0"
    if upper is None:
        # a[1:] = [...] -> splice from start to end
        return f"{js_obj}.splice({js_start}, {js_obj}.length - {js_start}, ...{js_value});"
    else:
        js_end = flatten(codegen.gen_expr(upper))
        # a[1:3] = [...] -> splice(1, 2, ...items)
        return f"{js_obj}.splice({js_start}, {js_end} - {js_start}, ...{js_value});"


@gen_stmt.register
def gen_assign(node: ast.Assign, codegen: CodeGen):
    """Variable assignment."""

    target_nodes, value_node = node.targets, node.value

    js_value = flatten(codegen.gen_expr(value_node))

    if len(target_nodes) > 1:
        msg = "Multiple assignment not (yet) supported"
        raise JSError(msg, node)

    target_node = target_nodes[0]

    match target_node:
        case ast.Name(id):
            if codegen.ns.type == "class":
                # Class-level attribute - no declaration keyword
                # Assign to both constructor and prototype so both access patterns work:
                # ClassName.attr (from static methods) and instance.attr (from instances)
                codegen.add_var(id)
                class_name = codegen.ns.name
                attr_name = id
                if attr_name.startswith("__") and not attr_name.endswith("__"):
                    attr_name = (
                        "_" + class_name + attr_name
                    )  # Double underscore name mangling
                return f"{class_name}.{attr_name} = {class_name}.prototype.{attr_name} = {js_value};"
            elif codegen.ns.is_known(id):
                # Already declared, just assign
                return f"{codegen.with_prefix(id)} = {js_value};"
            else:
                # First assignment - determine declaration keyword
                codegen.add_var(id)
                decl = codegen.get_declaration_kind(id)
                export_prefix = "export " if codegen.should_export() else ""
                if decl:
                    return (
                        f"{export_prefix}{decl} {codegen.with_prefix(id)} = {js_value};"
                    )
                else:
                    # No declaration needed (global/nonlocal)
                    return f"{codegen.with_prefix(id)} = {js_value};"

        case ast.Attribute(value, attr):
            js_target = flatten(codegen.gen_expr(target_node))
            return f"{js_target} = {js_value};"

        case ast.Subscript(value, slice_node):
            js_obj = flatten(codegen.gen_expr(value))

            # Handle slice assignment: a[1:3] = [10, 20]
            if isinstance(slice_node, ast.Slice):
                return gen_slice_assign(js_obj, slice_node, js_value, codegen)

            # Use op_setitem for regular index assignment
            js_key = flatten(codegen.gen_expr(slice_node))
            return f"{codegen.call_std_function('op_setitem', [js_obj, js_key, js_value])};"

        case _:
            msg = f"gen_assign not implemented for {node!r}"
            raise NotImplementedError(msg)

    #
    # code = [codegen.lf()]
    #
    # # Parse targets
    # tuple = []
    # dummy = ""
    # for target in target_nodes:
    #     var = flatten(codegen.gen_expr(target))
    #
    #     match target:
    #         case ast.Name(id):
    #             if "." in var:
    #                 code.append(var)
    #             else:
    #                 codegen.add_var(var)
    #                 code.append(codegen.with_prefix(var))
    #         case ast.Attribute(value, attr):
    #             code.append(var)
    #         case ast.Subscript(value, slice):
    #             code.append(var)
    #         case ast.Tuple(elts, ctx):
    #             dummy = codegen.dummy()
    #             code.append(dummy)
    #             tuple = elts
    #         case ast.List(elts, ctx):
    #             dummy = codegen.dummy()
    #             code.append(dummy)
    #             tuple = elts
    #         case _:
    #             raise JSError(f"Unsupported assignment type: {target}")
    #
    #     code.append(" = ")
    #
    # # Parse right side
    # if isinstance(value_node, ast.ListComp) and len(node.target_nodes) == 1:
    #     result_name = codegen.dummy()
    #     code.append(result_name + ";")
    #     lc_code = self.parse_ListComp_funtionless(node.value_node, result_name)
    #     code = [codegen.lf(), result_name + " = [];"] + lc_code + code
    # else:
    #     code += codegen.gen_expr(value_node)
    #     code.append(";")
    #
    # # Handle tuple unpacking
    # if tuple:
    #     code.append(codegen.lf())
    #     for i, x in enumerate(tuple):
    #         var = unify(codegen.gen_expr(x))
    #         if isinstance(x, ast.Name):  # but not when attr or index
    #             codegen.add_var(var)
    #         code.append("%s = %s[%i];" % (var, dummy, i))
    #
    # return code


@gen_stmt.register
def gen_annassign(node: ast.AnnAssign, codegen: CodeGen) -> str:
    """Annotated assignment: x: int = 5 or x: int"""
    target = node.target

    if not isinstance(target, ast.Name):
        msg = "Annotated assignment target must be a simple name"
        raise JSError(msg, node)

    name = target.id

    if node.value is not None:
        # Has value: x: int = 5
        js_value = flatten(codegen.gen_expr(node.value))

        if codegen.ns.type == "class":
            # Class-level attribute
            codegen.add_var(name)
            class_name = codegen.ns.name
            return f"{class_name}.{name} = {class_name}.prototype.{name} = {js_value};"
        elif codegen.ns.is_known(name):
            # Already declared
            return f"{codegen.with_prefix(name)} = {js_value};"
        else:
            # First assignment
            codegen.add_var(name)
            decl = codegen.get_declaration_kind(name)
            export_prefix = "export " if codegen.should_export() else ""
            if decl:
                return f"{export_prefix}{decl} {codegen.with_prefix(name)} = {js_value};"
            else:
                return f"{codegen.with_prefix(name)} = {js_value};"
    else:
        # No value: x: int (declaration only)
        if codegen.ns.type == "class":
            # Class-level declaration without value - skip
            return ""
        elif codegen.ns.is_known(name):
            # Already declared - skip
            return ""
        else:
            # Declare with let (will be assigned later)
            codegen.add_var(name)
            export_prefix = "export " if codegen.should_export() else ""
            return f"{export_prefix}let {codegen.with_prefix(name)};"


@gen_stmt.register
def gen_delete(node: ast.Delete, codegen: CodeGen) -> str:
    target_nodes = node.targets
    code = []
    for target in target_nodes:
        code.append(codegen.lf("delete "))
        code += codegen.gen_expr(target)
        code.append(";")
    return flatten(code)
