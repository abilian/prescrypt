# Optimization

Prescrypt applies several optimizations to generate efficient JavaScript. This page explains what optimizations are available and how to control them.

## Overview

Prescrypt optimizes at compile time:

| Optimization | Default | Flag to Disable |
|-------------|---------|-----------------|
| Constant folding | On | `--no-optimize` |
| Dead code elimination | On | `--no-optimize` |
| Type-informed codegen | On | `--no-optimize` |
| Tree-shaking (stdlib) | On | `--no-tree-shake` |

## Constant Folding

Prescrypt evaluates constant expressions at compile time:

```python
# Python
WIDTH = 800
HEIGHT = 600
AREA = WIDTH * HEIGHT

TAX_RATE = 0.08
PRICE = 100
TOTAL = PRICE * (1 + TAX_RATE)
```

**Compiles to:**

```javascript
const WIDTH = 800;
const HEIGHT = 600;
const AREA = 480000;  // Computed at compile time

const TAX_RATE = 0.08;
const PRICE = 100;
const TOTAL = 108;    // Computed at compile time
```

### What Gets Folded

- Arithmetic: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- String operations: concatenation, repetition
- Boolean operations: `and`, `or`, `not`
- Comparisons: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Built-in functions on constants: `len()`, `abs()`, `min()`, `max()`
- List/dict/set literals with constant elements

### Examples

```python
# All computed at compile time
DEBUG = False
LOG_LEVEL = "INFO" if DEBUG else "WARNING"

ITEMS = [1, 2, 3]
ITEM_COUNT = len(ITEMS)  # → 3

MESSAGE = "Hello " * 3   # → "Hello Hello Hello "
```

## Dead Code Elimination

Code that can never execute is removed:

```python
DEBUG = False

def log(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")  # Removed when DEBUG is False
    process(msg)
```

**Compiles to:**

```javascript
function log(msg) {
    // DEBUG check eliminated
    process(msg);
}
```

### What Gets Eliminated

- `if False:` blocks
- `if True: ... else:` → just the `if` body
- Unreachable code after `return`, `raise`, `break`, `continue`

## Type-Informed Code Generation

When Prescrypt knows the types of values (from literals, type annotations, or inference), it generates more efficient code using native JavaScript operators instead of runtime helpers.

### How It Works

Prescrypt infers types from:

- **Literals**: `x = 42` → `x` is `Int`
- **Type annotations**: `def greet(name: str)` → `name` is `String`
- **Function return types**: `def get_name() -> str` → calls return `String`
- **Built-in functions**: `len(items)` returns `Int`
- **Method calls**: `s.upper()` on a `String` returns `String`
- **Arithmetic**: `Int + Int` → `Int`, `Int / Int` → `Float`

### Optimized Operations

#### Arithmetic (`+`, `*`)

```python
# Without type info - uses helper for Python semantics
def add(a, b):
    return a + b
# → return _pyfunc_op_add(a, b);

# With type info - uses native operator
def add(a: int, b: int) -> int:
    return a + b
# → return (a + b);

# Or inferred from literals
x = 10
y = 20
z = x + y
# → const z = (x + y);
```

#### String Operations

```python
# String + String uses native +
name = "World"
greeting = "Hello, " + name
# → const greeting = ('Hello, ' + name);

# String * Int uses .repeat()
s = "ab"
n = 3
result = s * n
# → const result = s.repeat(n);
```

#### Equality (`==`, `!=`)

```python
# Primitive types use === for direct comparison
x = 10
y = 20
if x == y:  # → if ((x === y))
    pass

# Lists/dicts still use helper for deep comparison
a = [1, 2]
b = [1, 2]
if a == b:  # → if (_pyfunc_op_equals(a, b))
    pass
```

#### F-Strings

```python
# With known types - uses concatenation
def greet(name: str) -> str:
    return f"Hello, {name}!"
# → return ('Hello, ' + name + '!');

# With format specs - uses _pymeth_format
value = 3.14
result = f"Pi: {value:.2f}"
# → _pymeth_format.call("Pi: {:.2f}", value);
```

#### print() and str()

