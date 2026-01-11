TODO
====

## Short term (Stage 5)

- [ ] Unify `stdlib_js` and `stdlib_py` into single `stdlib/` directory
- [ ] Minimize stdlib code generation (tree-shake unused functions)
- [ ] Pre-mangle stdlib names / find a way to avoid NS pollution
- [ ] Add more compile-time optimizations

## Medium term (Stage 6)

- [ ] Add support for `async` and `await`
- [ ] Add support for `yield` and `yield from` (generators)
- [ ] Add `gen_async_for` and `gen_async_with`

## Long term (Stage 7+)

- [ ] Add support for dataclasses and/or attrs
- [ ] Add support for `__slots__`
- [ ] Error messages with source locations
- [ ] Source map generation
- [ ] Watch mode, multi-file support
- [ ] Documentation

## Done

### Stage 4.5 (2025-01-11)
- [x] Type inference pass (handles all expression types)
- [x] Fixed augmented assignment desugaring bug
- [x] Fixed return statement code generation
- [x] Import statement handlers (`from __future__` ignored)

### Stage 4 (2025-01-10)
- [x] Full class system with inheritance
- [x] `super()` support (including multi-level inheritance)
- [x] `@staticmethod`, `@classmethod`, `@property` decorators
- [x] Special methods: `__len__`, `__eq__`, `__getitem__`, `__setitem__`

### Stage 3 (2025-01-10)
- [x] f-strings, %-formatting, `.format()`
- [x] Operator precedence verification
- [x] Comparison chain desugaring

### Stage 2 (2025-01-10)
- [x] `with` statement support
- [x] `global` and `nonlocal` support
- [x] For-else and while-else break detection

### Stage 1 (2025-01-10)
- [x] Leverage scope info collected during parsing
- [x] Smart `const`/`let` declaration based on usage

### Earlier
- [x] List comprehensions
- [x] Dict comprehensions
- [x] Set comprehensions
- [x] Generator expressions
