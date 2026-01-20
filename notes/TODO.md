# Prescrypt TODO

**Current Status:** v0.9.2 (in progress) | **Tests:** 2385 passing, 28 skipped | **Coverage:** 89%

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

### Class System Enhancements (v0.9.2) ✓
- [x] `super()` support with `super_proxy` runtime
- [x] `@staticmethod` and `@classmethod` decorators
- [x] `@property` decorator with getter/setter/deleter
- [x] Special method dispatch (`__eq__`, `__lt__`, `__gt__`, `__le__`, `__ge__`)
- [x] Container special methods (`__getitem__`, `__setitem__`, `__delitem__`)

---

## Missing Features (discovered via demos)

### Tuple Unpacking (High Priority)

These patterns don't work and require manual workarounds:

- [ ] **Assignment unpacking:** `a, b = func()` → must use `r = func(); a = r[0]; b = r[1]`
- [ ] **For loop unpacking:** `for k, v in dict.items()` → must use `for k in dict: v = dict[k]`
- [ ] **Enumerate unpacking:** `for i, x in enumerate(lst)` → must use `for i in range(len(lst)): x = lst[i]`
- [ ] **Nested unpacking:** `for i, (k, v) in enumerate(d.items())` → not supported at all
- [ ] **Chained assignment with subscripts:** `a[0] = a[1] = False` → must split into two statements

### F-String Format Specifiers (Medium Priority)

These format specifiers cause issues (compiler hangs or incorrect output):

- [ ] **Thousands separator:** `f"{x:,}"` → use `str(x)` instead
- [ ] **Fixed precision:** `f"{x:.2f}"` → use `str(round(x, 2))` instead
- [ ] **Width/alignment:** `f"{x:>10}"` or `f"{x:2d}"` → use `str(x).rjust(10)` instead
- [ ] **Combined:** `f"{x:,.0f}"` → use `str(int(x))` instead

### Variable Scoping (Low Priority)

- [ ] **Loop variable redeclaration:** Variables declared in one loop aren't re-declared in subsequent loops with the same name, causing strict mode errors. Workaround: use different variable names.

### Recently Fixed

- [x] **Class `var` declaration:** Classes weren't declared with `var`, causing "assignment to undeclared variable" in strict mode. Fixed in `codegen/_statements/classes.py`.

## Future Enhancements

- [ ] Dataclasses support
- [ ] `__slots__` support
- [ ] Multiple inheritance (MRO)
- [ ] `match` statement (structural pattern matching)
- [ ] Watch mode for CLI

---

## Demos & Use Cases ✓

Demos created in `demos/` directory:

1. [x] **python-playground** - Interactive Python learning (server-side compilation)
2. [x] **validation-library** - Shared validation (backend + frontend)
3. [x] **data-dashboard** - Sales analytics with Canvas charts
4. [x] **browser-extension** - Chrome/Firefox page analyzer
5. [x] **simulation** - Predator-prey Lotka-Volterra model
6. [x] **edge-worker** - Cloudflare Workers (bot detection, A/B testing)

See `demos/README.md` for documentation.

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
