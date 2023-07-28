from prescrypt.ast import ast
from prescrypt.stdlib_js import FUNCTION_PREFIX
from prescrypt.stdlib_py import stdlib
from prescrypt.utils import unify

from ..compiler import compiler
from .expr import gen_expr
from ..stdlib import call_std_function


@gen_expr.register
def gen_call(node: ast.Call) -> str | list:
    """Generate code for a function call."""

    func, args, keywords = node.func, node.args, node.keywords

    method_name = ""
    func_name = ""
    obj_js = ""

    match func:
        case ast.Attribute(value, attr, ctx):
            # TODO:
            # we asume for now that the left side is an object and the call
            # a method call.
            method_name = attr
            obj_js = gen_expr(value)

        case ast.Subscript(value, slice, ctx):
            base_name = unify(gen_expr(value))
            full_name = unify(gen_expr(func))
            method_name = ""

        case ast.Name(id):
            func_name = id

        case _:
            method_name = ""
            base_name = ""
            full_name = unify(gen_expr(func))

    builtins = stdlib

    if method_name:
        if builtin_meth := builtins.get_method(method_name):
            if res := builtin_meth(compiler, obj_js, args, keywords):
                return res

        args_js = [obj_js] + [unify(gen_expr(arg)) for arg in args]

        return f"_pymeth_{method_name}.apply({', '.join(args_js)})"

    elif func_name:
        if builtin_func := builtins.get_function(func_name):
            if res := builtin_func(compiler, args, keywords):
                return res

        args_js = [unify(gen_expr(arg)) for arg in args]

        return f"_pyfunc_{func_name}({', '.join(args_js)})"

    else:
        raise NotImplementedError("Unknown function call: " + str(func))

        #
        # FIXME: Everything below needs to be refactored
        #

        # Handle builtins functions and methods
        # res = None
        # if builtin_func := builtins.get_function(full_name):
        #     res = builtin_func(self, args, keywords)
        # elif builtin_meth := builtins.get_method(full_name):
        #     res = builtin_meth(self, base_name, args, keywords)
        #
        # if res is not None:
        return res

    # Handle normally
    if base_name.endswith("._base_class") or base_name == "super()":
        # super() was used, use "call" to pass "this"
        return [full_name] + self._get_args(
            args, keywords, "this", use_call_or_apply=True
        )

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


def _get_args(args, keywords, base_name, use_call_or_apply=False):
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
    args_simple, args_array = _get_positional_args(args)
    kwargs = _get_keyword_args(keywords)

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


def _get_positional_args(args: list[ast.expr]):
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
                starname = "".join(gen_expr(value))
                arglists.append(starname)
                argswithcommas = []
                arglists.append(argswithcommas)
            case _:
                argswithcommas.extend(gen_expr(arg))
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


def _get_keyword_args(keywords: list[ast.keyword]):
    """Get a string that represents the dictionary of keyword arguments, or
    None if there are no keyword arguments (normal nor double-star)."""

    assert isinstance(keywords, list)

    # Collect elements that will make up the total kwarg dict
    kwargs = []
    for keyword in keywords:
        if not keyword.arg:  # **xx
            kwargs.append(unify(gen_expr(keyword.value)))
        else:  # foo=xx
            if not (kwargs and isinstance(kwargs[-1], list)):
                kwargs.append([])
            kwargs[-1].append(f"{keyword.arg}: {unify(gen_expr(keyword.value))}")

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
        call_std_function("merge_dicts", [])
        return FUNCTION_PREFIX + "merge_dicts(" + ", ".join(kwargs) + ")"
