from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_stmt
from prescrypt.codegen.utils import flatten
from prescrypt.exceptions import JSError
from prescrypt.front import ast


def _collect_assigned_names(stmts: list[ast.stmt]) -> set[str]:
    """Collect all variable names assigned in a list of statements.

    This is used to pre-declare variables before loop/block bodies,
    matching Python's function-level scoping semantics.
    """
    names: set[str] = set()

    def visit_expr(node):
        """Visit an expression that may contain walrus operator."""
        if isinstance(node, ast.NamedExpr):
            names.add(node.target.id)
            visit_expr(node.value)
        elif isinstance(node, (ast.List, ast.Tuple)):
            for elt in node.elts:
                visit_expr(elt)
        elif isinstance(node, ast.BinOp):
            visit_expr(node.left)
            visit_expr(node.right)
        elif isinstance(node, ast.Compare):
            visit_expr(node.left)
            for comp in node.comparators:
                visit_expr(comp)
        elif isinstance(node, ast.BoolOp):
            for val in node.values:
                visit_expr(val)
        elif isinstance(node, ast.IfExp):
            visit_expr(node.test)
            visit_expr(node.body)
            visit_expr(node.orelse)
        elif isinstance(node, ast.Call):
            visit_expr(node.func)
            for arg in node.args:
                visit_expr(arg)

    def visit_target(target):
        """Visit an assignment target to collect names."""
        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                visit_target(elt)
        # Subscript and Attribute don't create new names

    def visit_stmt(stmt):
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                visit_target(target)
            visit_expr(stmt.value)
        elif isinstance(stmt, ast.AnnAssign):
            if stmt.target:
                visit_target(stmt.target)
        elif isinstance(stmt, ast.AugAssign):
            visit_target(stmt.target)
        elif isinstance(stmt, (ast.For, ast.AsyncFor)):
            visit_target(stmt.target)
            for s in stmt.body:
                visit_stmt(s)
            for s in stmt.orelse:
                visit_stmt(s)
        elif isinstance(stmt, (ast.While, ast.If)):
            visit_expr(stmt.test)
            for s in stmt.body:
                visit_stmt(s)
            for s in stmt.orelse:
                visit_stmt(s)
        elif isinstance(stmt, (ast.With, ast.AsyncWith)):
            for item in stmt.items:
                if item.optional_vars:
                    visit_target(item.optional_vars)
            for s in stmt.body:
                visit_stmt(s)
        elif isinstance(stmt, ast.Try):
            for s in stmt.body:
                visit_stmt(s)
            for handler in stmt.handlers:
                if handler.name:
                    names.add(handler.name)
                for s in handler.body:
                    visit_stmt(s)
            for s in stmt.orelse:
                visit_stmt(s)
            for s in stmt.finalbody:
                visit_stmt(s)
        elif isinstance(stmt, ast.Match):
            # Match patterns can bind variables
            for case in stmt.cases:
                _collect_pattern_names(case.pattern, names)
                for s in case.body:
                    visit_stmt(s)
        elif isinstance(stmt, ast.Expr):
            visit_expr(stmt.value)

    for stmt in stmts:
        visit_stmt(stmt)

    return names


