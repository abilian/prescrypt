# Prescrypt Development History (since version 0.8.0)

This document records completed work on the Prescrypt Python-to-JavaScript transpiler since 2023.

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

## Stage 6: Developer Experience

**Goal:** Transform Prescrypt from a single-file transpiler into a usable development tool.

**Completed:**
- **Error messages with source locations (6.1):**
  - Added `SourceLocation` dataclass with file, line, column info
  - Updated `PrescryptError` and `JSError` with location support
  - Added `format_with_context()` for displaying source snippets
  - Errors now show: `file.py:42:5: error: message`

- **Export generation (6.2):**
  - Added `module_mode` flag to CodeGen
  - Module-level variables: `export const x = 1` or `export let x = 1`
  - Functions: `export function greet(name) { ... }`
  - Classes: `export const Person = function () { ... }`
  - Nested definitions not exported

- **Import code generation (6.3):**
  - `import foo` → `import * as foo from './foo.js'`
  - `from foo import bar` → `import { bar } from './foo.js'`
  - `from foo import bar as b` → `import { bar as b } from './foo.js'`
  - `from . import foo` → `import * as foo from './foo.js'`
  - `from ..bar import baz` → `import { baz } from '../bar.js'`
  - `from foo import *` → namespace import with `Object.assign`

- **JS FFI (6.4):**
  - `import js` recognized as FFI module (no output)
  - `js.console.log(x)` → `console.log(x)` (prefix stripped)
  - `js.document.getElementById("app")` → raw JS access
  - Supports aliased imports: `import js as javascript`

- **Module resolution (6.5):**
  - Created `ModuleResolver` class in `front/passes/resolver.py`
  - Resolves relative imports (`.`, `..`)
  - Resolves absolute imports in source_dir and module_paths
  - Package support: `__init__.py` → `index.js`
  - Verifies module existence for correct package detection

- **Multi-file CLI (6.6):**
  - Rewrote CLI with argparse
  - `py2js input.py -o output.js` (single file)
  - `py2js src/ -o dist/` (directory compilation)
  - Options: `-m` (module mode), `-M` (module paths), `--no-stdlib`, `--no-tree-shake`, `--no-optimize`, `-v`, `-q`
  - Automatic `__init__.py` → `index.js` conversion
  - Skips `__pycache__` and hidden directories

- **E2E testing:**
  - 12 tests verifying multi-file compilation runs in Node.js
  - Tests: simple imports, multiple imports, nested imports, classes, constants, relative imports, chained imports, packages, aliases, mixed content

**Bug fixes during implementation:**
- Class export syntax: `export Person =` → `export const Person =`
- Package resolution: enabled `verify_exists` to detect `__init__.py`

**Test Results:** 2188 passing, 36 skipped

---

## Stage 6.7: Source Map Generation

**Goal:** Enable debugging transpiled code using original Python source.

**Completed:**
- **SourceMapGenerator class** (`src/prescrypt/sourcemap.py`):
  - VLQ (Variable Length Quantity) encoding/decoding
  - Source map V3 format generation
  - Mapping tracking (generated position → source position)
  - JSON output and file writing

- **CodeGen integration:**
  - Added `source_map` parameter to CodeGen
  - Statement-level position tracking
  - Output line counting for accurate mappings
  - Preamble offset adjustment when stdlib included

- **CLI support:**
  - Added `-s` / `--source-maps` flag
  - Generates `.js.map` files alongside `.js` files
  - Appends `//# sourceMappingURL=` comment to output
  - Works with both single file and directory compilation

- **Testing:**
  - 25 unit tests for VLQ encoding and source map generation
  - 2 CLI integration tests for source map file output

**Test Results:** 2216 passing, 36 skipped

---

## Stage 6.9: Documentation

**Goal:** Provide user-facing documentation.

**Completed:**
- Created comprehensive `docs/README.md` covering:
  - Installation and Quick Start
  - CLI Reference with all options
  - Language Support (features, unsupported, semantic differences)
  - Module System (imports, exports, packages)
  - JavaScript Interop (`import js` FFI)
  - Source Maps for debugging
  - Optimization (tree-shaking, constant folding)
  - Troubleshooting guide
  - Practical examples (browser app, Node.js CLI, multi-file project)

---

## Stage 6.10: Strict Mode & MkDocs

**Goal:** ES6 strict mode compatibility and production documentation site.

**Completed:**
- **Strict mode bug fix:**
  - Fixed undeclared variable errors in ES6 modules (strict mode)
  - `_make_iterable()` now declares temp variables with `let`
  - `gen_while()` else clause declares dummy variable with `let`
  - Added 8 strict mode tests to prevent regression

- **MkDocs documentation site:**
  - Configured Material for MkDocs theme with dark mode support
  - Created modular documentation structure:
    - Getting Started: installation.md, quickstart.md
    - User Guide: overview.md, cli.md, language-support.md, modules.md, js-interop.md, source-maps.md, optimization.md, troubleshooting.md
    - Examples: browser-app.md, nodejs-cli.md, multi-file.md
    - Reference: features.md, limitations.md, differences.md
    - Developer Guide: developers.md (architecture, adding features)
  - Features: search, code highlighting, navigation, tabs

