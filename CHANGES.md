# Changelog

All notable changes to Prescrypt will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased (v0.9.4)

### Added

- **Watch mode**: Auto-recompile on file changes with `-w`/`--watch` flag
  - `py2js src/ -o dist/ --watch` - watch directory for changes
  - `py2js input.py --watch` - watch single file for changes
  - Uses watchdog if available for efficient file system events
  - Falls back to polling (1 second interval) if watchdog not installed
  - Works with all existing options (source maps, module mode, etc.)
- **Dataclass support**: `@dataclass` decorator generates `__init__`, `__repr__`, and `__eq__`
  - Supports fields with and without default values
  - Supports `@dataclass(eq=False)` to skip `__eq__` generation
  - Supports `@dataclass(frozen=True)` for immutable instances
  - Additional methods can be added to dataclasses
  - Works with `@classmethod` and `@staticmethod` decorators
- **`__slots__` support**: Restrict instance attributes for memory efficiency
  - `__slots__ = ['x', 'y']` prevents adding new attributes after `__init__`
  - Uses `Object.seal()` to enforce slot restrictions
  - Supports list, tuple, or single string syntax
- **Enhanced error messages**: Better error display with source context
  - Shows surrounding code lines for context
  - Highlights the error location with underlines
  - Includes hints for common mistakes (e.g., multiple inheritance)
- **Verbose/debug mode**: Show compilation stages and timing
  - `-v` shows compilation stages with timing
  - `-vv` also shows AST after each pass (truncated)
  - `--debug` or `-vvv` for full debug output
- **Match statement support**: Full Python 3.10+ structural pattern matching
  - Literal patterns: `case 0:`, `case "hello":`
  - OR patterns: `case 1 | 2 | 3:`
  - Capture patterns: `case n:`
  - Wildcard: `case _:`
  - Sequence patterns: `case [a, b]:`
  - Starred patterns: `case [first, *rest]:`, `case [*_, last]:`
  - Singleton patterns: `case None:`, `case True:`, `case False:`
  - Mapping patterns: `case {"x": x, "y": y}:`
  - Class patterns: `case Point(x=x, y=y):`
  - Guard clauses: `case n if n > 0:`

### Statistics

- 2486 tests passing, 28 skipped

## [0.9.3] - 2026-01-24

### Added

- **`JS` type annotation**: Mark variables as JavaScript objects to bypass Python stdlib transformations
  - Example: `result: JS = callback()` - compiler treats `result.get()` as native JS method, not `_pymeth_get`
  - Works with annotated assignments, function parameters, and any variable with `JS` or `JSObject` type
  - Useful for stored references from callbacks, browser APIs, and any JS object not from direct `js.X` chain
- **`from js import X` syntax**: Import JavaScript globals directly
  - Example: `from js import document, console, fetch`
  - Imported names are used as native JS globals: `document.getElementById("id")` → `document.getElementById("id")`
  - Works with aliases: `from js import document as doc`
  - Supports `.new()` constructor: `from js import Date; today = Date.new()`
- **Reserved word auto-renaming**: JavaScript reserved words (`default`, `switch`, `case`, `interface`, `export`, etc.) used as variable/function/parameter names are automatically renamed by appending underscore
  - Example: `default = 5` → `const default_ = 5`
  - Works in variable declarations, function definitions, function parameters, and tuple unpacking
  - Previously raised an error

### Fixed

- **Dict methods on non-Object JS objects**: `.get()`, `.keys()`, `.values()`, `.items()`, `.setdefault()`, `.update()`, `.popitem()` now work on any JavaScript object, not just plain `Object` instances
  - Previously failed with "can't access property 'apply'" on browser API objects
  - Methods now check if native method exists before attempting to call it
- **Type-based comparison optimization**: Removed fragile string-pattern matching (`.endswith(".length")`) in favor of proper type inference for `==`/`!=` optimization decisions

### Statistics

- 2433 tests passing, 28 skipped
- 89% code coverage

## [0.9.2] - 2026-01-20

### Added

- **`__all__` export control**: When `__all__` is defined in a module, only those names are exported in ES6 module mode
- **Context manager protocol**: `with` statements now support `__enter__` and `__exit__` methods
  - `__enter__()` return value is bound to the `as` variable
  - `__exit__(None, None, None)` called in `finally` block
  - Falls back to `.close()` for objects without context manager methods
- **Class system enhancements**:
  - `super()` support with `super_proxy` runtime helper for proper method delegation
  - `@staticmethod` decorator - methods with no `this` binding
  - `@classmethod` decorator - methods receiving constructor as first argument
  - `@property` decorator with full getter/setter/deleter support via `Object.defineProperty()`
  - Comparison special methods: `__eq__`, `__lt__`, `__gt__`, `__le__`, `__ge__` dispatch
  - Container special methods: `__getitem__`, `__setitem__`, `__delitem__` dispatch
  - Runtime helpers: `op_lt`, `op_gt`, `op_le`, `op_ge`, `op_delitem`, `op_delattr`
