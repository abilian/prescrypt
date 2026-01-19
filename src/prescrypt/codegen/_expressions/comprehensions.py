from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_expr
from prescrypt.codegen.utils import flatten, unify
from prescrypt.front import ast


@gen_expr.register
def gen_list_comp(node: ast.ListComp, codegen: CodeGen) -> list[str]:
    elt_node, generator_nodes = node.elt, node.generators

    codegen.push_ns("function", "<listcomp>")
    js_elt = flatten(codegen.gen_expr(elt_node))
    js_code = [
        "(function list_comprehension (iter0) {",
        "const res = []; res._is_list = true;",
    ]

    for iter, comprehension in enumerate(generator_nodes):
        assert isinstance(comprehension, ast.comprehension)
        cc = []
        # Get target (can be multiple vars)
        target_node = comprehension.target
        match target_node:
            case ast.Tuple(elts=target_elts):
                target = [flatten(codegen.gen_expr(t)) for t in target_elts]
            case _:
                target = [flatten(codegen.gen_expr(target_node))]

        # comprehension(target_node, iter_node, if_nodes)
        if iter > 0:  # first one is passed to function as an arg
            cc.append(f"let iter# = {flatten(codegen.gen_expr(comprehension.iter))};")

        cc.append(
            'if ((typeof iter# === "object") && '
            "!Array.isArray(iter#)) {iter# = Object.keys(iter#);}"
        )
        cc.append("for (let i#=0; i#<iter#.length; i#++) {")
        cc.append(_iterator_assign("iter#[i#]", *target))

        # Ifs
        if_nodes = comprehension.ifs
        if if_nodes:
            cc.append("if (!(")
            for if_node in if_nodes:
                cc += unify(codegen.gen_expr(if_node))
                cc.append("&&")
            cc.pop(-1)  # pop '&&'
            cc.append(")) {continue;}")

        # Insert code for this comprehension loop
        js_code.append(
            "".join(cc).replace("i#", f"i{iter:d}").replace("iter#", f"iter{iter:d}")
        )

    # Push result
    js_code.append("{res.push(%s);}" % js_elt)

    # End for
    js_code.append("}" * len(generator_nodes))

    # Finalize
    js_code.append("return res;})")  # end function
    iter0 = flatten(codegen.gen_expr(generator_nodes[0].iter))
    js_code.append(f".call(this, {iter0})")  # call funct with iter as 1st arg

    codegen.pop_ns()
    return js_code

    # todo: apply the apply(this) trick everywhere where we use a function


def _iterator_assign(val, *names):
    if len(names) == 1:
        return f"const {names[0]} = {val};"
    else:
        code = []
        for i, name in enumerate(names):
            code.append(f"const {name} = {val}[{i:d}];")
        return " ".join(code)


def _gen_loop_target(target_node, codegen: CodeGen) -> str:
    """Generate loop variable pattern for comprehension/generator.

    Handles simple names and tuple unpacking.
    """
    match target_node:
        case ast.Name(id=name):
            return name
        case ast.Tuple(elts=elts):
            parts = [_gen_loop_target(e, codegen) for e in elts]
            return "[" + ", ".join(parts) + "]"
        case _:
            from prescrypt.exceptions import JSError

            msg = (
                f"Unsupported loop target in generator expression: {type(target_node)}"
            )
            raise JSError(msg)


@gen_expr.register
def gen_generator_exp(node: ast.GeneratorExp, codegen: CodeGen) -> list[str]:
    """Generate generator expression using JS generator function.

    Python: (expr for target in iter if cond)
    JS: (function*() { for (let target of iter) if (cond) yield expr; })()

    This produces a lazy iterator, matching Python's generator semantics.
    """
    elt_node, generator_nodes = node.elt, node.generators

    codegen.push_ns("function", "<genexpr>")

    # Build the generator function body
    js_code = ["(function* () {"]

    for _gen_idx, comprehension in enumerate(generator_nodes):
        assert isinstance(comprehension, ast.comprehension)

        # Get target pattern
        loop_target = _gen_loop_target(comprehension.target, codegen)

        # Get iterable
        js_iter = flatten(codegen.gen_expr(comprehension.iter))

        # Use for...of for proper iteration (works with generators, arrays, etc.)
        js_code.append(f"for (let {loop_target} of {js_iter}) {{")

        # Add if conditions
        if_nodes = comprehension.ifs
        for if_node in if_nodes:
            js_condition = flatten(codegen.gen_expr(if_node))
            js_code.append(f"if (!({js_condition})) continue;")

    # Yield the element expression
    js_elt = flatten(codegen.gen_expr(elt_node))
    js_code.append(f"yield {js_elt};")

    # Close all for loops
    js_code.append("}" * len(generator_nodes))

    # Close generator function and invoke it
    js_code.append("})()")

    codegen.pop_ns()
    return js_code


