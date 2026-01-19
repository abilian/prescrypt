from __future__ import annotations

from attr import define

from prescrypt.codegen.main import CodeGen, gen_expr
from prescrypt.codegen.stdlib_py import stdlib
from prescrypt.codegen.utils import flatten, unify
from prescrypt.front import ast
from prescrypt.stdlib_js import StdlibJs


@gen_expr.register
def gen_call(node: ast.Call, codegen: CodeGen) -> str | list:
    """Generate code for a function call."""
    return FuncCall(node, codegen).gen()


@define
class FuncCall:
    """A function call."""

    node: ast.Call
    codegen: CodeGen

    def gen(self):
        """Generate JS code."""
        return self.gen_call()

    def gen_call(self):
        node = self.node
        func, args, keywords = node.func, node.args, node.keywords

        match func:
            case ast.Name(func_name):
                return self.gen_call_named(func_name, args, keywords)

            case ast.Attribute(value, method_name):
                # we asume for now that the left side is an object and the call
                # a method call.
                return self.gen_method_call(value, method_name, args, keywords)

            case ast.Call() | ast.Subscript() | ast.IfExp() | ast.Lambda():
                # Callable is the result of another expression:
                # - f(x)(y) - chained call
                # - items[0]() - subscript call
                # - (foo if cond else bar)() - conditional call
                # - (lambda x: x)() - lambda call
                js_func = flatten(self.codegen.gen_expr(func))
                return f"({js_func}){self.gen_args()}"

            case ast.Constant():
                # Calling a literal like 1() - valid Python that raises TypeError at runtime
                js_func = flatten(self.codegen.gen_expr(func))
                return f"({js_func}){self.gen_args()}"

            case _:
                msg = f"gen_call not implemented for {func!r}"
                raise NotImplementedError(msg)

    def gen_call_named(self, func_name, args, keywords):
        stdlib_py = stdlib
        stdlib_js = StdlibJs()

        if builtin_func := stdlib_py.get_function(func_name):
            if res := builtin_func(self.codegen, args, keywords):
                return res

        if func_name in stdlib_js.functions:
            # Use codegen.call_std_function for usage tracking
            return self.codegen.call_std_function(func_name, args)

        # Check if there are kwargs - if so, use call_kwargs helper
        if keywords:
            return self._gen_call_with_kwargs(func_name, args, keywords)

        return f"{self.gen_func()}{self.gen_args()}"

    def _gen_call_with_kwargs(self, func_name: str, args: list, keywords: list):
        """Generate call using call_kwargs helper for **kwargs support."""
        # Build positional args array
        _args_simple, args_array = self._get_positional_args(args)

        # Build kwargs dict
        kwargs = self._get_keyword_args(keywords)

        # Use call_kwargs runtime helper
        return self.codegen.call_std_function(
            "call_kwargs", [func_name, args_array, kwargs]
        )

    def gen_method_call(self, value, method_name, args, keywords):
        stdlib_py = stdlib
        stdlib_js = StdlibJs()

        # For class methods like int.from_bytes, pass the original name
        # so the method handler can recognize it
        if isinstance(value, ast.Name):
            obj_for_handler = value.id
        else:
            obj_for_handler = unify(self.gen_expr(value))

        obj_js = unify(self.gen_expr(value))

        if builtin_meth := stdlib_py.get_method(method_name):
            if res := builtin_meth(self.codegen, obj_for_handler, args, keywords):
                return res

        if method_name in stdlib_js.methods:
            # Use codegen.call_std_method for usage tracking
            return self.codegen.call_std_method(obj_js, method_name, args)

        return f"{self.gen_func()}{self.gen_args()}"

    def gen_func(self):
        return self.gen_expr(self.node.func)

    def gen_args(self):
        """Generate arguments for function call."""
        args = self.node.args
        keywords = self.node.keywords
        base_name = "null"
        return flatten(self._get_args(args, keywords, base_name))

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

        if args_simple is None:
            # Need to use apply
            return [".apply(", base_name, ", ", args_array, ")"]

        if use_call_or_apply:
            # Need to use call (arg_simple can be empty string)
            if args_simple:
                return [".call(", base_name, ", ", args_simple, ")"]
            else:
                return [".call(", base_name, ")"]

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
                    starname = flatten(self.gen_expr(value))
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
            args_simple = flatten(argswithcommas)
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
            return None, flatten(code)

    def _get_keyword_args(self, keywords: list[ast.keyword]):
        """Get a string that represents the dictionary of keyword arguments, or
        None if there are no keyword arguments (normal nor double-star)."""

        assert isinstance(keywords, list)

        # Collect elements that will make up the total kwarg dict
        kwargs = []
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
            self.call_std_function("merge_dicts", [])
            return (
                self.codegen.function_prefix + "merge_dicts(" + ", ".join(kwargs) + ")"
            )

    def gen_expr(self, expr: ast.expr):
        return self.codegen.gen_expr(expr)

    def call_std_function(self, func_name: str, args: list[str]):
        return self.codegen.call_std_function(func_name, args)
