# Changelog

All notable changes to Prescrypt will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.1] - unreleased

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

- 2403 tests passing


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