```python
# With known types - direct console.log, no wrapper
def greet(name: str) -> str:
    return f"Hello, {name}!"

print(greet("World"))
# → console.log(greet('World'));

# str() of primitives uses native String()
def get_count() -> int:
    return 42

x = str(get_count())
# → const x = String(get_count());

# Unknown types still use runtime helpers for Python semantics
def get_data():
    return [1, 2, 3]

print(get_data())
# → console.log(_pyfunc_str(get_data()));
```

### Best Practices

!!! tip "Add Type Annotations for Cleaner Output"
    ```python
    # Cleaner JavaScript output
    def calculate(x: int, y: int) -> int:
        return x + y * 2
    ```

!!! tip "Types Propagate Through Variables"
    ```python
    # x is inferred as Int from literal
    x = 10
    # y is inferred as Int from x
    y = x + 5  # Uses native +
    ```

!!! note "Fallback is Safe"
    When types are unknown, Prescrypt safely falls back to runtime helpers that handle all Python semantics correctly.

## Tree-Shaking

Prescrypt includes only the stdlib functions your code actually uses.

### Without Tree-Shaking

```bash
py2js app.py --no-tree-shake
```

Includes the entire stdlib (~50KB), regardless of what you use.

### With Tree-Shaking (Default)

```bash
py2js app.py
```

Analyzes your code and includes only required functions:

```python
# app.py
items = [1, 2, 3]
total = sum(items)
print(f"Total: {total}")
```

**Includes only:**
- `_pyfunc_sum`
- `_pyfunc_print`

### How It Works

1. **Scan**: Find all stdlib function calls in your code
2. **Resolve**: Include each required function and its dependencies
3. **Emit**: Output only the needed stdlib code

### Dependency Chains

Some stdlib functions depend on others:

```
range() → needs iterator protocol functions
enumerate() → needs range() internals
zip() → needs multiple iteration helpers
```

Tree-shaking automatically includes all dependencies.

## No-Stdlib Mode

For embedding or when providing your own runtime:

```bash
py2js app.py --no-stdlib
```

Generates pure JavaScript without any stdlib preamble. Your code must not use:
- `print()` (use `js.console.log()`)
- `range()`, `enumerate()`, `zip()`
- `len()` on custom objects
- Python-style equality (`==` on objects)

### When to Use

- Embedding in existing JS applications that provide runtime
- Maximum control over output size
- When targeting environments with custom polyfills

## Disabling Optimizations

For debugging or when optimizations cause issues:

```bash
py2js app.py --no-optimize
```

This disables:
- Constant folding
- Dead code elimination

The output will be more verbose but easier to debug.

## Bundle Size

### Measuring Output Size

```bash
# Check generated JS size
py2js app.py -o app.js
wc -c app.js

# With full stdlib for comparison
py2js app.py --no-tree-shake -o app-full.js
wc -c app-full.js
```

### Minimizing Bundle Size

1. **Use tree-shaking** (default): Only include what you use
2. **Avoid expensive stdlib functions**: `isinstance()`, complex iteration
3. **Use JS APIs directly**: `js.console.log()` vs `print()`
4. **Consider `--no-stdlib`**: For minimal output

### Size Comparison

| Configuration | Typical Size |
|--------------|--------------|
| Minimal (no stdlib) | ~1KB |
| Tree-shaken | 5-15KB |
| Full stdlib | ~50KB |

## Best Practices

!!! tip "Use Constants for Configuration"
    ```python
    # These get folded at compile time
    DEBUG = False
    API_URL = "https://api.example.com"
    MAX_RETRIES = 3
    ```

!!! tip "Prefer Simple Patterns"
    ```python
    # Good - tree-shakes well
    for i in range(10):
        process(i)

    # Heavier - pulls in more stdlib
    for i, item in enumerate(items):
        process(i, item)
    ```

!!! warning "Avoid Dynamic Calls"
    ```python
    # Can't be optimized - function name not known
    func_name = "process"
    getattr(module, func_name)(data)

    # Better - direct call
    module.process(data)
    ```

## See Also

- [CLI Reference](cli.md) - Optimization flags
- [Language Support](language-support.md) - Feature support
- [Limitations](../reference/limitations.md) - What can't be optimized
