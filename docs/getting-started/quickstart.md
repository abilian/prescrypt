# Quick Start

Get Prescrypt running in 5 minutes. By the end of this guide, you'll compile Python to JavaScript and run it in Node.js.

## Your First Compilation

### 1. Create a Python File

Create `hello.py`:

```python
def greet(name):
    return "Hello, " + name + "!"

message = greet("World")
print(message)
```

### 2. Compile to JavaScript

```bash
py2js hello.py
```

This creates `hello.js` in the same directory.

### 3. Run with Node.js

```bash
node hello.js
```

Output:

```
Hello, World!
```

Congratulations! You've just compiled and run your first Prescrypt program.

## Understanding the Output

Let's look at what Prescrypt generated (helper definitions omitted):

```javascript
// hello.js
var _pyfunc_op_add = function (a, b) { /* handles + for any type */ };
var _pyfunc_print = function (/* ... */) { /* Python-compatible print */ };

function greet(name) {
    return _pyfunc_op_add(_pyfunc_op_add("Hello, ", name), "!");
}

let message = greet("World");
_pyfunc_print(message);
```

Notice:

- **Functions** become JavaScript functions
- **Operators** use stdlib helpers for Python semantics (`+` works on strings, lists, numbers)
- **print()** uses a stdlib helper for Python-compatible behavior
- Variables use `let` or `const` appropriately

!!! note "About the stdlib"
    Prescrypt includes runtime helpers (`_pyfunc_*`, `_pymeth_*`) for Python features that don't map directly to JavaScript. The `+` operator uses `_pyfunc_op_add` because Python's `+` is polymorphic. Tree-shaking removes unused helpers.

## Module Mode

For ES6 modules with exports, use `-m`:

```bash
py2js hello.py -m
```

Now the output has exports:

```javascript
// hello.js (stdlib definitions omitted)
export function greet(name) {
    return _pyfunc_op_add(_pyfunc_op_add("Hello, ", name), "!");
}

export let message = greet("World");
_pyfunc_print(message);
```

## Compile a Project

For multi-file projects, compile an entire directory:

```bash
# Create a simple project
mkdir myproject
echo 'VERSION = "1.0"' > myproject/config.py
echo 'from config import VERSION
print(f"Version: {VERSION}")' > myproject/main.py

# Compile to dist/
py2js myproject/ -o dist/
```

Output:

```
Note: Enabling module mode for directory compilation
myproject/config.py -> dist/config.js
myproject/main.py -> dist/main.js

Compiled 2 file(s), 0 error(s)
```

Run it:

```bash
cd dist
echo '{"type": "module"}' > package.json
node main.js
```

Output:

```
Version: 1.0
```

## Enable Source Maps

For debugging, generate source maps with `-s`:

```bash
py2js hello.py -s
```

This creates both `hello.js` and `hello.js.map`. Open the JavaScript in browser DevTools and you can set breakpoints in your original Python code!

## Common Options

| Option | Description |
|--------|-------------|
| `-o <path>` | Output file or directory |
| `-m` | Enable ES6 module mode |
| `-s` | Generate source maps |
| `-v` | Verbose output |
| `--no-stdlib` | Don't include runtime helpers |

See the [CLI Reference](../guide/cli.md) for all options.

## What's Next?

<div class="grid cards" markdown>

-   :material-language-python: **Language Support**

    ---

    Learn what Python features work in Prescrypt.

    [:octicons-arrow-right-24: Language Support](../guide/language-support.md)

-   :material-web: **JavaScript Interop**

    ---

    Access browser and Node.js APIs from Python.

    [:octicons-arrow-right-24: JS Interop](../guide/js-interop.md)

-   :material-folder-multiple: **Multi-file Projects**

    ---

    Build real applications with multiple modules.

    [:octicons-arrow-right-24: Module System](../guide/modules.md)

-   :material-code-tags: **Examples**

    ---

    See complete working examples.

    [:octicons-arrow-right-24: Examples](../examples/index.md)

</div>