- **Browser demo (`demos/browser/`):**
  - Todo list application demonstrating browser capabilities
  - Makefile with build/serve/watch targets
  - Factory function pattern for event handlers (lambda workaround)

**Test Results:** 2224 passing, 36 skipped

---

## Stage 7: Type-Informed Code Generation

**Goal:** Generate cleaner JavaScript by using type information to emit native operators instead of runtime helpers.

**Completed:**

- **Phase 1 - Arithmetic optimization** (`codegen/_expressions/ops.py`):
  - Created `codegen/type_utils.py` with type checking helpers
  - `+` uses native operator when both operands are `Int`, `Float`, or `String`
  - `*` uses native operator for numeric types
  - `*` uses `.repeat()` for string repetition (`str * int`)
  - Falls back to `_pyfunc_op_add`/`_pyfunc_op_mul` for unknown types

- **Phase 2 - Enhanced type inference** (`front/passes/type_inference.py`):
  - Added `BUILTIN_RETURN_TYPES` map (30+ builtins):
    - Type constructors: `int()`, `str()`, `float()`, `bool()`, etc.
    - Numeric: `len()`, `abs()`, `round()`, `sum()`, `ord()`, `chr()`
    - Sequences: `range()`, `enumerate()`, `zip()`, `map()`, `filter()`, `sorted()`
  - Added `METHOD_RETURN_TYPES` map (50+ methods):
    - String methods: `upper()`, `lower()`, `strip()`, `split()`, `find()`, `count()`, etc.
    - List methods: `copy()`, `index()`, `count()`
    - Dict methods: `keys()`, `values()`, `items()`, `copy()`
  - Improved `visit_BinOp` with proper arithmetic type rules:
    - Numeric promotion: `Int + Float` → `Float`
    - Division always returns `Float`
    - Floor division/modulo preserve `Int` when both operands are `Int`
  - Added scope tracking for variable types (propagates through assignments)

- **Phase 3 - Equality optimization** (`codegen/_expressions/ops.py`):
  - `==` uses `===` when both operands are primitives (`Int`, `Float`, `String`, `Bool`)
  - `!=` uses `!==` for primitives
  - Falls back to `_pyfunc_op_equals` for lists, dicts, and unknown types

- **Phase 4 - F-string optimization** (`codegen/_expressions/f_strings.py`):
  - F-strings with primitive-typed interpolations use direct concatenation
  - `f"Hello, {name}!"` → `('Hello, ' + name + '!')` when `name: str`
  - Falls back to `_pymeth_format` for format specs (`.2f`) or conversions (`!r`)

- **Type inference pipeline integration:**
  - Added `TypeInference().visit(tree)` to `compiler.py` after Binder pass
  - Type information flows from literals → variables → expressions → code generation

- **Phase 5 - print/str optimization** (`codegen/stdlib_py/functions.py`, `codegen/stdlib_py/constructors.py`):
  - `print()` skips `_pyfunc_str` wrapper for primitive types (Int, Float, String, Bool)
  - `str()` uses native `String()` for numbers/bools, passthrough for strings
  - Function return type annotations now propagate to call sites
  - Fixed: `_set_var_type(node.name, ...)` in `visit_FunctionDef` registers return type in scope

- **Documentation updates:**
  - Added "Type-Informed Code Generation" section to `docs/guide/optimization.md`
  - Updated `README.md` example to show optimized output
  - Updated `docs/guide/language-support.md` with type annotation tips
  - Updated feature tables in `docs/index.md`

**Test Results:** 1207 passing, 31 skipped

**New tests added:** 144
- `test_type_optimized_codegen.py`: 31 tests (Phase 1)
- `test_enhanced_type_inference.py`: 35 tests (Phase 2)
- `test_equality_optimization.py`: 27 tests (Phase 3)
- `test_fstring_optimization.py`: 30 tests (Phase 4)
- `test_print_str_optimization.py`: 21 tests (Phase 5)

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
| 6 | 2188 | ES6 modules, multi-file CLI |
| 6.7 | 2216 | Source map generation |
| 6.10 | 2224 | Strict mode fix, MkDocs docs |
| 7 | 1207 | Type-informed code generation |

**Total lines cleaned:** 330+
**Coverage:** 83%

## Key Design Decisions

1. **Scope System:** Two distinct systems - semantic scope (Binder) and codegen scope (NameSpace)
2. **Tree-shaking:** On by default, dramatically reduces output size
3. **Pattern Matching:** Used throughout for type-safe, readable code
4. **Constant Folding:** Compile-time evaluation of constant expressions
5. **Special Methods:** Runtime dispatch via `op_*` functions in stdlib
6. **Type-Informed Codegen:** Use native JS operators when types are known, safe fallback to helpers otherwise
