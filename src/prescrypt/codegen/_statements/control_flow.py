from __future__ import annotations

from prescrypt.exceptions import JSError
from prescrypt.front import ast

from prescrypt.codegen.main import CodeGen, gen_stmt
from prescrypt.codegen.utils import flatten


@gen_stmt.register
def gen_if(node: ast.If, codegen: CodeGen):
    test, body, orelse = node.test, node.body, node.orelse

    match test:
        # Ignore ``__name__ == '__main__'``, since it may be
        # used inside a PScript file for the compiling.
        case ast.Compare(ast.Name("__name__"), ast.Eq(), [ast.Constant("__main__")]):
            return []

        # if (
        #     True
        #     and isinstance(test, ast.Compare)
        #     and isinstance(test.left, ast.Name)
        #     and test.left.name == "__name__"
        # ):
        #     # Ignore ``__name__ == '__main__'``, since it may be
        #     # used inside a PScript file for the compiling.
        #     return []

        case ast.Call(ast.Name("this_is_js"), [], []):
            code = [codegen.lf("if ("), "true", ") ", "{ /* if this_is_js() */"]
            codegen.indent()
            for stmt in body:
                code += codegen.gen_stmt(stmt)
            codegen.dedent()
            code.append(codegen.lf("}"))
            return code

    # # Shortcut for this_is_js() cases, discarting the else to reduce code
    # if (
    #     True
    #     and isinstance(test, ast.Call)
    #     and isinstance(test.func, ast.Name)
    #     and test.func.id == "this_is_js"
    # ):
    #     code = [codegen.lf("if ("), "true", ") ", "{ /* if this_is_js() */"]
    #     codegen.indent()
    #     for stmt in body:
    #         code += codegen.gen_stmt(stmt)
    #     codegen.dedent()
    #     code.append(codegen.lf("}"))
    #     return code

    # Disable body if "not this_is_js()"
    if (
        True
        and isinstance(test, ast.UnaryOp)
        and type(test.op) == ast.Not()
        and isinstance(test.right, ast.Call)
        and isinstance(test.right.func, ast.Name)
        and test.right.func.id == "this_is_js"
    ):
        body = []

    code = [codegen.lf("if (")]  # first part (popped in elif parsing)
    code.append(codegen.gen_truthy(test))
    code.append(") {")

    codegen.indent()
    for stmt in body:
        code += codegen.gen_stmt(stmt)
    codegen.dedent()

    if orelse:
        if len(orelse) == 1 and isinstance(orelse[0], ast.If):
            code.append(codegen.lf("} else if ("))
            code += codegen.gen_stmt(orelse[0])[1:-1]  # skip first and last
        else:
            code.append(codegen.lf("} else {"))
            codegen.indent()
            for stmt in orelse:
                code += codegen.gen_stmt(stmt)
            codegen.dedent()

    code.append(codegen.lf("}"))  # last part (popped in elif parsing)

    return flatten(code)


@gen_stmt.register
def gen_break(node: ast.Break, codegen: CodeGen):
    return "break;" + "\n"


@gen_stmt.register
def gen_continue(node: ast.Continue, codegen: CodeGen):
    return "continue;" + "\n"