@gen_expr.register
def gen_set_comp(node: ast.SetComp, codegen: CodeGen) -> list[str]:
    """Generate set comprehension: {x for x in items if condition}"""
    elt_node, generator_nodes = node.elt, node.generators

    codegen.push_ns("function", "<setcomp>")
    js_elt = flatten(codegen.gen_expr(elt_node))
    js_code = ["(function set_comprehension (iter0) {", "const res = new Set();"]

    for iter, comprehension in enumerate(generator_nodes):
        assert isinstance(comprehension, ast.comprehension)
        cc = []
        # Get target (can be multiple vars)
        target_node = comprehension.target
        match target_node:
            case ast.Tuple(elts=target_elts):
                target = [flatten(codegen.gen_expr(t)) for t in target_elts]
            case _:
                target = [flatten(codegen.gen_expr(target_node))]

        # comprehension(target_node, iter_node, if_nodes)
        if iter > 0:  # first one is passed to function as an arg
            cc.append(f"let iter# = {flatten(codegen.gen_expr(comprehension.iter))};")

        cc.append(
            'if ((typeof iter# === "object") && '
            "!Array.isArray(iter#)) {iter# = Object.keys(iter#);}"
        )
        cc.append("for (let i#=0; i#<iter#.length; i#++) {")
        cc.append(_iterator_assign("iter#[i#]", *target))

        # Ifs
        if_nodes = comprehension.ifs
        if if_nodes:
            cc.append("if (!(")
            for if_node in if_nodes:
                cc += unify(codegen.gen_expr(if_node))
                cc.append("&&")
            cc.pop(-1)  # pop '&&'
            cc.append(")) {continue;}")

        # Insert code for this comprehension loop
        js_code.append(
            "".join(cc).replace("i#", f"i{iter:d}").replace("iter#", f"iter{iter:d}")
        )

    # Add to set
    js_code.append("{res.add(%s);}" % js_elt)

    # End for
    js_code.append("}" * len(generator_nodes))

    # Finalize
    js_code.append("return res;})")  # end function
    iter0 = flatten(codegen.gen_expr(generator_nodes[0].iter))
    js_code.append(f".call(this, {iter0})")  # call funct with iter as 1st arg

    codegen.pop_ns()
    return js_code


@gen_expr.register
def gen_dict_comp(node: ast.DictComp, codegen: CodeGen) -> list[str]:
    """Generate dict comprehension: {k: v for k, v in items if condition}"""
    key_node, value_node, generator_nodes = node.key, node.value, node.generators

    codegen.push_ns("function", "<dictcomp>")
    js_key = flatten(codegen.gen_expr(key_node))
    js_value = flatten(codegen.gen_expr(value_node))
    js_code = ["(function dict_comprehension (iter0) {", "const res = {};"]

    for iter, comprehension in enumerate(generator_nodes):
        assert isinstance(comprehension, ast.comprehension)
        cc = []
        # Get target (can be multiple vars)
        target_node = comprehension.target
        match target_node:
            case ast.Tuple(elts=target_elts):
                target = [flatten(codegen.gen_expr(t)) for t in target_elts]
            case _:
                target = [flatten(codegen.gen_expr(target_node))]

        # comprehension(target_node, iter_node, if_nodes)
        if iter > 0:  # first one is passed to function as an arg
            cc.append(f"let iter# = {flatten(codegen.gen_expr(comprehension.iter))};")

        cc.append(
            'if ((typeof iter# === "object") && '
            "!Array.isArray(iter#)) {iter# = Object.keys(iter#);}"
        )
        cc.append("for (let i#=0; i#<iter#.length; i#++) {")
        cc.append(_iterator_assign("iter#[i#]", *target))

        # Ifs
        if_nodes = comprehension.ifs
        if if_nodes:
            cc.append("if (!(")
            for if_node in if_nodes:
                cc += unify(codegen.gen_expr(if_node))
                cc.append("&&")
            cc.pop(-1)  # pop '&&'
            cc.append(")) {continue;}")

        # Insert code for this comprehension loop
        js_code.append(
            "".join(cc).replace("i#", f"i{iter:d}").replace("iter#", f"iter{iter:d}")
        )

    # Set key-value pair
    js_code.append("{res[%s] = %s;}" % (js_key, js_value))

    # End for
    js_code.append("}" * len(generator_nodes))

    # Finalize
    js_code.append("return res;})")  # end function
    iter0 = flatten(codegen.gen_expr(generator_nodes[0].iter))
    js_code.append(f".call(this, {iter0})")  # call funct with iter as 1st arg

    codegen.pop_ns()
    return js_code
