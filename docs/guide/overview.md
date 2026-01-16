# User Guide Overview

This guide explains how Prescrypt works and how to use it effectively for Python-to-JavaScript transpilation.

## How Prescrypt Works

Prescrypt is a source-to-source compiler (transpiler) that converts Python code to JavaScript. The compilation happens at build time, not runtime.

```
Python Source → Parse → Analyze → Generate → JavaScript Output
```

### Compilation Pipeline

1. **Parsing**: Python's `ast` module parses your source code into an Abstract Syntax Tree
2. **Desugaring**: Complex syntax is simplified (e.g., `a += b` becomes `a = a + b`)
3. **Binding**: Scope analysis determines variable declarations and closures
4. **Code Generation**: The AST is walked to produce JavaScript code

### What Gets Generated

Prescrypt generates ES6+ JavaScript:

=== "Python Input"

    ```python
    def factorial(n):
        if n <= 1:
            return 1
        return n * factorial(n - 1)

    result = factorial(5)
    print("5! = " + str(result))
    ```

=== "JavaScript Output"

    ```javascript
    // Stdlib helper definitions omitted
    function factorial(n) {
        if (n <= 1) {
            return 1;
        }
        return (n * factorial((n - 1)));
    }

    let result = factorial(5);
    _pyfunc_print(_pyfunc_op_add("5! = ", result));
    ```

## Core Concepts

### Runtime vs Compile-Time

Prescrypt operates primarily at **compile time**:

- **Compile-time**: Syntax transformation, constant folding, dead code elimination
- **Runtime**: A small stdlib provides Python-compatible behavior for `len()`, `range()`, etc.

The stdlib is tree-shaken to include only functions you actually use.

### Module Modes

Prescrypt has two output modes:

| Mode | Use Case | Exports | Stdlib |
|------|----------|---------|--------|
| **Script mode** (default) | Standalone scripts | None | Inlined |
| **Module mode** (`-m`) | Multi-file projects | ES6 exports | Shared |

### Type Coercion

Prescrypt aims for Python semantics but uses JavaScript types:

```python
# Python types map to JavaScript
x = 42          # → number
y = 3.14        # → number
s = "hello"     # → string
b = True        # → boolean (true)
lst = [1, 2]    # → Array
dct = {"a": 1}  # → Object
```

!!! note "Integers vs Floats"
    JavaScript doesn't distinguish integers from floats. Both become `number`.

## Project Structure

A typical Prescrypt project looks like:

```
myproject/
├── src/
│   ├── main.py
│   ├── utils.py
│   └── models/
│       └── user.py
├── dist/           # Generated JavaScript
│   ├── main.js
│   ├── utils.js
│   └── models/
│       └── user.js
└── package.json    # {"type": "module"}
```

Compile with:

```bash
py2js src/ -o dist/
```

## Best Practices

!!! tip "Use Module Mode for Projects"
    For anything beyond single-file scripts, use module mode (`-m`). This enables proper imports/exports and avoids global namespace pollution.

!!! tip "Keep Python Patterns"
    Write idiomatic Python. Prescrypt handles the translation. Don't try to write "JavaScript-in-Python".

!!! warning "Know the Limitations"
    Not all Python features are supported. See [Limitations](../reference/limitations.md) for details. Key unsupported features:

    - Multiple inheritance
    - Metaclasses
    - `eval()` / `exec()`
    - Most of the standard library

## Next Steps

- [CLI Reference](cli.md) - All command-line options
- [Language Support](language-support.md) - Supported Python features
- [JavaScript Interop](js-interop.md) - Calling browser/Node.js APIs
