# Changelog

All notable changes to Prescrypt will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0] - 2026-01-15

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

- 2216 tests passing (up from 629)
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