@gen_stmt.register
def gen_for(node: ast.For, codegen: CodeGen):
    """Generate a for loop.

    This is a simplified implementation that handles common cases:
    - for x in iterable
    - for i, x in enumerate(iterable)
    - for x in range(...)
    """
    target = node.target
    iter_node = node.iter
    body = node.body
    orelse = node.orelse

    # Get target variable name(s)
    if isinstance(target, ast.Name):
        target_names = [target.id]
    elif isinstance(target, ast.Tuple):
        target_names = [flatten(codegen.gen_expr(t)) for t in target.elts]
    else:
        raise JSError("Invalid iterator target in for-loop")

    # Generate the iterable expression
    js_iter = flatten(codegen.gen_expr(iter_node))

    # Create dummy variables for iteration
    d_seq = codegen.dummy("seq")
    d_iter = codegen.dummy("itr")

    code = []

    # Prepare variable to detect else
    if orelse:
        else_dummy = codegen.dummy("els")
        code.append(codegen.lf(f"let {else_dummy} = true;"))

    # Ensure our iterable is indeed iterable
    code.append(_make_iterable(codegen, js_iter, d_seq))

    # The loop
    code.append(
        codegen.lf(
            f"for (let {d_iter} = 0; {d_iter} < {d_seq}.length; {d_iter} += 1) {{"
        )
    )
    codegen.indent()

    # Assign loop variable(s)
    if len(target_names) == 1:
        codegen.add_var(target_names[0])
        code.append(codegen.lf(f"let {target_names[0]} = {d_seq}[{d_iter}];"))
    else:
        # Tuple unpacking
        d_target = codegen.dummy("tgt")
        code.append(codegen.lf(f"let {d_target} = {d_seq}[{d_iter}];"))
        for i, name in enumerate(target_names):
            codegen.add_var(name)
            code.append(codegen.lf(f"let {name} = {d_target}[{i}];"))

    # Generate body
    for stmt in body:
        code.append(codegen.gen_stmt(stmt))

    codegen.dedent()
    code.append(codegen.lf("}"))

    # Handle else clause
    if orelse:
        code.append(codegen.lf(f"if ({else_dummy}) {{"))
        codegen.indent()
        for stmt in orelse:
            code.append(codegen.gen_stmt(stmt))
        codegen.dedent()
        code.append(codegen.lf("}"))
        # Update all breaks to set the dummy
        for i, part in enumerate(code):
            if part == "break;":
                code[i] = f"{else_dummy} = false; break;"

    return flatten(code)


def _make_iterable(codegen: CodeGen, name1, name2, newlines=True):
    code = []
    lf = codegen.lf
    if not newlines:  # pragma: no cover
        lf = lambda x: x  # noqa

    if name1 != name2:
        code.append(lf(f"{name2} = {name1};"))
    code.append(
        lf(
            'if ((typeof %s === "object") && '
            "(!Array.isArray(%s))) {" % (name2, name2)
        )
    )
    code.append(f" {name2} = Object.keys({name2});")
    code.append("}")
    return "".join(code)


@gen_stmt.register
def gen_while(node: ast.While, codegen: CodeGen):
    test_node, body_nodes, orelse_nodes = node.test, node.body, node.orelse
    js_test = "".join(codegen.gen_expr(test_node))

    # Collect body and else-body
    js_for_body = []
    codegen.indent()
    js_for_body = [codegen.gen_stmt(n) for n in body_nodes]
    js_or_else = [codegen.gen_stmt(n) for n in orelse_nodes]
    codegen.dedent()

    # Init code
    code = []

    # Prepare variable to detect else
    if orelse_nodes:
        else_dummy = codegen.dummy("els")
        code.append(codegen.lf(f"{else_dummy} = true;"))

    # The loop itself
    code.append(codegen.lf("while (%s) {" % js_test))
    codegen.indent()
    code += js_for_body
    codegen.dedent()
    code.append(codegen.lf("}"))

    # Handle else
    if orelse_nodes:
        code.append(" if (%s) {" % else_dummy)
        code += js_or_else
        code.append(codegen.lf("}"))
        # Update all breaks to set the dummy. We overwrite the
        # "break;" so it will not be detected by a parent loop
        ii = [i for i, part in enumerate(code) if part == "break;"]
        for i in ii:
            code[i] = f"{else_dummy} = false; break;"

    return code


def _iterator_assign(val, *names):
    if len(names) == 1:
        return f"{names[0]} = {val};"
    else:
        code = []
        for i, name in enumerate(names):
            code.append("%s = %s[%i];" % (name, val, i))
        return " ".join(code)