- **Chained assignment with subscripts/attributes**: `a[0] = a[1] = value` and `obj.x = obj.y = value` now work
- **F-string format specifiers**: Enhanced `format()` function with reasonable Python format spec support
  - Thousands separator: `f"{x:,}"` → `"1,234,567"`
  - Width/alignment: `f"{x:>10}"` → `"        42"`, `f"{x:<10}"`, `f"{x:^10}"`
  - Custom fill characters: `f"{x:*>5}"` → `"***42"`
  - Zero padding: `f"{x:05}"` → `"00042"`
  - Sign-aware padding: `f"{x:+05}"` → `"+0042"`
  - Combined formats: `f"{x:,.2f}"` → `"1,234,567.89"`
- **JS FFI `.new()` method**: `js.Object.new()` now correctly generates `new Object()`
  - Works with all constructors: `js.Date.new(2024, 0, 15)` → `new Date(2024, 0, 15)`
  - `js.Array.new(10)` → `new Array(10)`
  - `js.RegExp.new('[a-z]+', 'gi')` → `new RegExp('[a-z]+', 'gi')`

### Fixed

- **JS FFI method collision**: JS FFI calls (`js.X.method()`) no longer incorrectly convert methods like `.get()`, `.keys()`, `.values()`, `.clear()` to Python stdlib wrappers
  - `js.chrome.storage.local.get('key')` → `chrome.storage.local.get('key')` (previously used `_pymeth_get`)
  - `js.Object.keys(obj)` → `Object.keys(obj)` (previously used `_pymeth_keys`)
  - Affects all browser extension APIs that have Python-like method names

### Changed

- **Zero runtime dependencies**: Removed `buildstr`, `plum-dispatch`, and `dukpy`
- **Removed dead code**: `src/prescrypt/namespace.py` (unused, superseded by binder)
- **Comparison operators**: Now use runtime helpers for non-primitive types to support special methods

### Statistics

- 2414 tests passing
- Zero runtime dependencies

## [0.9.1] - 2026-01-19

### Added

#### Language Features
- **Set comprehensions**: `{x for x in items}` now compiles to JavaScript `Set`
- **`func(**kwargs)` calls**: Proper keyword argument unpacking using `call_kwargs` runtime helper
  - Functions now store parameter names as `__args__` metadata
  - `greet(**{"name": "World"})` correctly maps kwargs to positional args
- **Dict unpacking in literals**: `{**dict1, "key": val, **dict2}` using `Object.assign()`
- **`del` statement enhancements**:
  - `del lst[idx]` uses `splice()` for array element deletion
  - `del lst[start:end]` for slice deletion
  - `del d[key]` for dict key deletion
- **Decorator syntax**: `@decorator` on functions now applies decorators correctly
- **MatMult operator**: `a @ b` matrix multiplication operator (delegates to `__matmul__`)
- **Ellipsis literal**: `...` and `Ellipsis` now compile to `Symbol.for('Ellipsis')`
- **Exception chaining**: `raise X from Y` now sets `__cause__` on the exception
- **Generator expressions**: `(x for x in items)` compiles to JavaScript generator functions
- **Generators and yield**: Full `yield` and `yield from` support using JavaScript `function*`
- **Generator protocol methods**:
  - `generator.send(value)`: Send values into generators
  - `generator.throw(type)`: Throw exceptions into generators
  - `generator.close()`: Close generators with GeneratorExit
- **GeneratorExit exception**: Properly implemented as BaseException subclass

#### Optimizations
- **Type-informed code generation**: Native operators when types are known
  - Arithmetic: `a + b` → `(a + b)` when both are `int` or `str`
  - String repeat: `s * n` → `s.repeat(n)` when types known
  - Equality: `x == y` → `(x === y)` for primitive types
  - F-strings: `f"Hello, {name}!"` → `('Hello, ' + name + '!')` with type annotations
  - `print()`: Direct `console.log()` for primitives, skips `_pyfunc_str` wrapper
  - `str()`: Native `String()` for numbers, `_pyfunc_str` for bools (Python capitalization), passthrough for strings
  - Type inference from: literals, annotations, builtins (`len`, `str`), methods (`.upper()`, `.find()`), user-defined function return types

### Fixed

