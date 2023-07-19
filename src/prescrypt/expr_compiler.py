import ast
import json
import re

from devtools import debug

from prescrypt import stdlib
from prescrypt.constants import (ATTRIBUTE_MAP, BINARY_OP, BOOL_OP, COMP_OP,
                                 UNARY_OP, isidentifier1, reserved_names)
from prescrypt.exceptions import JSError
from prescrypt.utils import unify


class ExpressionCompiler:
    """
    + Constant(constant value, string? kind)
    + List(expr* elts, expr_context ctx)
    + Tuple(expr* elts, expr_context ctx)
    + Dict(expr* keys, expr* values)
    + Set(expr* elts)

    + BoolOp(boolop op, expr* values)
    + UnaryOp(unaryop op, expr operand)
    + BinOp(expr left, operator op, expr right)
    + Compare(expr left, cmpop* ops, expr* comparators)
    + Call(expr func, expr* args, keyword* keywords)

    + JoinedStr(expr* values)
    + Name(identifier id, expr_context ctx)
    + Attribute(expr value, identifier attr, expr_context ctx)
    + IfExp(expr test, expr body, expr orelse)

    - Lambda(arguments args, expr body)
    - ListComp(expr elt, comprehension* generators)
    - SetComp(expr elt, comprehension* generators)
    - DictComp(expr key, expr value, comprehension* generators)
    - NamedExpr(expr target, expr value)
    - GeneratorExp(expr elt, comprehension* generators)
    - Await(expr value)
    - Yield(expr? value)
    - YieldFrom(expr value)
    - FormattedValue(expr value, int conversion, expr? format_spec)
    - Subscript(expr value, expr slice, expr_context ctx)
    - Starred(expr value, expr_context ctx)
    - Slice(expr? lower, expr? upper, expr? step)
    """

    # Temp
    _pscript_overload = False
    _methods = {}
    _functions = {}
    _seen_func_names = set()
    _seen_class_names = set()
    _std_methods = set()
    _stack = []

    def gen_expr(self, expr_node: ast.expr) -> str | list:
        assert isinstance(expr_node, ast.expr)

        match expr_node:
            #
            # Constants / literals
            #
            case ast.Num(n):
                return str(n)

            case ast.Str(s):
                return repr(s)

            case ast.Bytes(b):
                raise JSError("No Bytes in JS")

            case ast.NameConstant(value):
                M = {True: "true", False: "false", None: "null"}
                return M[value]

            case ast.JoinedStr(values):
                parts, value_nodes = [], []
                for n in values:
                    match n:
                        case ast.Str(s):
                            parts.append(s)
                        case ast.FormattedValue(value, conversion, format_spec):
                            parts.append("{" + self._parse_FormattedValue_fmt(n) + "}")
                            value_nodes.append(n.value_node)
                        case _:
                            raise JSError("Unknown JoinedStr part: " + str(n))
                thestring = json.dumps("".join(parts))
                return self.use_std_method(thestring, "format", value_nodes)

            #
            # Complex primitive types
            #
            case ast.List(elts, ctx):
                return self.gen_list(elts, ctx)

            case ast.Tuple(elts, ctx):
                # tuple = ~ list in JS
                return self.gen_list(elts, ctx)

            case ast.Set(elts):
                raise JSError("No Set in JS")

            case ast.Dict(keys, values):
                return self.gen_dict(keys, values)

            #
            # Operators
            #
            case ast.UnaryOp(op, operand):
                return self.gen_unary_op(op, operand)

            case ast.BoolOp(op, values):
                return self.gen_bool_op(op, values)

            case ast.BinOp(left, op, right):
                return self.gen_bin_op(left, op, right)

            case ast.Compare(left, ops, comparators):
                return self.gen_compare(left, ops, comparators)

            #
            # Variables
            #
            case ast.Name(id, ctx):
                return self.gen_name(id, ctx)

            case ast.Attribute(value, attr, ctx):
                return self.gen_attribute(value, attr, ctx)

            #
            # Calls
            #
            case ast.Call(func, args, keywords):
                return self.gen_call(func, args, keywords)

            #
            # Other epxressions
            #
            case ast.IfExp(test, body, orelse):
                return self.gen_if_exp(test, body, orelse)

            case ast.ListComp(elt, generators):
                return self.gen_list_comp(elt, generators)

            #
            # Error
            #
            case _:
                raise NotImplementedError("Unknown expression type: " + str(expr_node))

    #
    # Complex types
    #
    def gen_list(self, elts, ctx) -> str | list:
        code = ["["]
        for el in elts:
            code += self.gen_expr(el)
            code.append(", ")
        if elts:
            code.pop(-1)  # skip last comma
        code.append("]")
        return code

    def gen_dict(self, keys, values) -> list | str:
        # Oh JS; without the outer braces, it would only be an Object if used
        # in an assignment ...
        code = ["({"]
        for key, val in zip(keys, values):
            if isinstance(key, (ast.Num, ast.NameConstant)):
                code += self.gen_expr(key)
            elif (
                isinstance(key, ast.Str)
                and isidentifier1.match(key.value)
                and key.value[0] not in "0123456789"
            ):
                code += key.value
            else:
                return self.gen_dict_fallback(keys, values)

            code.append(": ")
            code += self.gen_expr(val)
            code.append(", ")
        if keys:
            code.pop(-1)  # skip last comma
        code.append("})")

        return code

    def gen_dict_fallback(self, keys: list[ast.expr], values: list[ast.expr]) -> str:
        func_args = []
        for key, val in zip(keys, values):
            func_args += [
                unify(self.gen_expr(key)),
                unify(self.gen_expr(val)),
            ]
        self.use_std_function("create_dict", [])
        return stdlib.FUNCTION_PREFIX + "create_dict(" + ", ".join(func_args) + ")"

    #
    # Ops
    #
    def gen_unary_op(self, op, operand) -> str | list:
        if type(op) is ast.Not:
            return ["!", self._wrap_truthy(operand)]
        else:
            js_op = UNARY_OP[op]
            right = unify(self.gen_expr(operand))
            return [js_op, right]

    def gen_bool_op(self, op, values) -> str | list:
        js_op = f" {BOOL_OP[op]} "
        if type(op) == ast.Or:  # allow foo = bar or []
            js_values = [unify(self._wrap_truthy(val)) for val in values[:-1]]
            js_values += [unify(self.gen_expr(values[-1]))]
        else:
            js_values = [unify(self._wrap_truthy(val)) for val in values]
        return js_op.join(js_values)

    def gen_bin_op(self, left, op, right) -> str | list:
        if type(op) == ast.Mod and isinstance(left, ast.Str):
            # Modulo on a string is string formatting in Python
            return self._format_string(left, right)

        _js_left = self.gen_expr(left)
        debug(left, _js_left)
        js_left = unify(self.gen_expr(left))
        js_right = unify(self.gen_expr(right))

        if type(op) == ast.Add:
            C = ast.Num, ast.Str
            if self._pscript_overload and not (
                isinstance(left, C)
                or isinstance(right, C)
                or (
                    isinstance(left, ast.BinOp)
                    and type(left.op) == ast.Add
                    and "op_add" not in left
                )
                or (
                    isinstance(right, ast.BinOp)
                    and type(right.op) == ast.Add
                    and "op_add" not in right
                )
            ):
                return self.use_std_function("op_add", [js_left, js_right])

        elif type(op) == ast.Mult:
            C = ast.Num
            if self._pscript_overload and not (
                isinstance(left, C) and isinstance(right, C)
            ):
                return self.use_std_function("op_mult", [js_left, js_right])

        elif type(op) == ast.Pow:
            return ["Math.pow(", js_left, ", ", js_right, ")"]

        elif type(op) == ast.FloorDiv:
            return ["Math.floor(", js_left, "/", js_right, ")"]

        # Default
        js_op = f" {BINARY_OP[op]} "
        return [js_left, js_op, js_right]

    def gen_compare(self, left, ops, comparators) -> str | list:
        js_left = unify(self.gen_expr(left))
        js_right = unify(self.gen_expr(comparators[0]))
        op = ops[0]

        if type(op) in (ast.Eq, ast.NotEq) and not js_left.endswith(".length"):
            if self._pscript_overload:
                code = self.use_std_function("op_equals", [js_left, js_right])
                if type(op) == ast.NotEq:
                    code = "!" + code
            else:
                if type(op) == ast.NotEq:
                    code = [js_left, "!=", js_right]
                else:
                    code = [js_left, "==", js_right]
            return code

        elif type(op) in (ast.In, ast.NotIn):
            self.use_std_function("op_equals", [])  # trigger use of equals
            code = self.use_std_function("op_contains", [js_left, js_right])
            if type(op) == ast.NotIn:
                code = "!" + code
            return code

        else:
            js_op = COMP_OP[op]
            return f"{js_left} {js_op} {js_right}"

    #
    # Variables
    #
    def gen_name(self, id, ctx) -> str:
        name = id
        # ctx can be Load, Store, Del -> can be of use somewhere?
        if name in reserved_names:
            raise JSError(f"Cannot use reserved name {name} as a variable name!")
        # if self.vars.is_known(name):
        #     return self.with_prefix(name)
        # if self._scope_prefix:
        #     for stackitem in reversed(self._stack):
        #         scope = stackitem[2]
        #         for prefix in reversed(self._scope_prefix):
        #             prefixed_name = prefix + name
        #             if prefixed_name in scope:
        #                 return prefixed_name
        # if name in self.NAME_MAP:
        #     return self.NAME_MAP[name]
        # # Else ...
        # if not (name in self._functions or name in ("undefined", "window")):
        #     # mark as used (not defined)
        #     used_name = (name + "." + fullname) if fullname else name
        #     self.vars.use(name, used_name)
        return name

    def gen_attribute(self, value, attr, ctx, fullname=None):
        fullname = attr + "." + fullname if fullname else attr
        match value:
            case ast.Name():
                base_name = self.gen_name(value, ctx)
            case ast.Attribute():
                base_name = self.gen_attribute(value, ctx, fullname)
            case _:
                base_name = unify(self.gen_expr(value))

        # Double underscore name mangling
        if attr.startswith("__") and not attr.endswith("__") and base_name == "this":
            for i in range(len(self._stack) - 1, -1, -1):
                if self._stack[i][0] == "class":
                    classname = self._stack[i][1]
                    attr = "_" + classname + attr
                    break

        if attr in ATTRIBUTE_MAP:
            return ATTRIBUTE_MAP[attr].replace("{}", base_name)
        else:
            return f"{base_name}.{attr}"

    #
    # Function calls
    #
    def gen_call(self, func, args, keywords) -> str | list:
        # Get full function name and method name if it exists
        match func:
            case ast.Attribute():
                # We don't want to parse twice, because it may add to the vars_unknown
                method_name = func.attr
                nameparts = self.gen_expr(func)
                full_name = unify(nameparts)
                nameparts[-1] = nameparts[-1].rsplit(".", 1)[0]
                base_name = unify(nameparts)

            case ast.Subscript():
                base_name = unify(self.gen_expr(func.value_node))
                full_name = unify(self.gen_expr(func))
                method_name = ""

            case _:
                method_name = ""
                base_name = ""
                full_name = unify(self.gen_expr(func))

        # Handle special functions and methods
        res = None
        if method_name in self._methods:
            res = self._methods[method_name](node, base_name)
        elif full_name in self._functions:
            res = self._functions[full_name](node)
        if res is not None:
            return res

        # Handle normally
        if base_name.endswith("._base_class") or base_name == "super()":
            # super() was used, use "call" to pass "this"
            return [full_name] + self._get_args(
                args, keywords, "this", use_call_or_apply=True
            )
        else:
            code = [full_name] + self._get_args(args, keywords, base_name)
            # Insert "new" if this looks like a class
            if base_name == "this":
                pass
            elif method_name:
                if method_name[0].lower() != method_name[0]:
                    code.insert(0, "new ")
            else:
                fn = full_name
                if fn in self._seen_func_names and fn not in self._seen_class_names:
                    pass
                elif fn not in self._seen_func_names and fn in self._seen_class_names:
                    code.insert(0, "new ")
                elif full_name[0].lower() != full_name[0]:
                    code.insert(0, "new ")
            return code

    def _get_args(self, args, keywords, base_name, use_call_or_apply=False):
        """Get arguments for function call.

        Does checking for keywords and handles starargs. The first
        element in the returned list is either "(" or ".apply(".
        """

        # Can produce:
        # normal:               foo(.., ..)
        # use_call_or_apply:    foo.call(base_name, .., ..)
        # use_starargs:         foo.apply(base_name, vararg_name)
        #           or:         foo.apply(base_name, [].concat([.., ..], vararg_name)
        # has_kwargs:           foo({__args: [], __kwargs: {} })
        #         or:           foo.apply(base_name, ({__args: [], __kwargs: {} })

        base_name = base_name or "null"

        # Get arguments
        args_simple, args_array = self._get_positional_args(args)
        kwargs = self._get_keyword_args(keywords)

        if kwargs is not None:
            # Keyword arguments need a whole special treatment
            if use_call_or_apply:
                start = [".call(", base_name, ", "]
            else:
                start = ["("]
            return start + [
                "{",
                "flx_args: ",
                args_array,
                ", flx_kwargs: ",
                kwargs,
                "})",
            ]
        elif args_simple is None:
            # Need to use apply
            return [".apply(", base_name, ", ", args_array, ")"]
        elif use_call_or_apply:
            # Need to use call (arg_simple can be empty string)
            if args_simple:
                return [".call(", base_name, ", ", args_simple, ")"]
            else:
                return [".call(", base_name, ")"]
        else:
            # Normal function call
            return ["(", args_simple, ")"]

    def _get_positional_args(self, args: list[ast.expr]):
        """Returns:
        * a string args_simple, which represents the positional args in comma
          separated form. Can be None if the args cannot be represented that
          way. Note that it can be empty string.
        * a string args_array representing the array with positional arguments.
        """

        # Generate list of arg lists (has normal positional args and starargs)
        # Note that there can be multiple starargs and these can alternate.
        assert isinstance(args, list)

        argswithcommas = []
        arglists = [argswithcommas]
        for arg in args:
            match arg:
                case ast.Starred(value):
                    starname = "".join(self.gen_expr(value))
                    arglists.append(starname)
                    argswithcommas = []
                    arglists.append(argswithcommas)
                case _:
                    argswithcommas.extend(self.gen_expr(arg))
                    argswithcommas.append(", ")

        # Clear empty lists and trailing commas
        for i in reversed(range(len(arglists))):
            arglist = arglists[i]
            if not arglist:
                arglists.pop(i)
            elif arglist[-1] == ", ":
                arglist.pop(-1)

        # Generate code for positional arguments
        if len(arglists) == 0:
            return "", "[]"
        elif len(arglists) == 1 and isinstance(arglists[0], list):
            args_simple = "".join(argswithcommas)
            return args_simple, "[" + args_simple + "]"
        elif len(arglists) == 1:
            assert isinstance(arglists[0], str)
            return None, arglists[0]
        else:
            code = ["[].concat("]
            for arglist in arglists:
                if isinstance(arglist, list):
                    code += ["["] + arglist + ["]"]
                else:
                    code += [arglist]
                code += [", "]
            code.pop(-1)
            code += ")"
            return None, "".join(code)

    def _get_keyword_args(self, keywords: list[ast.keyword]):
        """Get a string that represents the dictionary of keyword arguments, or
        None if there are no keyword arguments (normal nor double-star)."""

        assert isinstance(keywords, list)

        # Collect elements that will make up the total kwarg dict
        kwargs = []
        debug(keywords)
        for keyword in keywords:
            if not keyword.arg:  # **xx
                kwargs.append(unify(self.gen_expr(keyword.value)))
            else:  # foo=xx
                if not (kwargs and isinstance(kwargs[-1], list)):
                    kwargs.append([])
                kwargs[-1].append(
                    f"{keyword.arg}: {unify(self.gen_expr(keyword.value))}"
                )

        # Resolve sequneces of loose kwargs
        for i in range(len(kwargs)):
            if isinstance(kwargs[i], list):
                kwargs[i] = "{" + ", ".join(kwargs[i]) + "}"

        # Compose, easy if singleton, otherwise we need to merge
        if len(kwargs) == 0:
            return None
        elif len(kwargs) == 1:
            return kwargs[0]
        else:
            # register use of merge_dicts(), but we build the string ourselves
            self.use_std_function("merge_dicts", [])
            return stdlib.FUNCTION_PREFIX + "merge_dicts(" + ", ".join(kwargs) + ")"

    #
    # The rest
    #
    def gen_if_exp(self, test, body, orelse) -> list[str]:
        # in "a if b else c"
        js_body = self.gen_expr(body)
        js_test = self._wrap_truthy(test)
        js_else = self.gen_expr(orelse)

        code = ["("]
        code += js_test
        code.append(")? (")
        code += js_body
        code.append(") : (")
        code += js_else
        code.append(")")
        return code

    def gen_list_comp(self, elt, generators) -> list[str]:
        # Note: generators is a list of ast.comprehension
        # ast.comprehension has attrs: 'target', 'iter', 'ifs', 'is_async',
        debug(elt, generators)

        self.push_stack("function", "listcomp")
        elt = "".join(self.gen_expr(elt))
        code = ["(function list_comprehension (iter0) {", "var res = [];"]
        vars = []

        for iter, comprehension in enumerate(generators):
            cc = []
            # Get target (can be multiple vars)
            if isinstance(comprehension.target, ast.Tuple):
                target = ["".join(self.gen_expr(t)) for t in comprehension.target]
            else:
                target = ["".join(self.gen_expr(comprehension.target))]

            for t in target:
                vars.append(t)
            vars.append("i%i" % iter)

            # comprehension(target_node, iter_node, if_nodes)
            if iter > 0:  # first one is passed to function as an arg
                cc.append(f"iter# = {''.join(self.gen_expr(comprehension.iter_node))};")
                vars.append("iter%i" % iter)
            cc.append(
                'if ((typeof iter# === "object") && '
                "(!Array.isArray(iter#))) {iter# = Object.keys(iter#);}"
            )
            cc.append("for (i#=0; i#<iter#.length; i#++) {")
            cc.append(self._iterator_assign("iter#[i#]", *target))

            # Ifs
            if comprehension.if_nodes:
                cc.append("if (!(")
                for iff in comprehension.if_nodes:
                    cc += unify(self.gen_expr(iff))
                    cc.append("&&")
                cc.pop(-1)  # pop '&&'
                cc.append(")) {continue;}")

            # Insert code for this comprehension loop
            code.append(
                "".join(cc)
                .replace("i#", "i%i" % iter)
                .replace("iter#", "iter%i" % iter)
            )

        # Push result
        code.append("{res.push(%s);}" % elt)
        for comprehension in node.comp_nodes:
            code.append("}")  # end for
        # Finalize
        code.append("return res;})")  # end function
        iter0 = "".join(self.parse(node.comp_nodes[0].iter_node))
        code.append(".call(this, " + iter0 + ")")  # call funct with iter as 1st arg
        code.insert(2, f"var {', '.join(vars)};")
        # Clean vars
        for var in vars:
            self.vars.add(var)
        self.pop_stack()
        return code

        # todo: apply the apply(this) trick everywhere where we use a function

    #
    # Utility functions
    #
    def _wrap_truthy(self, node: ast.expr) -> str | list:
        """Wraps an operation in a truthy call, unless it's not necessary."""
        eq_name = stdlib.FUNCTION_PREFIX + "op_equals"
        test = "".join(self.gen_expr(node))
        if not self._pscript_overload:
            return unify(test)
        elif (
            test.endswith(".length")
            or test.startswith("!")
            or test.isnumeric()
            or test == "true"
            or test == "false"
            or test.count("==")
            or test.count(">")
            or test.count("<")
            or test.count(eq_name)
            or test == '"this_is_js()"'
            or test.startswith("Array.isArray(")
            or (test.startswith(returning_bool) and "||" not in test)
        ):
            return unify(test)
        else:
            return self.use_std_function("truthy", [test])

    def _format_string(self, left, right):
        # Get value_nodes
        if isinstance(right, (ast.Tuple, ast.List)):
            value_nodes = right.elts
        else:
            value_nodes = [right]

        # Is the left side a string? If not, exit early
        # This works, but we cannot know whether the left was a string or number :P
        # if not isinstance(node.left_node, ast.Str):
        #     thestring = unify(self.parse(node.left_node))
        #     thestring += ".replace(/%([0-9\.\+\-\#]*[srdeEfgGioxXc])/g, '{:$1}')"
        #     return self.use_std_method(thestring, 'format', value_nodes)

        assert isinstance(left, ast.Str)
        js_left = "".join(self.gen_expr(left))
        sep, js_left = js_left[0], js_left[1:-1]

        # Get matches
        matches = list(re.finditer(r"%[0-9.+#-]*[srdeEfgGioxXc]", js_left))
        if len(matches) != len(value_nodes):
            raise JSError(
                "In string formatting, number of placeholders "
                "does not match number of replacements"
            )
        # Format
        parts = []
        start = 0
        for m in matches:
            fmt = m.group(0)
            fmt = {"%r": "!r", "%s": ""}.get(fmt, ":" + fmt[1:])
            # Add the part in front of the match (and after prev match)
            parts.append(left[start : m.start()])
            parts.append("{%s}" % fmt)
            start = m.end()
        parts.append(left[start:])
        thestring = sep + "".join(parts) + sep
        return self.use_std_method(thestring, "format", value_nodes)

    def use_std_function(self, name: str, args: list) -> str:
        """Use a function from the standard library."""
        mangled_name = stdlib.FUNCTION_PREFIX + name
        return f"{mangled_name}.call({', '.join(args)})"

    def use_std_method(self, base, name, arg_nodes) -> str:
        """Use a method from the PScript standard library."""
        self._handle_std_deps(stdlib.METHODS[name])
        self._std_methods.add(name)
        mangled_name = stdlib.METHOD_PREFIX + name
        args = [
            (a if isinstance(a, str) else unify(self.gen_expr(a))) for a in arg_nodes
        ]
        # return '%s.%s(%s)' % (base, mangled_name, ', '.join(args))
        args.insert(0, base)
        return f"{mangled_name}.call({', '.join(args)})"

    def _handle_std_deps(self, code):
        nargs, function_deps, method_deps = stdlib.get_std_info(code)
        for dep in function_deps:
            self.use_std_function(dep, [])
        for dep in method_deps:
            self.use_std_method("x", dep, [])
