from __future__ import annotations

from attr import define

from prescrypt.codegen.main import CodeGen, gen_expr
from prescrypt.codegen.stdlib_py import stdlib
from prescrypt.codegen.utils import flatten, unify
from prescrypt.front import ast
from prescrypt.stdlib_js import FUNCTION_PREFIX, METHOD_PREFIX, StdlibJs


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

            case _:
                raise NotImplementedError(f"gen_call not implemented for {func!r}")

    def gen_call_named(self, func_name, args, keywords):
        stdlib_py = stdlib
        stdlib_js = StdlibJs()

        if builtin_func := stdlib_py.get_function(func_name):
            if res := builtin_func(self.codegen, args, keywords):
                return res

        if func_name in stdlib_js.functions:
            args_js = [unify(self.gen_expr(arg)) for arg in args]
            return f"{FUNCTION_PREFIX}{func_name}({', '.join(args_js)})"

        return f"{self.gen_func()}{self.gen_args()}"

    def gen_method_call(self, value, method_name, args, keywords):
        stdlib_py = stdlib
        stdlib_js = StdlibJs()

        obj_js = self.gen_expr(value)

        if builtin_meth := stdlib_py.get_method(method_name):
            if res := builtin_meth(self.codegen, obj_js, args, keywords):
                return res

        if method_name in stdlib_js.methods:
            args_js = [obj_js] + [unify(self.gen_expr(arg)) for arg in args]
            return f"{METHOD_PREFIX}{method_name}.call({', '.join(args_js)})"

        return f"{self.gen_func()}{self.gen_args()}"

    def gen_func(self):
        return self.gen_expr(self.node.func)

    def gen_args(self):
        """Generate arguments for function call."""
        args = self.node.args
        keywords = self.node.keywords
        base_name = "xxx"
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
            return FUNCTION_PREFIX + "merge_dicts(" + ", ".join(kwargs) + ")"

    def gen_expr(self, expr: ast.expr):
        return self.codegen.gen_expr(expr)

    def call_std_function(self, func_name: str, args: list[str]):
        return self.codegen.call_std_function(func_name, args)
