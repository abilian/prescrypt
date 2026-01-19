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
        return (
            f"{js_obj}.splice({js_start}, {js_obj}.length - {js_start}, ...{js_value});"
        )
    else:
        js_end = flatten(codegen.gen_expr(upper))
        # a[1:3] = [...] -> splice(1, 2, ...items)
        return f"{js_obj}.splice({js_start}, {js_end} - {js_start}, ...{js_value});"


@gen_stmt.register
def gen_assign(node: ast.Assign, codegen: CodeGen):
    """Variable assignment."""

    target_nodes, value_node = node.targets, node.value

    js_value = flatten(codegen.gen_expr(value_node))

    # Multiple targets: a = b = c = 3
    if len(target_nodes) > 1:
        return gen_multi_target_assign(target_nodes, js_value, codegen)

    target_node = target_nodes[0]

    # Tuple/List unpacking: a, b = 1, 2
    if isinstance(target_node, (ast.Tuple, ast.List)):
        return gen_unpack_assign(target_node.elts, js_value, codegen)

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
                export_prefix = "export " if codegen.should_export(id) else ""
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


def gen_multi_target_assign(
    targets: list[ast.expr], js_value: str, codegen: CodeGen
) -> str:
    """Handle multiple assignment: a = b = c = 3"""
    lines = []

    # Process targets right-to-left
    # a = b = c = 3 -> let c = 3; let b = c; let a = b;
    prev_name = None
    for target in reversed(targets):
        if not isinstance(target, ast.Name):
            msg = "Multiple assignment only supports simple names"
            raise JSError(msg)

        name = target.id

        # Check if already known BEFORE adding
        is_known = codegen.ns.is_known(name)
        codegen.add_var(name)

        export_prefix = "export " if codegen.should_export(name) else ""

        if is_known:
            # Already declared - just reassign
            if prev_name is None:
                lines.append(f"{name} = {js_value};")
            else:
                lines.append(f"{name} = {prev_name};")
        else:
            # New variable - declare it
            decl = codegen.get_declaration_kind(name)
            if prev_name is None:
                # First (rightmost) target gets the value
                if decl:
                    lines.append(f"{export_prefix}{decl} {name} = {js_value};")
                else:
                    lines.append(f"{name} = {js_value};")
            else:
                # Subsequent targets get the previous variable
                if decl:
                    lines.append(f"{export_prefix}{decl} {name} = {prev_name};")
                else:
                    lines.append(f"{name} = {prev_name};")

        prev_name = name

    return "\n".join(lines)


def gen_unpack_assign(targets: list[ast.expr], js_value: str, codegen: CodeGen) -> str:
    """Handle tuple/list unpacking: a, b = 1, 2"""
    # Check if all targets are simple names (no nested unpacking or starred)
    all_simple = all(isinstance(t, ast.Name) for t in targets)

    if all_simple:
        # Simple destructuring: let [a, b] = value;
        names = [t.id for t in targets]  # type: ignore

        # Check if any are already known BEFORE adding (for reassignment detection)
        any_known = any(codegen.ns.is_known(name) for name in names)

        # Now register them
        for name in names:
            codegen.add_var(name)

        pattern = "[" + ", ".join(names) + "]"
        if any_known:
            # Reassignment - no declaration keyword
            return f"{pattern} = {js_value};"
        else:
            # New variables - use let for flexibility
            return f"let {pattern} = {js_value};"

    # Handle nested unpacking and starred expressions
    return gen_complex_unpack(targets, js_value, codegen)


def _collect_target_names(targets: list[ast.expr]) -> list[str]:
    """Collect all variable names from destructuring targets."""
    names = []
    for t in targets:
        match t:
            case ast.Name(id=name):
                names.append(name)
            case ast.Tuple(elts=elts) | ast.List(elts=elts):
                names.extend(_collect_target_names(elts))
            case ast.Starred(value=ast.Name(id=name)):
                names.append(name)
            case ast.Starred(value=inner):
                if isinstance(inner, (ast.Tuple, ast.List)):
                    names.extend(_collect_target_names(inner.elts))
    return names


def gen_complex_unpack(targets: list[ast.expr], js_value: str, codegen: CodeGen) -> str:
    """Handle complex unpacking with nesting or starred expressions."""
    # Check for starred element
    starred_idx = None
    for i, t in enumerate(targets):
        if isinstance(t, ast.Starred):
            if starred_idx is not None:
                msg = "Multiple starred expressions in assignment"
                raise JSError(msg)
            starred_idx = i

    if starred_idx is not None:
        return gen_starred_unpack(targets, starred_idx, js_value, codegen)

    # Check if any target names are already known (for reassignment detection)
    all_names = _collect_target_names(targets)
    any_known = any(codegen.ns.is_known(name) for name in all_names)

    # Nested unpacking without starred
    pattern = gen_destructure_pattern(targets, codegen)
    if any_known:
        return f"{pattern} = {js_value};"
    return f"let {pattern} = {js_value};"


def gen_destructure_pattern(targets: list[ast.expr], codegen: CodeGen) -> str:
    """Generate JS destructuring pattern: [a, b, [c, d]]"""
    parts = []
    for t in targets:
        match t:
            case ast.Name(id=name):
                codegen.add_var(name)
                parts.append(name)
            case ast.Tuple(elts=elts) | ast.List(elts=elts):
                parts.append(gen_destructure_pattern(elts, codegen))
            case ast.Starred(value=ast.Name(id=name)):
                codegen.add_var(name)
                parts.append(f"...{name}")
            case _:
                msg = f"Cannot destructure into {t}"
                raise JSError(msg)
    return "[" + ", ".join(parts) + "]"


