# Prescrypt Development History

This document records completed work on the Prescrypt Python-to-JavaScript transpiler since late 2025.

---

## Stage 0: Foundation Cleanup

**Goal:** Remove noise, establish clean baseline.

**Completed:**
- Enabled Binder pass in compiler pipeline
- Fixed `gen_attribute` broken references
- Removed debug print statements
- Removed duplicate scope implementations:
  - `front/passes/scope.py` (duplicate of Binder)
  - `front/passes/scopes.py` (unused ScopedMap)
  - `front/passes/symbol.py` (only used by scopes.py)
- Cleaned 330+ lines of dead code:
  - `functions.py`: 240 lines removed
  - `calls.py`: 90 lines removed (`_OLD_gen_call`)

**Test Results:** 629 passing, 9 skipped

---

## Stage 1: Scope System Consolidation

**Goal:** Single source of truth for variable scope information.

**Completed:**
- Enhanced Binder output:
  - Added `Variable.declaration_kind` property: `"const"` | `"let"` | `"none"`
  - Added `Variable.is_captured` field for closure tracking
  - Added `Scope.is_global()` method
  - Binder attaches `_scope` to Module node
- Used scope info in CodeGen:
  - Added `CodeGen._binding_scope` to access Binder's scope
  - Added `CodeGen.get_declaration_kind(name)` method
  - Assignment handler uses `const`/`let` based on analysis
- Added 7 tests for `declaration_kind`
- Single-assignment variables emit `const`, multi-assignment emit `let`

**Test Results:** 629 passing

---

## Stage 2: Statement Handlers Stabilization

**Goal:** All statement handlers work correctly with new architecture.

**Completed:**
- Fixed `gen_for`:
  - `for x in range(n)` patterns
  - `for x in iterable` patterns
  - `for i, x in enumerate(items)` with unpacking
  - `else` clause (fixed break detection bug)
- Fixed `gen_try`:
  - Basic try/except
  - Multiple except clauses
  - Finally clause
  - Exception capture `except E as e`
- Added `gen_with` handler for context managers
- Integrated `gen_global` / `gen_nonlocal`:
  - Handlers generate comments
  - Binder marks outer scope variables as mutable
  - CodeGen uses `let` for modified globals/nonlocals
- Fixed `gen_if` elif handling (string slicing bug)
- Added 42+ tests including 12 regression tests

**Test Results:** 1336 passing, 645 skipped

---

## Stage 3: Expression Handlers Cleanup

**Goal:** Consistent, correct expression handling.

**Completed:**
- Fixed expression handlers:
  - f-string handler (missing `_format_spec_to_string`)
  - `call_std_method` parameter order
  - %-formatting string slicing bug
  - Return statement missing `flatten()` call
- Verified operator precedence works correctly
- Verified comparison chain desugaring works
- String formatting:
  - f-strings: `f"hello {name}"`
  - %-formatting: `"hello %s" % name`
  - `.format()`: `"hello {}".format(name)`
- Added 22 new tests for strings/operators/comparisons

**Test Results:** 1506 passing, 647 skipped

---

## Stage 4: Class System

**Goal:** Reliable class transpilation for common patterns.

**Completed:**
- Basic classes:
  - `class Foo:` with `__init__`
  - Instance methods with `self` → `this` conversion
  - Instance attributes via `self.x`
  - Auto-instantiation without `new` keyword
- Inheritance:
  - Single inheritance with `super()`
  - Multi-level inheritance (3+ levels)
  - Method override
  - `super().__init__()` calls via `_pyfunc_super_proxy` runtime
- Decorators:
  - `@staticmethod`
  - `@classmethod`
  - `@property` (getter and setter)
- Special methods:
  - `__str__` / `__repr__`
  - `__len__` via `op_len()` runtime
  - `__eq__` via `op_equals()` check
  - `__getitem__` / `__setitem__` via `op_getitem()`/`op_setitem()`
