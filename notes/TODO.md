# Prescrypt TODO

**Current Status:** v0.9.4 (in progress) | **Tests:** 2444 passing, 28 skipped | **Coverage:** 89%

See `notes/history.md` for completed work (Stages 0-6).

---

## Recently Completed (v0.9.2)

### JS FFI Fixes ✓
- [x] **`js.X.new()` constructor syntax:** `js.Object.new()` → `new Object()`, `js.Date.new(2024, 0, 15)` → `new Date(2024, 0, 15)`
- [x] **JS FFI method passthrough:** Methods like `.get()`, `.keys()`, `.values()`, `.clear()` no longer converted to `_pymeth_*` wrappers
- [x] **Browser extension API compatibility:** `js.chrome.storage.local.get('key')` now works correctly

### Assignment & Formatting Enhancements ✓
- [x] **Chained assignment with subscripts/attributes:** `a[0] = a[1] = value` and `obj.x = obj.y = value`
- [x] **F-string thousands separator:** `f"{x:,}"` → `"1,234,567"`
- [x] **F-string width/alignment:** `f"{x:>10}"`, `f"{x:<10}"`, `f"{x:^10}"`
- [x] **F-string custom fill:** `f"{x:*>5}"` → `"***42"`
- [x] **F-string zero padding:** `f"{x:05}"` → `"00042"`
- [x] **F-string combined formats:** `f"{x:,.2f}"` → `"1,234,567.89"`

### Class System Enhancements ✓
- [x] `super()` support with `super_proxy` runtime
- [x] `@staticmethod` and `@classmethod` decorators
- [x] `@property` decorator with getter/setter/deleter
- [x] Special method dispatch (`__eq__`, `__lt__`, `__gt__`, `__le__`, `__ge__`)
- [x] Container special methods (`__getitem__`, `__setitem__`, `__delitem__`)

### Short-term Fixes ✓
- [x] Remove dependencies: `buildstr`, `plum-dispatch`, `dukpy` (zero runtime deps)
- [x] Lambda with default arguments (`lambda x=1: x`)
- [x] `__all__` to control module exports
- [x] Context manager protocol (`__enter__`/`__exit__`)
- [x] Class `var` declaration in strict mode

### Previous Milestones ✓

<details>
<summary>Stage 7-8: Async & Generators (click to expand)</summary>

- [x] `async def` functions, `await` expressions
- [x] `async for` and `async with` statements
- [x] `yield` and `yield from` support
- [x] Generator protocol (`__next__`, `send`, `throw`, `close`)
- [x] `GeneratorExit` exception

</details>

<details>
<summary>v0.9.1 Fixes (click to expand)</summary>

- [x] `func(**kwargs)` calls with `call_kwargs` runtime helper
- [x] Dict unpacking `{**d1, **d2}` in literals
- [x] `del lst[idx]` and `del lst[start:end]`
- [x] `int.from_bytes` class method
- [x] Type-informed operator codegen (optimizations)

</details>

---

## Known Issues

### Variable Scoping (Low Priority)

- [ ] **Loop variable redeclaration:** Variables declared in one loop aren't re-declared in subsequent loops with the same name, causing strict mode errors. Workaround: use different variable names.

### JS Interop (Fixed in v0.9.3)

- [x] **`for x in js_obj` iteration:** Now works - plain objects are automatically converted to `Object.keys()`
- [x] **`.get(key, default)` on JS objects:** Fixed - dict methods now check for native method before calling, preventing "apply undefined" errors

### Compatibility

- [ ] **Python 3.14 support:** Test and fix any import errors on Python 3.14.

## Future Enhancements

### Build & Tooling
- [ ] **Built-in bundling:** Bundle multi-file projects into a single JS file (currently requires external bundler like esbuild)
- [x] **Watch mode for CLI:** Auto-recompile on file changes ✓ (done in v0.9.4)
  - `py2js src/ -o dist/ --watch`
  - Uses watchdog if available, falls back to polling
- [x] **Reserved word handling:** Auto-rename JavaScript reserved words (`default`, `switch`, `interface`, etc.) - done in v0.9.3

### JS FFI Enhancements
- [x] **`JS` type annotation:** Mark variables as JavaScript objects to bypass Python stdlib transformations ✓
  - Example: `result: JS = callback()` - compiler treats `result.get()` as JS method, not `_pymeth_get`
  - Useful for stored references, callback return values, and any JS object not from direct `js.X` chain
- [x] **`from js import document, fetch`:** Direct imports from `js` module ✓
  - Imported names work as native JS globals
  - Supports aliases and `.new()` constructor

### Language Features
- [x] **Dataclasses support** ✓ (done in v0.9.4)
  - `@dataclass` generates `__init__`, `__repr__`, `__eq__`
  - Supports default values, `eq=False`, `frozen=True`
- [x] **`__slots__` support** ✓ (done in v0.9.4)
  - Restricts attributes to declared slots using `Object.seal()`
  - Supports list, tuple, or single string syntax
- [x] **`match` statement** ✓ (done in v0.9.4)
  - Literal, OR, capture, wildcard, sequence patterns
  - Mapping patterns (`case {"x": x, "y": y}:`)
  - Class patterns (`case Point(x=x, y=y):`)
  - Guard clauses supported
- [ ] Multiple inheritance (MRO)

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
