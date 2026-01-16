# Prescrypt

**Python-to-JavaScript transpiler for modern web development.**

Prescrypt compiles Python 3.9+ code to ES6+ JavaScript. Write Python, run it anywhere JavaScript runs—browsers, Node.js, or serverless functions.

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Get Started in 5 Minutes**

    ---

    Install Prescrypt and compile your first Python program to JavaScript.

    [:octicons-arrow-right-24: Quick Start](getting-started/quickstart.md)

-   :material-language-python:{ .lg .middle } **Write Python, Run JavaScript**

    ---

    Use familiar Python syntax—classes, comprehensions, f-strings—and get ES6 output.

    [:octicons-arrow-right-24: Language Support](guide/language-support.md)

-   :material-web:{ .lg .middle } **Browser & Node.js Ready**

    ---

    ES6 modules with imports/exports. Access browser APIs and Node.js directly.

    [:octicons-arrow-right-24: JS Interop](guide/js-interop.md)

-   :material-bug:{ .lg .middle } **Debug with Source Maps**

    ---

    Set breakpoints in your Python code and debug in browser DevTools.

    [:octicons-arrow-right-24: Source Maps](guide/source-maps.md)

</div>

## Why Prescrypt?

### Familiar Syntax

Write Python code you already know:

```python
class Counter:
    def __init__(self, start=0):
        self.value = start

    def increment(self):
        self.value += 1
        return self.value

items = [x * 2 for x in range(10) if x % 2 == 0]
message = f"Generated {len(items)} items"
```

### JavaScript Output

Generated ES6 (core logic shown, stdlib helpers omitted):

```javascript
export const Counter = function () {
    if (!(this instanceof Counter)) {
        return new Counter(...arguments);
    }
    this.value = arguments[0] ?? 0;
};
Counter.prototype.increment = function () {
    this.value += 1;
    return this.value;
};

// Constant folding: computed at compile time!
export const items = [0, 4, 8, 12, 16];
export const message = "Generated 5 items";
```

### Direct JavaScript Access

Access any JavaScript API with `import js`:

```python
import js

async def fetch_data():
    response = await js.fetch("/api/users")
    return await response.json()

js.document.getElementById("app").innerHTML = "Hello!"
```

## Key Features

| Feature | Description |
|---------|-------------|
| **ES6 Modules** | Automatic exports and ES6 import statements |
| **JS FFI** | Access browser and Node.js APIs via `import js` |
| **Source Maps** | Debug Python code in browser DevTools |
| **Tree-Shaking** | Only include stdlib functions you actually use |
| **Constant Folding** | Compile-time evaluation of constant expressions |
| **Multi-file Projects** | Compile entire directories with module resolution |

## Quick Example

=== "Python"

    ```python
    # app.py
    import js

    def greet(name):
        return "Hello, " + name + "!"

    message = greet("World")
    js.console.log(message)
    ```

=== "Generated JavaScript"

    ```javascript
    // app.js (stdlib helper definitions omitted)
    export function greet(name) {
        return _pyfunc_op_add(_pyfunc_op_add("Hello, ", name), "!");
    }

    export const message = greet("World");
    console.log(message);
    ```

=== "Terminal"

    ```bash
    $ py2js app.py -m
    app.py -> app.js

    $ node app.js
    Hello, World!
    ```

!!! note "Generated output includes stdlib helpers"
    The actual output includes `_pyfunc_*` and `_pymeth_*` helpers for Python-compatible behavior. Tree-shaking ensures only what you use is included.

## Installation

```bash
pip install prescrypt
```

Or with pipx for CLI usage:

```bash
pipx install prescrypt
```

[:octicons-arrow-right-24: Full installation guide](getting-started/installation.md)

## Next Steps

<div class="grid cards" markdown>

-   [:octicons-rocket-24: **Quick Start**](getting-started/quickstart.md)

    Compile your first program

-   [:octicons-book-24: **User Guide**](guide/overview.md)

    Learn all the features

-   [:octicons-code-24: **Examples**](examples/index.md)

    Real-world use cases

-   [:octicons-git-pull-request-24: **Contributing**](contributing.md)

    Help improve Prescrypt

</div>