- Bug fixes:
  - `pop_ns()` namespace stack bug
  - Method generation to attach to prototype
  - Class constructor auto-instantiate without `new`
  - Function namespace for method-local variables
  - Class attribute assignments (both constructor and prototype)
- Added 36 tests for classes, inheritance, decorators, and special methods

**Test Results:** 1506 passing, 647 skipped

---

## Stage 4.5: Bug Fixes & Type Inference

**Goal:** Fix integration test failures and improve type inference.

**Completed:**
- Type inference pass (`front/passes/type_inference.py`):
  - Added `Unknown`, `List`, `Dict`, `Tuple` type singletons
  - Made type inference robust (assigns `Unknown` instead of crashing)
  - Added handlers for all expression types (comprehensions, subscripts, etc.)
- Bug fixes:
  - Augmented assignment desugaring (`x += 1` now marks `x` as `let`)
  - Return statement missing `flatten()` call
- Import statement handlers:
  - `from __future__ import annotations` silently ignored
  - Other imports generate comments
- All 8 integration tests (P1-P8) passing

**Test Results:** 1698 passing, 455 skipped

---

## Stage 5: Standard Library Optimization

**Goal:** Optimize stdlib for size and performance.

**Completed:**
- **Tree-shaking:**
  - Track used functions/methods during codegen
  - Parse and resolve transitive dependencies in `StdlibJs`
  - Results: 94-99% size reduction (33KB → 177 bytes for simple code)
  - `tree_shake=True` parameter (default), can disable with `tree_shake=False`

- **Constant folding** (`front/passes/constant_folder.py`):
  - Arithmetic: `1 + 2 * 3` → `7`
  - Strings: `"a" + "b"` → `"ab"`, `"x" * 3` → `"xxx"`
  - Booleans: `True and False` → `False`, short-circuit evaluation
  - Comparisons: `1 < 2` → `True`
  - Subscripts: `"hello"[0]` → `"h"`, `[1,2,3][1]` → `2`
  - Conditionals: `x if True else y` → `x`
  - Compile-time error detection (division by zero)

- **Function inlining:**
  - `len([1,2,3])` → `3`, `len("hello")` → `5`
  - `min(1,2,3)` → `1`, `max(1,2,3)` → `3`
  - `abs(-5)` → `5`, `sum([1,2,3])` → `6`
  - `bool(0)` → `False`, `int("123")` → `123`
  - `chr(65)` → `"A"`, `ord("A")` → `65`

- **Configurable namespace prefixes:**
  - `function_prefix` parameter (default `_pyfunc_`)
  - `method_prefix` parameter (default `_pymeth_`)
  - Supports custom/minified prefixes

- **Code quality improvements:**
  - Refactored `constant_folder.py` with declarative tables + pattern matching
  - Reduced from 496 to 348 lines (30% reduction)
  - Eliminated most `isinstance()` calls using pattern matching
  - Improved `type_inference.py` with pattern matching helpers

**Test Results:** 2068 passing, 36 skipped

---

## Summary Statistics

| Stage | Tests Passing | Key Achievement |
|-------|---------------|-----------------|
| 0 | 629 | Clean baseline |
| 1 | 629 | Smart const/let declarations |
| 2 | 1336 | All statement handlers working |
| 3 | 1506 | All expression handlers working |
| 4 | 1506 | Full class system with inheritance |
| 4.5 | 1698 | Robust type inference |
| 5 | 2068 | Optimized stdlib, constant folding |

**Total lines cleaned:** 330+
**Total tests added:** 1400+
**Coverage:** 83%

## Key Design Decisions

1. **Scope System:** Two distinct systems - semantic scope (Binder) and codegen scope (NameSpace)
2. **Tree-shaking:** On by default, dramatically reduces output size
3. **Pattern Matching:** Used throughout for type-safe, readable code
4. **Constant Folding:** Compile-time evaluation of constant expressions
5. **Special Methods:** Runtime dispatch via `op_*` functions in stdlib