def _collect_pattern_names(pattern, names: set[str]) -> None:
    """Collect variable names from a match pattern."""
    if isinstance(pattern, ast.MatchAs):
        if pattern.name:
            names.add(pattern.name)
        if pattern.pattern:
            _collect_pattern_names(pattern.pattern, names)
    elif isinstance(pattern, (ast.MatchOr, ast.MatchSequence)):
        for p in pattern.patterns:
            _collect_pattern_names(p, names)
    elif isinstance(pattern, ast.MatchStar):
        if pattern.name:
            names.add(pattern.name)
    elif isinstance(pattern, ast.MatchMapping):
        for p in pattern.patterns:
            _collect_pattern_names(p, names)
        if pattern.rest:
            names.add(pattern.rest)
    elif isinstance(pattern, ast.MatchClass):
        for p in pattern.patterns:
            _collect_pattern_names(p, names)
        for p in pattern.kwd_patterns:
            _collect_pattern_names(p, names)


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

    # Generate test expression first to capture any pending declarations
    js_test = codegen.gen_truthy(test)
    pending_decls = codegen.flush_pending_declarations()

    code = []
    # Emit pending declarations before the if statement
    if pending_decls:
        code.append(pending_decls)

    code.append(codegen.lf("if ("))  # first part (popped in elif parsing)
    code.append(js_test)
    code.append(") {")

    codegen.indent()
    for stmt in body:
        code += codegen.gen_stmt(stmt)
    codegen.dedent()

    if orelse:
        if len(orelse) == 1 and isinstance(orelse[0], ast.If):
            # gen_stmt returns a list, flatten to string
            inner_if = flatten(codegen.gen_stmt(orelse[0]))
            # Remove leading whitespace and "if (" prefix
            inner_if = inner_if.lstrip()
            if inner_if.startswith("if ("):
                inner_if = inner_if[4:]  # Skip "if ("
            # Remove trailing "}" and whitespace
            inner_if = inner_if.rstrip()
            if inner_if.endswith("}"):
                inner_if = inner_if[:-1]
            code.append(codegen.lf("} else if ("))
            code.append(inner_if)
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

    Note: Loop variables are declared BEFORE the loop to match Python's
    function-level scoping (variables are accessible after the loop).
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
        msg = "Invalid iterator target in for-loop"
        raise JSError(msg, target)

    # Generate the iterable expression
    js_iter = flatten(codegen.gen_expr(iter_node))

    # Create dummy variables for iteration
    d_seq = codegen.dummy("seq")
    d_iter = codegen.dummy("itr")

    code = []

    # Collect all variables that will be assigned in the loop body
    # Pre-declare them to match Python's function-level scoping
    body_vars = _collect_assigned_names(body)
    if orelse:
        body_vars.update(_collect_assigned_names(orelse))

    # Declare loop variables and body variables BEFORE the loop
    all_vars = set(target_names) | body_vars
    for name in sorted(all_vars):  # Sort for deterministic output
        if not codegen.ns.is_known(name):
            codegen.add_var(name)
            code.append(codegen.lf(f"let {name};"))

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

    # Assign loop variable(s) - no declaration needed, already declared above
    if len(target_names) == 1:
        code.append(codegen.lf(f"{target_names[0]} = {d_seq}[{d_iter}];"))
    else:
        # Tuple unpacking
        d_target = codegen.dummy("tgt")
        code.append(codegen.lf(f"let {d_target} = {d_seq}[{d_iter}];"))
        for i, name in enumerate(target_names):
            code.append(codegen.lf(f"{name} = {d_target}[{i}];"))

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
            if "break;" in part:
                code[i] = part.replace("break;", f"{else_dummy} = false; break;")

    return flatten(code)


def _make_iterable(codegen: CodeGen, name1, name2, newlines=True):
    """Convert an expression to an iterable array.

    Handles:
    - Arrays: passed through
    - Plain objects: converted to Object.keys()
    - Iterators/generators: converted to array using spread
    """
    code = []
    lf = codegen.lf
    if not newlines:  # pragma: no cover
        lf = lambda x: x  # noqa

    if name1 != name2:
        code.append(lf(f"let {name2} = {name1};"))

    # Handle iterators/generators first (they have Symbol.iterator but not length)
    code.append(
        lf(
            f"if (!Array.isArray({name2}) && typeof {name2}[Symbol.iterator] === 'function') {{"
        )
    )
    code.append(f" {name2} = [...{name2}];")
    code.append("}")

    # Handle plain objects (convert to keys)
    code.append(
        lf(f'else if ((typeof {name2} === "object") && (!Array.isArray({name2}))) {{')
    )
    code.append(f" {name2} = Object.keys({name2});")
    code.append("}")

    return "".join(code)


@gen_stmt.register
def gen_while(node: ast.While, codegen: CodeGen):
    """Generate a while loop with Python-like scoping.

    Variables assigned inside the loop are pre-declared to be accessible
    after the loop ends.
    """
    test_node, body_nodes, orelse_nodes = node.test, node.body, node.orelse

    code = []

    # Pre-declare variables from body to match Python's function-level scoping
    body_vars = _collect_assigned_names(body_nodes)
    if orelse_nodes:
        body_vars.update(_collect_assigned_names(orelse_nodes))

    for name in sorted(body_vars):
        if not codegen.ns.is_known(name):
            codegen.add_var(name)
            code.append(codegen.lf(f"let {name};"))

    # Generate test expression with proper Python truthiness
    js_test = flatten(codegen.gen_truthy(test_node))

    # Flush any pending declarations (e.g., from walrus operator in condition)
    pending_decls = codegen.flush_pending_declarations()
    if pending_decls:
        code.append(pending_decls)

    # Prepare variable to detect else
    if orelse_nodes:
        else_dummy = codegen.dummy("els")
        code.append(codegen.lf(f"let {else_dummy} = true;"))

    # The loop itself
    code.append(codegen.lf("while (%s) {" % js_test))
    codegen.indent()
    for stmt in body_nodes:
        code.append(codegen.gen_stmt(stmt))
    codegen.dedent()
    code.append(codegen.lf("}"))

    # Handle else
    if orelse_nodes:
        code.append(" if (%s) {" % else_dummy)
        codegen.indent()
        for stmt in orelse_nodes:
            code.append(codegen.gen_stmt(stmt))
        codegen.dedent()
        code.append(codegen.lf("}"))
        # Update all breaks to set the dummy. We overwrite the
        # "break;" so it will not be detected by a parent loop
        for i, part in enumerate(code):
            if "break;" in part:
                code[i] = part.replace("break;", f"{else_dummy} = false; break;")

    return code


