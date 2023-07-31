from prescrypt.ast import ast
from prescrypt.codegen.context import Context
from prescrypt.exceptions import JSError
from .stmt import gen_stmt


@gen_stmt.register
def gen_if(node: ast.If, ctx: Context):
    test, body, orelse = node.test, node.body, node.orelse

    if (
            True
            and isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name)
            and test.left.name == "__name__"
    ):
        # Ignore ``__name__ == '__main__'``, since it may be
        # used inside a PScript file for the compiling.
        return []

    # Shortcut for this_is_js() cases, discarting the else to reduce code
    if (
            True
            and isinstance(test, ast.Call)
            and isinstance(test.func, ast.Name)
            and test.func.id == "this_is_js"
    ):
        code = [ctx.lf("if ("), "true", ") ", "{ /* if this_is_js() */"]
        ctx._indent += 1
        for stmt in body:
            code += ctx.gen_stmt(stmt)
        ctx._indent -= 1
        code.append(ctx.lf("}"))
        return code

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

    code = [ctx.lf("if (")]  # first part (popped in elif parsing)
    code.append(ctx.gen_truthy(test))
    code.append(") {")
    ctx._indent += 1
    for stmt in body:
        code += ctx.gen_stmt(stmt)
    ctx._indent -= 1
    if orelse:
        if len(orelse) == 1 and isinstance(orelse[0], ast.If):
            code.append(ctx.lf("} else if ("))
            code += ctx.gen_stmt(orelse[0])[1:-1]  # skip first and last
        else:
            code.append(ctx.lf("} else {"))
            ctx._indent += 1
            for stmt in orelse:
                code += ctx.gen_stmt(stmt)
            ctx._indent -= 1
    code.append(ctx.lf("}"))  # last part (popped in elif parsing)
    return code


