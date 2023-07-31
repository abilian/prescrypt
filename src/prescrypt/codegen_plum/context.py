from prescrypt.codegen import gen_expr
from prescrypt.passes.scope import Scope


class Context:
    _pscript_overload = False

    def __init__(self, scope: Scope):
        self.scope = scope

        self._indent = 0
        self._dummy_counter = 0

        self._pscript_overload = False
        self._methods = {}
        self._functions = {}
        self._seen_func_names = set()
        self._seen_class_names = set()
        self._std_methods = set()

    def gen_expr(self, expr):
        return gen_expr(expr, self)

    def gen_stmt(self, stmt):
        from prescrypt.codegen import gen_stmt
        return gen_stmt(stmt, self)

    #
    # Output control
    #
    def indent(self):
        """Increase indentation."""
        self._indent += 1

    def dedent(self):
        """Decrease indentation."""
        self._indent -= 1

    def lf(self, code=""):
        """Line feed - create a new line with the correct indentation."""
        return "\n" + self._indent * "    " + code