def gen_starred_unpack(
    targets: list[ast.expr], starred_idx: int, js_value: str, codegen: CodeGen
) -> str:
    """Handle starred unpacking: first, *rest, last = items"""
    n = len(targets)

    # Check if any target names are already known (for reassignment detection)
    all_names = _collect_target_names(targets)
    any_known = any(codegen.ns.is_known(name) for name in all_names)

    if starred_idx == n - 1:
        # Starred at end: [first, ...rest] works directly in JS
        pattern = gen_destructure_pattern(targets, codegen)
        if any_known:
            return f"{pattern} = {js_value};"
        return f"let {pattern} = {js_value};"

    # Starred not at end: need to split manually
    lines = []
    tmp = codegen.dummy("unpack")
    lines.append(f"let {tmp} = [...{js_value}];")

    # Elements after starred (pop from end)
    after_starred = targets[starred_idx + 1 :]
    for t in reversed(after_starred):
        if isinstance(t, ast.Name):
            name = t.id
            is_known = codegen.ns.is_known(name)
            codegen.add_var(name)
            if is_known:
                lines.append(f"{name} = {tmp}.pop();")
            else:
                lines.append(f"let {name} = {tmp}.pop();")
        else:
            msg = "Complex unpacking after starred not supported"
            raise JSError(msg)

    # Get starred variable name
    starred_target = targets[starred_idx]
    if isinstance(starred_target, ast.Starred) and isinstance(
        starred_target.value, ast.Name
    ):
        starred_name = starred_target.value.id
        starred_known = codegen.ns.is_known(starred_name)
        codegen.add_var(starred_name)
    else:
        msg = "Starred expression must be a simple name"
        raise JSError(msg)

    # Elements before starred
    before_starred = targets[:starred_idx]
    if before_starred:
        before_names = []
        before_any_known = False
        for t in before_starred:
            if isinstance(t, ast.Name):
                if codegen.ns.is_known(t.id):
                    before_any_known = True
                codegen.add_var(t.id)
                before_names.append(t.id)
            else:
                msg = "Complex unpacking before starred not supported"
                raise JSError(msg)
        pattern = ", ".join(before_names)
        if before_any_known or starred_known:
            lines.append(f"[{pattern}, ...{starred_name}] = {tmp};")
        else:
            lines.append(f"let [{pattern}, ...{starred_name}] = {tmp};")
    else:
        if starred_known:
            lines.append(f"{starred_name} = {tmp};")
        else:
            lines.append(f"let {starred_name} = {tmp};")

    return "\n".join(lines)

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
            export_prefix = "export " if codegen.should_export(name) else ""
            if decl:
                return (
                    f"{export_prefix}{decl} {codegen.with_prefix(name)} = {js_value};"
                )
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
            export_prefix = "export " if codegen.should_export(name) else ""
            return f"{export_prefix}let {codegen.with_prefix(name)};"


@gen_stmt.register
def gen_delete(node: ast.Delete, codegen: CodeGen) -> str:
    target_nodes = node.targets
    code = []
    for target in target_nodes:
        if isinstance(target, ast.Subscript):
            # del obj[key] - need different handling for list vs dict
            value = target.value
            slice_node = target.slice
            js_value = flatten(codegen.gen_expr(value))

            if isinstance(slice_node, ast.Slice):
                # del lst[:] or del lst[start:end] - clear or remove range
                lower = slice_node.lower
                upper = slice_node.upper
                if lower is None and upper is None:
                    # del lst[:] -> lst.splice(0, lst.length) (clear)
                    code.append(codegen.lf(f"{js_value}.splice(0, {js_value}.length);"))
                elif lower is None:
                    # del lst[:n] -> lst.splice(0, n)
                    js_upper = flatten(codegen.gen_expr(upper))
                    code.append(codegen.lf(f"{js_value}.splice(0, {js_upper});"))
                elif upper is None:
                    # del lst[n:] -> lst.splice(n)
                    js_lower = flatten(codegen.gen_expr(lower))
                    code.append(codegen.lf(f"{js_value}.splice({js_lower});"))
                else:
                    # del lst[start:end] -> lst.splice(start, end - start)
                    js_lower = flatten(codegen.gen_expr(lower))
                    js_upper = flatten(codegen.gen_expr(upper))
                    code.append(
                        codegen.lf(
                            f"{js_value}.splice({js_lower}, {js_upper} - {js_lower});"
                        )
                    )
            else:
                # del obj[key] or del lst[idx]
                # Use splice for arrays, delete for objects
                # At runtime, check if it's an array and use appropriate method
                js_key = flatten(codegen.gen_expr(slice_node))
                code.append(
                    codegen.lf(
                        f"if (Array.isArray({js_value})) {{ {js_value}.splice({js_key}, 1); }} "
                        f"else {{ delete {js_value}[{js_key}]; }}"
                    )
                )
        else:
            # del var or del obj.attr - use JS delete
            code.append(codegen.lf("delete "))
            code += codegen.gen_expr(target)
            code.append(";")
    return flatten(code)
