# from .exceptions import JSError
#
# RAW_DOC_WARNING = (
#     "Function %s only has a docstring, which used to be "
#     "intepreted as raw JS. Wrap a call to RawJS(...) around the "
#     'docstring, or add "pass" to the function body to prevent '
#     "this behavior."
# )
#
#
# class StatementCompiler:
#     # Functions and class definitions
#
#     def function_super(self, node):
#         # allow using super() in methods
#         # Note that in parse_Call() we ensure that a call using super
#         # uses .call(this, ...) so that the instance is handled ok.
#
#         if node.arg_nodes:
#             # raise JSError('super() accepts 0 or 1 arguments.')
#             pass  # In Python 2, arg nodes are provided, and we ignore them
#         if len(self._stack) < 3:  # module, class, function
#             # raise JSError('can only use super() inside a method.')
#             # We just provide "super()" and hope that the user will
#             # replace the code (as we do in the Model class).
#             return "super()"
#
#         # Find the class of this function. Using this._base_class would work
#         # in simple situations, but not when there's two levels of super().
#         nstype1, nsname1, _ = self._stack[-1]
#         nstype2, nsname2, _ = self._stack[-2]
#         if not (nstype1 == "function" and nstype2 == "class"):
#             raise JSError("can only use super() inside a method.")
#
#         base_class = nsname2
#         return f"{base_class}.prototype._base_class"
#
#     # def parse_Yield
#     # def parse_YieldFrom
#
#     def gen_await(self, node):
#         return f"await {''.join(self.parse(node.value_node))}"
#
#     def gen_global(self, names) -> str:
#         for name in names:
#             self.vars.set_global(name)
#         return ""
#
#     def gen_nonlocal(self, names) -> str:
#         for name in names:
#             self.vars.set_nonlocal(name)
#         return ""
#
#     #
#     # Utils
#     #
#     def lf(self, code=""):
#         """Line feed - create a new line with the correct indentation."""
#         return "\n" + self._indent * "    " + code
#
#     def dummy(self, name=""):
#         """Get a unique name.
#
#         The name is added to vars.
#         """
#         self._dummy_counter += 1
#         name = "stub%i_%s" % (self._dummy_counter, name)
#         self.vars.add(name)
#         return name