def _iterator_assign(val, *names):
    if len(names) == 1:
        return f"{names[0]} = {val};"
    else:
        code = []
        for i, name in enumerate(names):
            code.append("%s = %s[%i];" % (name, val, i))
        return " ".join(code)


@gen_stmt.register
def gen_with(node: ast.With, codegen: CodeGen):
    """Generate a with statement with context manager protocol support.

    Transpiles Python `with` to JavaScript try/finally with __enter__/__exit__:

        with open('file.txt') as f:
            x = f.read()

    becomes:

        const _ctx = open('file.txt');
        const f = _ctx.__enter__ ? _ctx.__enter__() : _ctx;
        try {
            const x = f.read();
        } finally {
            if (_ctx.__exit__) {
                _ctx.__exit__(null, null, null);
            } else if (_ctx && typeof _ctx.close === 'function') {
                _ctx.close();
            }
        }

    Supports:
    - Context manager protocol (__enter__/__exit__)
    - Fallback to .close() for file-like objects
    - Single context manager (multiple not yet supported)
    """
    items = node.items
    body = node.body

    if len(items) > 1:
        msg = "Multiple context managers in a single 'with' statement not yet supported"
        raise JSError(
            msg,
            node,
        )

    item = items[0]
    context_expr = item.context_expr
    optional_vars = item.optional_vars

    code = []

    # Generate the context expression
    js_context = flatten(codegen.gen_expr(context_expr))

    # Always create a context manager variable for cleanup
    ctx_var = codegen.dummy("ctx")
    code.append(codegen.lf(f"let {ctx_var} = {js_context};"))

    # If there's a binding variable (as x), call __enter__ or use context directly
    if optional_vars:
        if isinstance(optional_vars, ast.Name):
            var_name = optional_vars.id
            # Check if known BEFORE adding (for reassignment detection)
            is_known = codegen.ns.is_known(var_name)
            codegen.add_var(var_name)

            # Call __enter__ if it exists, otherwise use context directly
            enter_expr = f"{ctx_var}.__enter__ ? {ctx_var}.__enter__() : {ctx_var}"

            if is_known:
                # Already declared - just reassign
                code.append(codegen.lf(f"{var_name} = {enter_expr};"))
            else:
                decl = codegen.get_declaration_kind(var_name)
                if decl:
                    code.append(codegen.lf(f"{decl} {var_name} = {enter_expr};"))
                else:
                    code.append(codegen.lf(f"{var_name} = {enter_expr};"))
        else:
            msg = "Complex 'with' variable binding not supported"
            raise JSError(msg, optional_vars)
    else:
        # No binding variable, but still call __enter__ if it exists
        code.append(codegen.lf(f"if ({ctx_var}.__enter__) {ctx_var}.__enter__();"))

    # Generate try block
    code.append(codegen.lf("try {"))
    codegen.indent()
    for stmt in body:
        code.append(codegen.gen_stmt(stmt))
    codegen.dedent()
    code.append(codegen.lf("}"))

    # Generate finally block with cleanup
    code.append(" finally {")
    codegen.indent()
    # Call __exit__ if it exists, otherwise fall back to .close()
    code.append(
        codegen.lf(
            f"if ({ctx_var}.__exit__) {{ {ctx_var}.__exit__(null, null, null); }}"
        )
    )
    code.append(
        codegen.lf(
            f"else if ({ctx_var} && typeof {ctx_var}.close === 'function') "
            f"{ctx_var}.close();"
        )
    )
    codegen.dedent()
    code.append(codegen.lf("}"))

    return flatten(code)
