# Prescrypt TODO

**Current Status:** v0.9.5 (in progress) | **Tests:** 2639 passing, 0 skipped | **Coverage:** 89%

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

### Variable Scoping ✓ Fixed

- [x] **Loop variable scoping:** Fixed in v0.9.4 - Loop variables and variables assigned inside loops are now properly hoisted to function scope, matching Python's scoping semantics.

### JS Interop (Fixed in v0.9.3)

- [x] **`for x in js_obj` iteration:** Now works - plain objects are automatically converted to `Object.keys()`
- [x] **`.get(key, default)` on JS objects:** Fixed - dict methods now check for native method before calling, preventing "apply undefined" errors

### Compatibility

- [x] **Python 3.14 support:** Fixed deprecation warnings in AST conversion. Operator nodes no longer receive `lineno`/`col_offset` kwargs. All 2639 tests pass on Python 3.14.2.

### Runtime & Stdlib Issues (discovered during tryalgo tests)

These issues were found while creating golden tests for the tryalgo algorithms:

- [x] **`int(boolean)` returns NaN:** Fixed - `int()` now handles booleans properly using type checking.

- [x] **`while array:` always truthy:** Fixed - `while` loops now use `gen_truthy()` for proper Python truthiness semantics.

- [x] **`float('inf')` not defined:** Fixed - both compile-time constants and `float('inf')` now produce `Infinity` in JS.

- [x] **`str.startswith(s, offset)` broken:** Fixed - `startswith()` and `endswith()` now support optional `start` and `end` parameters.

- [x] **`min()`/`max()` on tuple generators:** Fixed - `min()` and `max()` now use proper lexicographic comparison for tuples/arrays, support `key` function, and support `default` for empty iterables.

- [ ] **Large integer precision loss:** JavaScript numbers lose precision beyond 2^53. Modular arithmetic with large numbers gives wrong results.
  - Note: This is a fundamental JS limitation. Consider documenting or using BigInt for specific cases.

- [x] **`set.isdisjoint()` not implemented:** Fixed - added `isdisjoint()`, `issubset()`, `issuperset()`, `union()`, `intersection()`, `difference()`, `symmetric_difference()`, `add()`, `discard()`. Also fixed `in` operator for sets.

- [x] **`bisect_left`/`bisect_right` not implemented:** Fixed - added `bisect_left`, `bisect_right`, `bisect`, `insort_left`, `insort_right`, `insort` functions.

## Recently Completed (v0.9.5 internal)

### Code Quality Improvements ✓ (from code review 2026-W8)

- [x] **Utility methods for codegen:** Added `gen_expr_str()` and `gen_expr_unified()` to CodeGen (replaced 132 occurrences of `flatten(codegen.gen_expr(...))`)
- [x] **JS FFI consolidation:** Moved `is_js_ffi_chain()` and `strip_js_ffi_prefix()` from duplicated module functions into CodeGen class
- [x] **Type decision helpers:** Added `can_use_native_add()`, `get_mult_strategy()`, `can_use_native_compare()` to `type_utils.py`
- [x] **ModuleResolver caching:** Cached resolver instances in CodeGen for faster multi-file compilation
- [x] **Documentation:** Added comprehensive CodeGen class docstring documenting Binder contract
- [x] **Removed unused code:** Removed `Function` AST node and `is_captured` Variable field
- [x] **Security fix:** Fixed shell injection in `mro_graph.py` (dev tool)

---

## Next Up (v0.9.6 → v1.0)

### High Priority

| Task | Effort | Description |
|------|--------|-------------|
| ~~Python 3.14 compatibility~~ | ~~Low~~ | ~~Test and fix any import/AST changes~~ ✓ Done |
| CodeWriter refactor | High | Replace string returns with buffer-based writer |

### Medium Priority

| Task | Effort | Description |
|------|--------|-------------|
| Precedence-based parentheses | Medium | Replace regex-based `unify()` with proper precedence |
| Stdlib manifest | Low | Replace regex parsing with explicit TOML manifest |
| Event handler `event` param | Low | Auto-pass `event` to handler functions |
| Async/await polish | Medium | Test and document `fetch` patterns |
| Security tests | Low | Add tests for string escaping, identifier mangling |

### Lower Priority

| Task | Effort | Description |
|------|--------|-------------|
| Multiple inheritance (MRO) | High | Complex - may not be worth it |
| VSCode extension | Medium | Syntax highlighting, error display |
| Interactive docs | Medium | Compile examples in browser |

---

## Completed Features

<details>
<summary>Build & Tooling ✓ (click to expand)</summary>

- [x] **Built-in bundling** ✓ (v0.9.5)
  - `py2js entry.py -o out.js --bundle -M src/`
  - Recursively resolves imports and bundles all modules
  - Combined tree-shaking across all modules
- [x] **Watch mode for CLI** ✓ (v0.9.4)
  - `py2js src/ -o dist/ --watch`
  - Uses watchdog if available, falls back to polling
- [x] **Reserved word handling** ✓ (v0.9.3)
  - Auto-rename JavaScript reserved words (`default`, `switch`, `interface`, etc.)

</details>

<details>
<summary>JS FFI Enhancements ✓ (click to expand)</summary>

- [x] **`JS` type annotation** ✓ (v0.9.3)
  - `result: JS = callback()` - compiler treats `result.get()` as JS method
- [x] **`from js import document, fetch`** ✓ (v0.9.3)
  - Direct imports work as native JS globals

</details>

<details>
<summary>Language Features ✓ (click to expand)</summary>

- [x] **Dataclasses support** ✓ (v0.9.4)
  - `@dataclass` generates `__init__`, `__repr__`, `__eq__`
- [x] **`__slots__` support** ✓ (v0.9.4)
  - Restricts attributes using `Object.seal()`
- [x] **`match` statement (full)** ✓ (v0.9.4)
  - All patterns: literal, OR, capture, wildcard, sequence, starred, mapping, class, guards

</details>

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
- [x] Enhanced JS FFI (`from js import document, fetch`) ✓ (done in v0.9.3)
- [ ] Event handler compilation with `event` parameter
- [ ] Async/await with `fetch` (test and polish)
- [ ] Module splitting (`@client` code to separate JS file)
- [x] Dataclass support ✓ (done in v0.9.4)

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
