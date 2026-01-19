# Prescrypt TODO

**Current Status:** v0.9.1 (released) | **Tests:** 2409 (2381 passing, 28 skipped) | **Coverage:** 89%

See `notes/history.md` for completed work (Stages 0-6).

---

## Recently Completed

### Stage 7: Async Support ✓
- [x] `async def` functions
- [x] `await` expressions
- [x] `async for` statements
- [x] `async with` statements

### Stage 8: Generators ✓
- [x] `yield` expression handler
- [x] `yield from` delegation
- [x] Generator expressions
- [x] Generator protocol (`__next__`, `send`, `throw`, `close`)
- [x] `GeneratorExit` exception

### Recent Fixes (v0.9.1)
- [x] `func(**kwargs)` calls with `call_kwargs` runtime helper
- [x] Dict unpacking `{**d1, **d2}` in literals
- [x] `del lst[idx]` and `del lst[start:end]`
- [x] `int.from_bytes` class method
- [x] Type-informed operator codegen (optimizations)
- [x] Remove dead code: `src/prescrypt/namespace.py`

### Short-term Fixes (v0.9.2) ✓
- [x] Remove dependencies: `buildstr`, `plum-dispatch`, `dukpy` (zero runtime deps)
- [x] Lambda with default arguments (`lambda x=1: x`)
- [x] `__all__` to control module exports
- [x] Context manager protocol (`__enter__`/`__exit__`)

---

## Future Enhancements

- [ ] Dataclasses and/or attrs support
- [ ] `__slots__` support
- [ ] Multiple inheritance (MRO)
- [ ] `match` statement (structural pattern matching)
- [ ] Watch mode for CLI

---

## Class System Enhancements

**Goal:** Full class support with decorators and special methods.

### Phase 1: `super()` Support
- [ ] Detect `super` as special function in `gen_call_named()`
- [ ] Generate `this._base_class.METHOD.call(this, args)`
- [ ] Enable test: `class_super.py`

### Phase 2: `@staticmethod` / `@classmethod`
- [ ] Remove "Class decorators not supported" error
- [ ] Handle `@staticmethod` - no `this` binding
- [ ] Handle `@classmethod` - pass constructor as `cls`
- [ ] Enable test: `class_staticclassmethod.py`

### Phase 3: `@property` Decorator
- [ ] Detect `@property` and `.setter`/`.deleter`
- [ ] Generate `Object.defineProperty()` calls
- [ ] Enable test: `builtin_property.py`

### Phase 4: Special Method Dispatch
- [ ] `__getitem__` / `__setitem__` dispatch
- [ ] `__len__` in `len()` calls
- [ ] `__eq__` in equality comparisons
- [ ] Enable tests: `class_binop.py`, `getitem.py`

---

## Demos & Use Cases

Develop demos for various use cases:

1. Interactive Python learning platforms
2. Shared validation libraries (backend + frontend)
3. Lightweight data dashboards
4. Browser extensions in Python
5. Scientific simulations / educational widgets
6. Edge computing (Cloudflare Workers)

---

## Full-Stack Web Framework (POC)

**Goal:** Python for both server and client with `@client`/`@server` decorators.

See `local-notes/proposals/web-framework-proposal.md` for full plan.

### Prerequisites (Prescrypt improvements)
- [ ] Enhanced JS FFI (`from js import document, fetch`)
- [ ] Event handler compilation with `event` parameter
- [ ] Async/await with `fetch` (test and polish)
- [ ] Module splitting (`@client` code to separate JS file)
- [ ] Dataclass support

### Framework Phases
- [ ] Phase 1: Foundation (client-side examples)
- [ ] Phase 2: `@client` decorator with validation
- [ ] Phase 3: Build system and dev server
- [ ] Phase 4: Server RPC communication
- [ ] Phase 5: Reactive state synchronization

---

## Known Limitations (Won't Fix)

These are fundamental Python/JavaScript differences:

1. **Float display:** `4.0` shows as `4` (JS doesn't distinguish)
2. **ZeroDivisionError:** `100/0` returns `Infinity` in JS
3. **`print(end="")`:** `console.log` always adds newline
