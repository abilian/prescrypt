"""Parts of this code (and in the other modules that define the parser class)
are inspired by / taken from the py2js project.

Useful links:
 * https://greentreesnakes.readthedocs.org/en/latest/nodes.html
 * https://github.com/qsnake/py2js/blob/master/py2js/__init__.py

Main limiting features for browsers (not sure if this is 100% complete):
* Object.keys supported from IE 9 - we use it in method_keys()
"""
import ast
from abc import abstractmethod

from . import stdlib_js
from .namespace import NameSpace
from .utils import unify


class BaseCompiler:
    """The Base parser class. Implements the basic mechanism to allow parsing
    to work, but does not implement any parsing on its own.

    For details see the Parser class.
    """

    _indent: int
    _stack: list

    # Developer notes:
    # The parse_x() functions are called by parse() with the node of
    # type x. They should return a string or a list of strings. parse()
    # always returns a list of strings.

    # def __init__(
    #     self, code, pysource=None, indent=0, docstrings=True, inline_stdlib=True
    # ):
    #     self._pycode = code  # helpfull during debugging
    #     self._pysource = None
    #     if isinstance(pysource, str):
    #         self._pysource = pysource, 0
    #     elif isinstance(pysource, tuple):
    #         self._pysource = str(pysource[0]), int(pysource[1])
    #     elif pysource is not None:
    #         logger.warning("Parser ignores pysource; it must be str or (str, int).")
    #     self._root = converter.parse(code)
    #     self._stack = []
    #     self._indent = indent
    #     self._dummy_counter = 0
    #     self._scope_prefix = []  # stack of name prefixes to simulate local scope
    #
    #     # To keep track of std lib usage
    #     self._std_functions = set()
    #     self._std_methods = set()
    #
    #     # To help distinguish classes from functions
    #     self._seen_func_names = set()
    #     self._seen_class_names = set()
    #
    #     # Options
    #     self._docstrings = bool(docstrings)  # whether to inclue docstrings
    #
    #     # Collect function and method handlers
    #     self._functions, self._methods = {}, {}
    #     for name in dir(self.__class__):
    #         if name.startswith("function_op_"):
    #             pass  # special operator function that we use explicitly
    #         elif name.startswith("function_"):
    #             self._functions[name[9:]] = getattr(self, name)
    #         elif name.startswith("method_"):
    #             self._methods[name[7:]] = getattr(self, name)
    #
    #     # Prepare
    #     self.push_stack("module", "")
    #
    #     # Parse
    #     try:
    #         self._parts = self.parse(self._root)
    #     except JSError as err:
    #         # Give smarter error message
    #         _, _, tb = sys.exc_info()
    #         try:
    #             msg = self._better_js_error(tb)
    #         except Exception:  # pragma: no cover
    #             raise err
    #         else:
    #             err.args = (msg + ":\n" + str(err),)
    #             raise (err)
    #
    #     # Finish
    #     ns = self.vars  # do not self.pop_stack() so caller can inspect module vars
    #     defined_names = ns.get_defined()
    #     if defined_names:
    #         self._parts.insert(0, self.get_declarations(ns))
    #
    #     # Add part of the stdlib that was actually used
    #     if inline_stdlib:
    #         libcode = stdlib.get_partial_std_lib(
    #             self._std_functions, self._std_methods, self._indent
    #         )
    #         if libcode:
    #             self._parts.insert(0, libcode)
    #
    #     # Post-process
    #     if self._parts:
    #         self._parts[0] = "    " * indent + self._parts[0].lstrip()

    @abstractmethod
    def gen_expr(self, node) -> str:
        """Implemented in the ExpressionCompiler mixin."""

    @abstractmethod
    def gen_stmt(self, node) -> str:
        """Implemented in the StatementCompiler mixin."""

    def _better_js_error(self, tb):  # pragma: no cover
        """If we get a JSError, we try to get the corresponding node and print
        the lineno as well as the function etc."""
        node = None
        class_node = None
        func_node = None
        while tb.tb_next:
            tb = tb.tb_next
            node = tb.tb_frame.f_locals.get("node", node)
            class_node = node if isinstance(node, ast.ClassDef) else class_node
            func_node = node if isinstance(node, ast.FunctionDef) else func_node

        # Get location as accurately as we can
        filename = None
        lineno = getattr(node, "lineno", -1)
        if self._pysource:
            filename, lineno = self._pysource
            lineno += node.lineno

        msg = f"Error processing {node.__class__.__name__}-node"
        if class_node:
            msg += f' in class "{class_node.name}"'
        if func_node:
            msg += f' in function "{func_node.name}"'
        if filename:
            msg += f' in "{filename}"'
        if hasattr(node, "lineno"):
            msg += ", line %i, " % lineno
        if hasattr(node, "col_offset"):
            msg += "col %i" % node.col_offset
        return msg

    def push_stack(self, type, name):
        """New namespace stack.

        Match a call to this with a call to pop_stack() and process the
        resulting line to declare the used variables. type must be
        'module', 'class' or 'function'.
        """
        assert type in ("module", "class", "function")
        self._stack.append((type, name, NameSpace()))

    def pop_stack(self):
        """Pop the current stack and return the namespace."""
        # Pop
        nstype, nsname, ns = self._stack.pop(-1)
        self.vars.leak_stack(ns)
        return ns

    def get_declarations(self, ns):
        """Get string with variable (and builtin-function) declarations."""
        if not ns:
            return ""
        code = []
        loose_vars = []
        for name, value in sorted(ns.items()):
            if value == 1:
                loose_vars.append(name)
            # else: pass global/nonlocal or expected to be defined in outer scope
        if loose_vars:
            code.insert(0, self.lf(f"var {', '.join(loose_vars)};"))
        return "".join(code)

    def with_prefix(self, name, new=False):
        """Add class prefix to a variable name if necessary."""
        nstype, nsname, ns = self._stack[-1]
        if nstype == "class":
            if name.startswith("__") and not name.endswith("__"):
                name = "_" + nsname + name  # Double underscore name mangling
            return nsname + ".prototype." + name
        else:
            return name

    @property
    def vars(self):
        """NameSpace instance for the current stack."""
        return self._stack[-1][2]

    def lf(self, code=""):
        """Line feed - create a new line with the correct indentation."""
        return "\n" + self._indent * "    " + code

    def pop_docstring(self, node):
        """If a docstring is present in the body of the given node, remove
        that string node and return it as a string, corrected for indentation
        and stripped.

        If no docstring is present return empty string.
        """
        docstring = ""
        if (
            node.body_nodes
            and isinstance(node.body_nodes[0], ast.Expr)
            and isinstance(node.body_nodes[0].value_node, ast.Str)
        ):
            docstring = node.body_nodes.pop(0).value_node.value.strip()
            lines = docstring.splitlines()

            def getindent(x):
                return len(x) - len(x.strip())

            if len(lines) > 1:
                indent = min([getindent(x) for x in lines[1:]])
            else:
                indent = 0

            if lines:
                lines[0] = " " * indent + lines[0]
                lines = [line[indent:] for line in lines]
            docstring = "\n".join(lines)

        return docstring

    #
    # Using stdlib
    #
    def call_std_function(self, name: str, args: list[str | ast.expr]) -> str:
        """Generate a function call from the Prescrypt standard library."""
        mangled_name = stdlib_js.FUNCTION_PREFIX + name
        js_args = [(a if isinstance(a, str) else unify(self.gen_expr(a))) for a in args]
        return f"{mangled_name}({', '.join(js_args)})"

    def call_std_method(self, base, name: str, args: list) -> str:
        """Generate a method call from the Prescrypt standard library."""
        mangled_name = stdlib_js.METHOD_PREFIX + name
        js_args = [(a if isinstance(a, str) else unify(self.gen_expr(a))) for a in args]
        args.insert(0, base)
        return f"{mangled_name}.call({', '.join(js_args)})"