- **Negative array/tuple indexing**: `arr[-1]` now correctly returns last element
- **Function *args**: Rest parameters (`...args`) work correctly in nested functions
- **Function *args calls**: `func(*args)` now generates valid `.apply(null, args)`
- **Parameter reassignment**: Reassigning function parameters no longer creates shadowed variables
- **Default arguments with None**: `def foo(x=None)` generates correct `x = null` default
- **sorted() with numbers**: Uses proper comparison function instead of JavaScript string sort
- **sorted() with generators**: Now properly handles iterators/generators
- **Division by zero in constants**: Left for runtime instead of crashing compiler
- **Function hoisting**: Module-level functions use expressions instead of declarations to prevent JavaScript hoisting issues when same function is defined multiple times
- **Implicit return null**: Functions without explicit return now return `null` (Python's `None`)
- **Tuple/list repr()**: Lists display as `[1, 2]`, tuples as `(1, 2)` - exception `.args` now correctly shown as tuple
- **str(None)**: Returns `"None"` instead of empty string
- **str(True)/str(False)**: Returns `"True"` and `"False"` (Python-style capitalization)
- **repr() with __repr__**: Objects with `__repr__` method now use it correctly
- **repr() string quoting**: Uses double quotes for strings containing single quotes (`"it's"`)
- **Exception args**: `raise ValueError()` now correctly sets `e.args = []` (empty tuple)
- **Exception multiple args**: `raise ValueError("msg", 42)` now works correctly
- **repr(undefined)**: No longer crashes on undefined values
- **`int.from_bytes`**: Class method now correctly recognized (passes original name to handler)

#### Developer Tools
- **`scripts/coverage_report.py`**: Coverage report with context showing uncovered lines in their class/function scope

### Documentation

- Fix doc build issues
- Removed unreliable claims

### Statistics

- 2375 tests passing
- 89.33% test coverage (cf. `make test-cov`)


## [0.9.0] - 2026-01-16

Major release with ES6 module support, optimizations, and developer tooling.

### Added

#### Developer Experience
- **Source map generation** (`-s`/`--source-maps`): Debug Python in browser DevTools
- **Error messages with source locations**: Shows file, line, column with source context
- **Multi-file CLI**: Compile entire directories with `py2js src/ -o dist/`
- **Module path support**: Add search paths with `-M`/`--module-path`

#### ES6 Module System
- **Export generation** (`-m` flag): Auto-export module-level definitions
- **Import translation**: Python imports → ES6 imports
  - `import foo` → `import * as foo from './foo.js'`
  - `from foo import bar` → `import { bar } from './foo.js'`
  - Relative imports (`.`, `..`) fully supported
- **Package support**: `__init__.py` → `index.js`
- **JS FFI**: `import js` for direct JavaScript API access

#### Optimizations
- **Tree-shaking**: Include only used stdlib functions (94-99% size reduction)
- **Constant folding**: Compile-time evaluation of expressions
  - Arithmetic: `1 + 2 * 3` → `7`
  - Strings: `"a" + "b"` → `"ab"`
  - Built-ins: `len("hello")` → `5`
- **Function inlining**: `abs(-5)` → `5`, `min(1,2,3)` → `1`
- **Type-informed code generation**: Native operators when types are known
  - Arithmetic: `a + b` → `(a + b)` when both are `int` or `str`
  - String repeat: `s * n` → `s.repeat(n)` when types known
  - Equality: `x == y` → `(x === y)` for primitive types
  - F-strings: `f"Hello, {name}!"` → `('Hello, ' + name + '!')` with type annotations
  - `print()`: Direct `console.log()` for primitives, skips `_pyfunc_str` wrapper
  - `str()`: Native `String()` for numbers, `_pyfunc_str` for bools (Python capitalization), passthrough for strings
  - Type inference from: literals, annotations, builtins (`len`, `str`), methods (`.upper()`, `.find()`), user-defined function return types

#### Class System Enhancements
- `super()` calls with `_pyfunc_super_proxy` runtime
- Decorators: `@staticmethod`, `@classmethod`, `@property`
- Special methods: `__str__`, `__len__`, `__eq__`, `__getitem__`, `__setitem__`

#### Compiler Infrastructure
- Smart `const`/`let` declarations based on scope analysis
- Type inference pass for better code generation
- Pattern matching throughout codebase for cleaner code

### Changed

- Rewrote CLI with argparse (better help, error messages)
- Improved all statement handlers (for, try/except, with, if/elif)
- Improved all expression handlers (f-strings, operators, comprehensions)
- Refactored constant folder with declarative tables (30% less code)

### Fixed

- For loop `else` clause break detection
- If/elif string slicing bug
- Augmented assignment (`+=`) now correctly marks variables as `let`
- Class constructor auto-instantiation without `new`
- Method-local variable scoping

### Documentation

- Complete MkDocs documentation site
- User Guide: CLI, language support, modules, JS interop, source maps, optimization
- Examples: browser app, Node.js CLI, multi-file project
- Reference: feature matrix, limitations, semantic differences
- Developer guide for contributors

### Statistics

- 2347 tests passing (up from 629)
- 330+ lines of dead code removed
- 83% code coverage

---

## [0.8.0] - 2023-08

Initial internal release of Prescrypt, forked from PScript with redesigned architecture.

### Added

- Python to JavaScript transpilation
- Core Python constructs:
  - Functions with default arguments, `*args`, `**kwargs`
  - Classes with single inheritance
  - Control flow: if/elif/else, for, while, try/except
  - Comprehensions: list, dict, set
  - Async/await
- Built-in functions: `len()`, `range()`, `enumerate()`, `zip()`, `map()`, `filter()`, `sorted()`, `reversed()`, etc.
- String formatting: f-strings, %-formatting, `.format()`
- CLI tool: `py2js`
- Basic Binder pass for scope analysis
