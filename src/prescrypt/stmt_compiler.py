from . import stdlib_js
from .ast import ast
from .exceptions import JSError
from .expr_compiler import ExpressionCompiler
from .utils import flatten, js_repr, unify

RAW_DOC_WARNING = (
    "Function %s only has a docstring, which used to be "
    "intepreted as raw JS. Wrap a call to RawJS(...) around the "
    'docstring, or add "pass" to the function body to prevent '
    "this behavior."
)

JS_RESERVED_WORDS = set()


# https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Lexical_grammar
RESERVED = {
    "true",
    "false",
    "null",
    # Reserved keywords as of ECMAScript 6
    "break",
    "case",
    "catch",
    "class",
    "const",
    "continue",
    "debugger",
    "default",
    "delete",
    "do",
    "else",
    "export",
    "extends",
    "finally",
    "for",
    "function",
    "if",
    "import",
    "in",
    "instanceof",
    "new",
    "return",
    "super",
    "switch",
    "this",
    "throw",
    "try",
    "typeof",
    "var",
    "void",
    "while",
    "with",
    "yield",
    # Future reserved keywords
    "implements",
    "interface",
    "let",
    "package",
    "private",
    "protected",
    "public",
    "static",
    "enum",
    "await",  # only in module code
}


class StatementCompiler(ExpressionCompiler):
    """Parser that adds control flow, functions, classes, and exceptions.

    Must parse:

    + Pass
    - Global(identifier* names)
    - Nonlocal(identifier* names)

    - If(expr test, stmt* body, stmt* orelse)
    - While(expr test, stmt* body, stmt* orelse)
    - For(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
    - AsyncFor(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
    - Break
    - Continue

    - FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
        expr? returns, string? type_comment)
    - AsyncFunctionDef(identifier name, arguments args, stmt* body,
        expr* decorator_list, expr? returns, string? type_comment)
    - ClassDef(identifier name, expr* bases, keyword* keywords, stmt* body,
        expr* decorator_list)
    - Return(expr? value)

    - Delete(expr* targets)
    - Assign(expr* targets, expr value, string? type_comment)
    - AugAssign(expr target, operator op, expr value)
    - AnnAssign(expr target, expr annotation, expr? value, int simple)

    - With(withitem* items, stmt* body, string? type_comment)
    - AsyncWith(withitem* items, stmt* body, string? type_comment)
    - Match(expr subject, match_case* cases)
    - Raise(expr? exc, expr? cause)
    - Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
    - TryStar(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
    - Assert(expr test, expr? msg)
    - Import(alias* names)
    - ImportFrom(identifier? module, alias* names, int? level)
    - Expr(expr value)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._indent = 0
        self._dummy_counter = 0

    def gen_module(self, module: ast.Module):
        statements = module.body
        code = []
        for statement in statements:
            code += [self.gen_stmt(statement)]
        return "\n".join(code)

    def gen_stmt(self, node_or_nodes: ast.stmt | list[ast.stmt]) -> str:
        match node_or_nodes:
            case [*stmts]:
                return flatten([self.gen_stmt(node) for node in stmts])
            case ast.stmt():
                return flatten(self._gen_stmt(node_or_nodes))
            case _:
                raise JSError(f"Unexpected node type: {type(node_or_nodes)}")

    def _gen_stmt(self, node: ast.stmt) -> str | list:
        match node:
            case ast.Pass():
                return [self.lf("/* pass */")]
            case ast.Return(value_node):
                return [self.lf("return " + unify(self.gen_expr(value_node)) + ";")]

            # Exceptions
            case ast.Raise(exc, cause):
                return self.gen_raise(exc, cause)
            case ast.Assert(test_node, msg_node):
                return self.gen_assert(test_node, msg_node)
            case ast.Try(body, handlers, orelse, finalbody):
                return self.gen_try(body, handlers, orelse, finalbody)
            case ast.TryStar(body, handlers, orelse, finalbody):
                raise NotImplementedError("TryStar is not supported.")
            case ast.ExceptHandler(type, name, body):
                raise NotImplementedError("ExceptHandler is not supported.")

            # Control flow
            case ast.If(test, body, orelse):
                return self.gen_if(test, body, orelse)
            case ast.For(target, iter, body, orelse, type_comment):
                return self.gen_for(target, iter, body, orelse, type_comment)
            case ast.AsyncFor(target, iter_node, body, orelse, type_comment):
                raise NotImplementedError("AsyncFor is not supported.")
            case ast.While(test, body, orelse):
                return self.gen_while(test, body, orelse)
            case ast.Break():
                # Note that in parse_For, we detect breaks and modify them to
                # deal with the for-else clause
                return [self.lf("break;")]
            case ast.Continue():
                return [self.lf("continue;")]
            case ast.Match(subject_node, cases):
                return self.gen_match(subject_node, cases)

            case ast.With(items, body, type_comment):
                return self.gen_with(items, body, type_comment)
            case ast.AsyncWith(items, body, type_comment):
                raise NotImplementedError("AsyncWith is not supported.")
            case ast.FunctionDef(
                name, args, body, decorator_list, returns, type_comment
            ):
                return self.gen_function_def(
                    name, args, body, decorator_list, returns, type_comment
                )
            case ast.AsyncFunctionDef(
                name, args, body, decorator_list, returns, type_comment
            ):
                raise NotImplementedError("AsyncFunctionDef is not supported.")
            case ast.ClassDef(name, bases, keywords, body, decorator_list):
                return self.gen_class_def(name, bases, keywords, body, decorator_list)

            # Variables
            case ast.Delete(targets):
                return self.gen_delete(targets)
            case ast.Assign(targets, value_node, type_comment):
                return self.gen_assign(targets, value_node, type_comment)
            case ast.AugAssign(target, op, value_node):
                return self.gen_aug_assign(target, op, value_node)
            case ast.AnnAssign(target, annotation, value_node, simple):
                return self.gen_ann_assign(target, annotation, value_node, simple)

            case ast.Expr(value_node):
                return self.gen_expr(value_node)
            case ast.Import(names):
                return self.gen_import(names)
            case ast.ImportFrom(module, names, level):
                return self.gen_import_from(module, names, level)
            case ast.Global(names):
                return self.gen_global(names)
            case ast.Nonlocal(names):
                return self.gen_nonlocal(names)
            case _:
                raise NotImplementedError(f"Statement {node} is not supported.")

    def gen_with(self, items, body, type_comment):
        if len(items) != 1:
            raise JSError("With statement only supported for singleton contexts.")

        with_item: ast.expr = items[0]
        code = []

        context_name = unify(self.gen_expr(with_item.expr_node))

        # Store context expression in a variable?
        if "(" in context_name or "[" in context_name:
            ctx = self.dummy("context")
            code.append(self.lf(ctx + " = " + context_name + ";"))
            context_name = ctx

        err_name1 = "err_%i" % self._indent
        err_name2 = self.dummy("err")

        # Enter
        # for with_item in node.item_nodes: ...
        match with_item.as_node:
            case None:
                code.append(self.lf())
            case ast.Name():
                self.vars.add(with_item.as_node.name)
                code.append(self.lf(with_item.as_node.name + " = "))
            case ast.Attribute():
                code += [self.lf()] + self.parse(with_item.as_node) + [" = "]
            case _:
                raise JSError("The as-node in a with-statement must be a name or attr.")

        code += [context_name, ".__enter__();"]

        # Try
        code.append(self.lf("try {"))
        self._indent += 1
        for n in body:
            code += self.gen_stmt(n)
        self._indent -= 1
        code.append(self.lf("}"))

        # Exit
        code.append(f" catch({err_name1})  {{ {err_name2}={err_name1};")
        code.append(self.lf("} finally {"))
        self._indent += 1
        code.append(
            self.lf() + "if (%s) { "
            'if (!%s.__exit__(%s.name || "error", %s, null)) '
            "{ throw %s; }" % (err_name2, context_name, err_name2, err_name2, err_name2)
        )
        code.append(
            self.lf() + "} else { %s.__exit__(null, null, null); }" % context_name
        )
        self._indent -= 1
        code.append(self.lf("}"))
        return code

    # Control flow

    def gen_if(self, test, body, orelse):
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
            code = [self.lf("if ("), "true", ") ", "{ /* if this_is_js() */"]
            self._indent += 1
            for stmt in body:
                code += self.gen_stmt(stmt)
            self._indent -= 1
            code.append(self.lf("}"))
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

        code = [self.lf("if (")]  # first part (popped in elif parsing)
        code.append(self.gen_truthy(test))
        code.append(") {")
        self._indent += 1
        for stmt in body:
            code += self.gen_stmt(stmt)
        self._indent -= 1
        if orelse:
            if len(orelse) == 1 and isinstance(orelse[0], ast.If):
                code.append(self.lf("} else if ("))
                code += self.gen_stmt(orelse[0])[1:-1]  # skip first and last
            else:
                code.append(self.lf("} else {"))
                self._indent += 1
                for stmt in orelse:
                    code += self.gen_stmt(stmt)
                self._indent -= 1
        code.append(self.lf("}"))  # last part (popped in elif parsing)
        return code

    def gen_for(self, target, iter, body, orelse, type_comment):
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
                iter = "".join(self.parse(f.value_node))
            elif isinstance(f, ast.Name) and f.name in ("xrange", "range"):
                sure_is_range = [
                    "".join(self.parse(arg)) for arg in node.iter_node.arg_nodes
                ]
                iter = "range"  # stub to prevent the parsing of iter_node below

        # Otherwise we parse the iter
        if iter is None:
            iter = "".join(self.parse(node.iter_node))

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
            target = ["".join(self.gen_expr(t)) for t in target.elts]
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
        self._indent += 1
        for n in node.body_nodes:
            for_body += self.parse(n)
        for n in node.else_nodes:
            for_else += self.parse(n)
        self._indent -= 1

        # Init code
        code = []

        # Prepare variable to detect else
        if node.else_nodes:
            else_dummy = self.dummy("els")
            code.append(self.lf(f"{else_dummy} = true;"))

        # Declare iteration variables if necessary
        for t in target:
            self.vars.add(t)

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
            code.append(self.lf(t))
            self._indent += 1

        elif sure_is_dict:  # Enumeration over an object (i.e. a dict)
            # Create dummy vars
            d_seq = self.dummy("seq")
            code.append(self.lf(f"{d_seq} = {iter};"))
            # The loop
            code += self.lf(), "for (", target[0], " in ", d_seq, ") {"
            self._indent += 1
            code.append(
                self.lf(f"if (!{d_seq}.hasOwnProperty({target[0]})){{ continue; }}")
            )
            # Set second/alt iteration variable
            if len(target) > 1:
                code.append(self.lf(f"{target[1]} = {d_seq}[{target[0]}];"))

        else:  # Enumeration
            # We cannot know whether the thing to iterate over is an
            # array or a dict. We use a for-iterarion (otherwise we
            # cannot be sure of the element order for arrays). Before
            # running the loop, we test whether its an array. If its
            # not, we replace the sequence with the keys of that
            # sequence. Peformance for arrays should be good. For
            # objects probably slightly less.

            # Create dummy vars
            d_seq = self.dummy("seq")
            d_iter = self.dummy("itr")
            d_target = target[0] if (len(target) == 1) else self.dummy("tgt")

            # Ensure our iterable is indeed iterable
            code.append(self._make_iterable(iter, d_seq))

            # The loop
            code.append(
                self.lf(
                    "for (%s = 0; %s < %s.length; %s += 1) {"
                    % (d_iter, d_iter, d_seq, d_iter)
                )
            )
            self._indent += 1
            code.append(self.lf(f"{d_target} = {d_seq}[{d_iter}];"))
            if len(target) > 1:
                code.append(self.lf(self._iterator_assign(d_target, *target)))

        # The body of the loop
        code += for_body
        self._indent -= 1
        code.append(self.lf("}"))

        # Handle else
        if node.else_nodes:
            code.append(" if (%s) {" % else_dummy)
            code += for_else
            code.append(self.lf("}"))
            # Update all breaks to set the dummy. We overwrite the
            # "break;" so it will not be detected by a parent loop
            ii = [i for i, part in enumerate(code) if part == "break;"]
            for i in ii:
                code[i] = f"{else_dummy} = false; break;"

        return code

    def _make_iterable(self, name1, name2, newlines=True):
        code = []
        lf = self.lf
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

    def gen_while(self, test, body, orelse):
        js_test = "".join(self.gen_expr(test))

        # Collect body and else-body
        for_body = []
        for_else = []
        self._indent += 1
        for n in body:
            for_body += self.gen_stmt(n)
        for n in orelse:
            for_else += self.gen_stmt(n)
        self._indent -= 1

        # Init code
        code = []

        # Prepare variable to detect else
        if orelse:
            else_dummy = self.dummy("els")
            code.append(self.lf(f"{else_dummy} = true;"))

        # The loop itself
        code.append(self.lf("while (%s) {" % js_test))
        self._indent += 1
        code += for_body
        self._indent -= 1
        code.append(self.lf("}"))

        # Handle else
        if orelse:
            code.append(" if (%s) {" % else_dummy)
            code += for_else
            code.append(self.lf("}"))
            # Update all breaks to set the dummy. We overwrite the
            # "break;" so it will not be detected by a parent loop
            ii = [i for i, part in enumerate(code) if part == "break;"]
            for i in ii:
                code[i] = f"{else_dummy} = false; break;"

        return code

    def _iterator_assign(self, val, *names):
        if len(names) == 1:
            return f"{names[0]} = {val};"
        else:
            code = []
            for i, name in enumerate(names):
                code.append("%s = %s[%i];" % (name, val, i))
            return " ".join(code)

    # Functions and class definitions

    def gen_functiondef(self, node, lambda_=False, asyn=False):
        # Common code for the FunctionDef and Lambda nodes.

        has_self = node.arg_nodes and node.arg_nodes[0].name in ("self", "this")

        # Bind if this function is inside a function, and does not have self
        binder = ""  # code to add to the end
        if len(self._stack) >= 1 and self._stack[-1][0] == "function":
            if not has_self:
                binder = ").bind(this)"

        # Init function definition
        # Non-anonymouse functions get a name so that they are debugged more
        # easily and resolve to the correct event labels in flexx.event. However,
        # we cannot use the exact name, since we don't want to actually *use* it.
        # Classes give their methods a __name__, so no need to name these.
        code = []
        func_name = ""
        if not lambda_:
            if not has_self:
                func_name = "flx_" + node.name
            prefixed = self.with_prefix(node.name)
            if prefixed == node.name:  # normal function vs method
                self.vars.add(node.name)
                self._seen_func_names.add(node.name)
            code.append(self.lf(f"{prefixed} = "))
        code.append(
            "%s%sfunction %s%s("
            % (
                "(" if binder else "",
                "async " if asyn else "",
                func_name,
                " " if func_name else "",
            )
        )

        # Collect args
        argnames = []
        for arg in node.arg_nodes:  # ast.Arg nodes
            name = self.NAME_MAP.get(arg.name, arg.name)
            if name != "this":
                argnames.append(name)
                # Add code and comma
                code.append(name)
                code.append(", ")
        if argnames:
            code.pop(-1)  # pop last comma

        # Check
        if (not lambda_) and node.decorator_nodes:
            if not (
                len(node.decorator_nodes) == 1
                and isinstance(node.decorator_nodes[0], ast.Name)
                and node.decorator_nodes[0].name == "staticmethod"
            ):
                raise JSError("No support for function decorators")

        # Prepare for content
        code.append(") {")
        pre_code, code = code, []
        self._indent += 1
        self.push_stack("function", "" if lambda_ else node.name)

        # Add argnames to known vars
        for name in argnames:
            self.vars.add(name)

        # Prepare code for varargs
        vararg_code1 = vararg_code2 = ""
        if node.args_node:
            name = node.args_node.name  # always an ast.Arg
            self.vars.add(name)
            if not argnames:
                # Make available under *arg name
                # code.append(self.lf('%s = arguments;' % name))
                vararg_code1 = f"{name} = Array.prototype.slice.call(arguments);"
                vararg_code2 = f"{name} = arguments[0].flx_args;"
            else:
                # Slice it
                x = name, len(argnames)
                vararg_code1 = "%s = Array.prototype.slice.call(arguments, %i);" % x
                vararg_code2 = "%s = arguments[0].flx_args.slice(%i);" % x

        # Handle keyword arguments and kwargs
        kw_argnames = set()  # variables that come from keyword args, or helper vars
        if node.kwarg_nodes or node.kwargs_node:
            # Collect names and default values
            names, values = [], []
            for arg in node.kwarg_nodes:
                self.vars.add(arg.name)
                kw_argnames.add(arg.name)
                names.append(f"'{arg.name}'")
                values.append("".join(self.parse(arg.value_node)))
            # Turn into string representation
            names = "[" + ", ".join(names) + "]"
            values = "[" + ", ".join(values) + "]"
            # Write code to prepare for kwargs
            if node.kwargs_node:
                code.append(self.lf("%s = {};" % node.kwargs_node.name))
            if node.kwarg_nodes:
                values_var = self.dummy("kw_values")
                kw_argnames.add(values_var)
                code += [self.lf(values_var), " = ", values, ";"]
            else:
                values_var = values
            # Enter if to actually parse kwargs
            code.append(
                self.lf(
                    "if (arguments.length == 1 && typeof arguments[0] == 'object' && "
                    "Object.keys(arguments[0]).toString() == 'flx_args,flx_kwargs') {"
                )
            )
            self._indent += 1
            # Call function to parse args
            code += [self.lf()]
            if node.kwargs_node:
                kw_argnames.add(node.kwargs_node.name)
                self.vars.add(node.kwargs_node.name)
                code += [node.kwargs_node.name, " = "]
            self.call_std_function("op_parse_kwargs", [])
            code += [
                stdlib_js.FUNCTION_PREFIX + "op_parse_kwargs(",
                names,
                ", ",
                values_var,
                ", arguments[0].flx_kwargs",
            ]
            if not node.kwargs_node:
                code.append(f", '{func_name}'" or "anonymous")
            code.append(");")
            # Apply values of positional args
            # inside if, because standard arguments are invalid
            args_var = "arguments[0].flx_args"
            if len(argnames) > 1:
                args_var = self.dummy("args")
                code.append(self.lf(f"{args_var} = arguments[0].flx_args;"))
            for i, name in enumerate(argnames):
                code.append(self.lf("%s = %s[%i];" % (name, args_var, i)))
            # End if
            if vararg_code2:
                code.append(self.lf(vararg_code2))
            self._indent -= 1
            code.append(self.lf("}"))
            if vararg_code1:
                code += [" else {", vararg_code1, "}"]
            # Apply values of keyword-only args
            # outside if, because these need to be assigned always
            # Note that we cannot use destructuring assignment because not all
            # browsers support it (meh IE and Safari!)
            for i, arg in enumerate(node.kwarg_nodes):
                code.append(self.lf("%s = %s[%i];" % (arg.name, values_var, i)))
        else:
            if vararg_code1:
                code.append(self.lf(vararg_code1))

        # Apply defaults of positional arguments
        for arg in node.arg_nodes:
            if arg.value_node is not None:
                name = arg.name
                d = "".join(self.parse(arg.value_node))
                x = f"{name} = ({name} === undefined) ? {d}: {name};"
                code.append(self.lf(x))

        # Apply content
        if lambda_:
            code.append("return ")
            code += self.parse(node.body_node)
            code.append(";")
        else:
            docstring = self.pop_docstring(node)
            if docstring and not node.body_nodes:
                # Raw JS - but deprecated
                logger.warning(RAW_DOC_WARNING, node.name)
                for line in docstring.splitlines():
                    code.append(self.lf(line))
            else:
                # Normal function
                if self._docstrings:
                    for line in docstring.splitlines():
                        code.append(self.lf("// " + line))
                for child in node.body_nodes:
                    code += self.parse(child)

        # Wrap up
        if lambda_:
            code.append("}%s" % binder)
            # ns should only consist only of arg names (or helpers)
            for name in argnames:
                self.vars.discard(name)
            if node.args_node:
                self.vars.discard(node.args_node.name)
            ns = self.pop_stack()
            assert set(ns) == kw_argnames
            pre_code.append(self.get_declarations(ns))
        else:
            if not (code and code[-1].strip().startswith("return ")):
                code.append(self.lf("return null;"))
            # Declare vars, but exclude our argnames
            for name in argnames:
                self.vars.discard(name)
            ns = self.pop_stack()
            pre_code.append(self.get_declarations(ns))

        self._indent -= 1
        if not lambda_:
            code.append(self.lf("}%s;\n" % binder))
        return pre_code + code

    def gen_lambda(self, node):
        return self.parse_FunctionDef(node, lambda_=True)

    def gen_asyncfunctiondef(self, node):
        return self.parse_FunctionDef(node, asyn=True)

    def gen_return(self, node):
        if node.value_node is not None:
            return self.lf(f"return {''.join(self.parse(node.value_node))};")
        else:
            return self.lf("return null;")

    def gen_classdef(self, node):
        # Checks
        if len(node.arg_nodes) > 1:
            raise JSError("Multiple inheritance not (yet) supported.")
        if node.kwarg_nodes:
            raise JSError("Metaclasses not supported.")
        if node.decorator_nodes:
            raise JSError("Class decorators not supported.")

        # Get base class (not the constructor)
        base_class = "Object"
        if node.arg_nodes:
            base_class = "".join(self.parse(node.arg_nodes[0]))
        if not base_class.replace(".", "_").isalnum():
            raise JSError("Base classes must be simple names")
        elif base_class.lower() == "object":  # maybe Python "object"
            base_class = "Object"
        else:
            base_class += ".prototype"

        # Define function that acts as class constructor
        code = []
        docstring = self.pop_docstring(node)
        docstring = docstring if self._docstrings else ""
        for line in make_class_definition(node.name, base_class, docstring):
            code.append(self.lf(line))
        self.call_std_function("op_instantiate", [])

        # Body ...
        self.vars.add(node.name)
        self._seen_class_names.add(node.name)
        self.push_stack("class", node.name)
        for sub in node.body_nodes:
            code += self.parse(sub)
        code.append("\n")
        self.pop_stack()
        # no need to declare variables, because they're prefixed

        return code

    def function_super(self, node):
        # allow using super() in methods
        # Note that in parse_Call() we ensure that a call using super
        # uses .call(this, ...) so that the instance is handled ok.

        if node.arg_nodes:
            # raise JSError('super() accepts 0 or 1 arguments.')
            pass  # In Python 2, arg nodes are provided, and we ignore them
        if len(self._stack) < 3:  # module, class, function
            # raise JSError('can only use super() inside a method.')
            # We just provide "super()" and hope that the user will
            # replace the code (as we do in the Model class).
            return "super()"

        # Find the class of this function. Using this._base_class would work
        # in simple situations, but not when there's two levels of super().
        nstype1, nsname1, _ = self._stack[-1]
        nstype2, nsname2, _ = self._stack[-2]
        if not (nstype1 == "function" and nstype2 == "class"):
            raise JSError("can only use super() inside a method.")

        base_class = nsname2
        return f"{base_class}.prototype._base_class"

    # def parse_Yield
    # def parse_YieldFrom

    def gen_await(self, node):
        return f"await {''.join(self.parse(node.value_node))}"

    def gen_global(self, names) -> str:
        for name in names:
            self.vars.set_global(name)
        return ""

    def gen_nonlocal(self, names) -> str:
        for name in names:
            self.vars.set_nonlocal(name)
        return ""

    #
    # Utils
    #
    def lf(self, code=""):
        """Line feed - create a new line with the correct indentation."""
        return "\n" + self._indent * "    " + code

    def dummy(self, name=""):
        """Get a unique name.

        The name is added to vars.
        """
        self._dummy_counter += 1
        name = "stub%i_%s" % (self._dummy_counter, name)
        self.vars.add(name)
        return name