@gen_stmt.register
def gen_for(node: ast.For, ctx: Context):
    target, iter, body, orelse, type_comment = node.target, node.iter, node.body, node.orelse, node.type_comment

    # Note that enumerate, reversed, sorted, filter, map are handled in parser3

    METHODS = "keys", "values", "items"

    iter = None  # what to iterate over
    sure_is_dict = False  # flag to indicate that we're sure iter is a dict
    sure_is_range = False  # dito for range

    # First see if this for-loop is something that we support directly
    if isinstance(iter, ast.Call):
        f = iter.func_node
        if (
                isinstance(f, ast.Attribute)
                and not iter.arg_nodes
                and f.attr in METHODS
        ):
            sure_is_dict = f.attr
            iter = "".join(gen_expr(f.value_node))
        elif isinstance(f, ast.Name) and f.name in ("xrange", "range"):
            sure_is_range = [
                "".join(gen_expr(arg)) for arg in node.iter_node.arg_nodes
            ]
            iter = "range"  # stub to prevent the parsing of iter_node below

    # Otherwise we parse the iter
    if iter is None:
        iter = "".join(gen_expr(node.iter_node))

    # Get target
    if isinstance(target, ast.Name):
        target_name = [target.id]
        if sure_is_dict == "values":
            target.append(target_name[0])
        elif sure_is_dict == "items":
            raise JSError(
                "Iteration over a dict with .items() " "needs two iterators."
            )

    elif isinstance(target, ast.Tuple):
        target = ["".join(gen_expr(t)) for t in target.elts]
        if sure_is_dict:
            if not (sure_is_dict == "items" and len(target) == 2):
                raise JSError(
                    "Iteration over a dict needs one iterator, "
                    "or 2 when using .items()"
                )
        elif sure_is_range:
            raise JSError("Iterarion via range() needs one iterator.")

    else:
        raise JSError("Invalid iterator in for-loop")

    # Collect body and else-body
    for_body = []
    for_else = []
    ctx._indent += 1
    for n in node.body_nodes:
        for_body += self.parse(n)
    for n in node.else_nodes:
        for_else += ctx.parse(n)
    ctx._indent -= 1

    # Init code
    code = []

    # Prepare variable to detect else
    if node.else_nodes:
        else_dummy = ctx.dummy("els")
        code.append(ctx.lf(f"{else_dummy} = true;"))

    # Declare iteration variables if necessary
    for t in target:
        ctx.vars.add(t)

    if sure_is_range:  # Explicit iteration
        # Get range args
        nums = sure_is_range  # The range() arguments
        assert len(nums) in (1, 2, 3)
        if len(nums) == 1:
            start, end, step = "0", nums[0], "1"
        elif len(nums) == 2:
            start, end, step = nums[0], nums[1], "1"
        elif len(nums) == 3:
            start, end, step = nums[0], nums[1], nums[2]
        else:
            raise JSError("Invalid range() arguments")

        # Build for-loop in JS
        t = "for ({i} = {start}; {i} < {end}; {i} += {step})"
        if step.lstrip("+-").isdecimal() and float(step) < 0:
            t = t.replace("<", ">")
        assert len(target) == 1
        t = t.format(i=target[0], start=start, end=end, step=step) + " {"
        code.append(ctx.lf(t))
        ctx._indent += 1

    elif sure_is_dict:  # Enumeration over an object (i.e. a dict)
        # Create dummy vars
        d_seq = ctx.dummy("seq")
        code.append(ctx.lf(f"{d_seq} = {iter};"))
        # The loop
        code += ctx.lf(), "for (", target[0], " in ", d_seq, ") {"
        ctx._indent += 1
        code.append(
            ctx.lf(f"if (!{d_seq}.hasOwnProperty({target[0]})){{ continue; }}")
        )
        # Set second/alt iteration variable
        if len(target) > 1:
            code.append(ctx.lf(f"{target[1]} = {d_seq}[{target[0]}];"))

    else:  # Enumeration
        # We cannot know whether the thing to iterate over is an
        # array or a dict. We use a for-iterarion (otherwise we
        # cannot be sure of the element order for arrays). Before
        # running the loop, we test whether its an array. If its
        # not, we replace the sequence with the keys of that
        # sequence. Peformance for arrays should be good. For
        # objects probably slightly less.

        # Create dummy vars
        d_seq = ctx.dummy("seq")
        d_iter = ctx.dummy("itr")
        d_target = target[0] if (len(target) == 1) else ctx.dummy("tgt")

        # Ensure our iterable is indeed iterable
        code.append(ctx._make_iterable(iter, d_seq))

        # The loop
        code.append(
            ctx.lf(
                "for (%s = 0; %s < %s.length; %s += 1) {"
                % (d_iter, d_iter, d_seq, d_iter)
            )
        )
        ctx._indent += 1
        code.append(ctx.lf(f"{d_target} = {d_seq}[{d_iter}];"))
        if len(target) > 1:
            code.append(ctx.lf(ctx._iterator_assign(d_target, *target)))

    # The body of the loop
    code += for_body
    ctx._indent -= 1
    code.append(ctx.lf("}"))

    # Handle else
    if node.else_nodes:
        code.append(" if (%s) {" % else_dummy)
        code += for_else
        code.append(ctx.lf("}"))
        # Update all breaks to set the dummy. We overwrite the
        # "break;" so it will not be detected by a parent loop
        ii = [i for i, part in enumerate(code) if part == "break;"]
        for i in ii:
            code[i] = f"{else_dummy} = false; break;"

    return code


def _make_iterable(ctx, name1, name2, newlines=True):
    code = []
    lf = ctx.lf
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
def gen_while(node: ast.While, ctx: Context):
    test, body, orelse = node.test, node.body, node.orelse
    js_test = "".join(ctx.gen_expr(test))

    # Collect body and else-body
    for_body = []
    for_else = []
    ctx._indent += 1
    for n in body:
        for_body += ctx.gen_stmt(n)
    for n in orelse:
        for_else += ctx.gen_stmt(n)
    ctx._indent -= 1

    # Init code
    code = []

    # Prepare variable to detect else
    if orelse:
        else_dummy = ctx.dummy("els")
        code.append(ctx.lf(f"{else_dummy} = true;"))

    # The loop itself
    code.append(ctx.lf("while (%s) {" % js_test))
    ctx._indent += 1
    code += for_body
    ctx._indent -= 1
    code.append(ctx.lf("}"))

    # Handle else
    if orelse:
        code.append(" if (%s) {" % else_dummy)
        code += for_else
        code.append(ctx.lf("}"))
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
