TODO
====

## Short term

- [ ] Unify `stdlib_js` and `stdlib_py` into one Class.
- [ ] Minimize stdlib code generation.
- [ ] Pre-mangle stdlib names / find a way to awoy NS pollution (?)
- [ ] Leverage scope info collected during parsing.
- [ ] Add support for `global`, `nonlocal` and `super()`.

## Long term

- [ ] Add support for `async` and `await`.
- [ ] Add support for `yield` and `yield from`.
- [ ] Add support for `with` statement.
- [ ] Add support for dataclasses and/or attrs.
- [ ] Add support for `@property` and `@classmethod`.
- [ ] Add support for `__slots__`.
- [ ] Add support for more magic methods.
- [ ] Implement and leverage type annotations and inference.

## Done

- [x] List comprehensions.


## Notes

```python
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
#     def gen_Yield(self, node): ...
#     def gen_YieldFrom(self, node): ...
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
```
