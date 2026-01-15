# Prescrypt

A Python to JavaScript transpiler for a well-defined subset of Python.

Status: Alpha. Use at your own risks.

## Overview

Prescrypt converts Python 3.9+ code to ES6+ JavaScript. It prioritizes correctness over completeness, targeting common use cases rather than full Python compatibility.

## Features

- **Modern Python support** - Python 3.10+ with pattern matching
- **Modern JavaScript output** - Targets ES6+ with `const`/`let`, arrow functions, classes
- **Comprehensive test suite** - 2000+ tests covering expressions, statements, and full programs
- **Optimized output** - Tree-shaking, constant folding, function inlining
- **Source locations in errors** - Clear error messages with file:line:column

## Installation

```bash
pip install prescrypt
# or
poetry add prescrypt
```

## Quick Start

### As a library

```python
from prescrypt import py2js

code = """
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
"""

js = py2js(code)
print(js)
```

Output:
```javascript
function greet(name) {
    return `Hello, ${name}!`;
}
console.log(greet("World"));
```

### From the command line

```bash
py2js input.py           # Creates input.js
py2js input.py output.js # Explicit output path
```

## Supported Python Features

### Fully Supported

- **Data types**: `int`, `float`, `bool`, `str`, `None`, `list`, `dict`, `tuple`
- **Control flow**: `if`/`elif`/`else`, `for`, `while`, `break`, `continue`
- **Exception handling**: `try`/`except`/`finally`, `raise`
- **Functions**: `def`, `lambda`, `*args`, default arguments, closures
- **Classes**: `class`, `__init__`, inheritance, `super()`, `@property`
- **Decorators**: `@staticmethod`, `@classmethod`, `@property`
- **Comprehensions**: list, dict, generator expressions
- **Operators**: arithmetic, comparison, logical, membership (`in`)
- **Builtins**: `print`, `len`, `range`, `enumerate`, `zip`, `min`, `max`, `sorted`, etc.

### Partially Supported

- `**kwargs` - basic support
- `with` statement - single context manager
- `async`/`await` - basic support

### Not Supported

- `yield` / generators
- Metaclasses
- Multiple inheritance
- `exec()`, `eval()`
- Most of the standard library

## Architecture

```
Python Source → Parse → Desugar → Bind → Optimize → CodeGen → JavaScript
```

- **Parse**: Python's `ast` module with custom extensions
- **Desugar**: Simplifies syntax (e.g., `a += b` → `a = a + b`)
- **Bind**: Scope analysis, determines `const` vs `let`
- **Optimize**: Constant folding, dead code elimination
- **CodeGen**: Produces JavaScript output

## Development

```bash
# Install dependencies
uv sync

# Run tests
make test

# Run linter
make lint

# Format code
make format
```

## License

BSD 2-Clause License. See [LICENSE](LICENSE) for details.

## Acknowledgments

Prescrypt was inspired by [PScript](https://github.com/flexxui/pscript/), originally developed as part of [Flexx](https://flexx.app). While the codebase has been largely rewritten, we acknowledge PScript's pioneering work in Python-to-JavaScript transpilation.
