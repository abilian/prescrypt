# Multi-file Project Example

Build a structured project with multiple modules, packages, and shared utilities.

## Project Structure

```
calculator/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── operations/
│   │   ├── __init__.py
│   │   ├── basic.py
│   │   └── advanced.py
│   └── utils/
│       ├── __init__.py
│       ├── parser.py
│       └── formatter.py
├── dist/               # Generated
│   ├── index.js
│   ├── main.js
│   ├── operations/
│   │   ├── index.js
│   │   ├── basic.js
│   │   └── advanced.js
│   └── utils/
│       ├── index.js
│       ├── parser.js
│       └── formatter.js
└── package.json
```

## The Code

### src/\_\_init\_\_.py

```python
"""Calculator Package"""
VERSION = "1.0.0"
```

### src/main.py

```python
"""Calculator CLI - Main entry point."""
import js
from operations import add, subtract, multiply, divide
from operations.advanced import power, sqrt, factorial
from utils.parser import parse_expression
from utils.formatter import format_result

def calculate(expression):
    """Parse and evaluate an expression."""
    parsed = parse_expression(expression)
    if parsed is None:
        return None

    op = parsed["operator"]
    a = parsed["left"]
    b = parsed.get("right")

    operations = {
        "+": lambda: add(a, b),
        "-": lambda: subtract(a, b),
        "*": lambda: multiply(a, b),
        "/": lambda: divide(a, b),
        "^": lambda: power(a, b),
        "sqrt": lambda: sqrt(a),
        "!": lambda: factorial(int(a))
    }

    if op not in operations:
        js.console.error(f"Unknown operator: {op}")
        return None

    result = operations[op]()
    return format_result(result)


def repl():
    """Interactive calculator REPL."""
    js.console.log("Calculator v1.0.0")
    js.console.log("Enter expressions like: 2 + 3, 10 / 2, sqrt 16, 5!")
    js.console.log("Type 'exit' to quit.\n")

    readline = js.require("readline")
    rl = readline.createInterface({
        "input": js.process.stdin,
        "output": js.process.stdout
    })

    def handle_line(line):
        line = line.strip()
        if line.lower() == "exit":
            rl.close()
            return

        if line:
            result = calculate(line)
            if result is not None:
                js.console.log(f"= {result}")
            else:
                js.console.log("Invalid expression")

        rl.prompt()

    rl.on("line", handle_line)
    rl.on("close", lambda: js.console.log("\nGoodbye!"))
    rl.setPrompt("> ")
    rl.prompt()


def main():
    """Main entry point."""
    args = list(js.process.argv)[2:]

    if not args:
        # No arguments - start REPL
        repl()
    else:
        # Evaluate expression from command line
        expression = " ".join(args)
        result = calculate(expression)
        if result is not None:
            js.console.log(result)
        else:
            js.process.exit(1)


main()
```

### src/operations/\_\_init\_\_.py

```python
"""Basic operations - re-exported for convenience."""
from .basic import add, subtract, multiply, divide

__all__ = ["add", "subtract", "multiply", "divide"]
```

### src/operations/basic.py

```python
"""Basic arithmetic operations."""

def add(a, b):
    """Add two numbers."""
    return a + b


def subtract(a, b):
    """Subtract b from a."""
    return a - b


def multiply(a, b):
    """Multiply two numbers."""
    return a * b


def divide(a, b):
    """Divide a by b."""
    if b == 0:
        raise ValueError("Division by zero")
    return a / b
```

### src/operations/advanced.py

```python
"""Advanced mathematical operations."""
import js

def power(base, exponent):
    """Raise base to the power of exponent."""
    return js.Math.pow(base, exponent)


def sqrt(n):
    """Calculate square root."""
    if n < 0:
        raise ValueError("Cannot take square root of negative number")
    return js.Math.sqrt(n)


def factorial(n):
    """Calculate factorial of n."""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

### src/utils/\_\_init\_\_.py

```python
"""Utility modules."""
from .parser import parse_expression
from .formatter import format_result

__all__ = ["parse_expression", "format_result"]
```

### src/utils/parser.py

```python
"""Expression parser."""
import js

def parse_expression(expr):
    """Parse a mathematical expression.

    Supports: a + b, a - b, a * b, a / b, a ^ b, sqrt a, a!
    """
    expr = expr.strip()

    # Unary: factorial (5!)
    if expr.endswith("!"):
        try:
            num = float(expr[:-1].strip())
            return {"operator": "!", "left": num}
        except:
            return None

    # Unary: sqrt
    if expr.startswith("sqrt"):
        try:
            num = float(expr[4:].strip())
            return {"operator": "sqrt", "left": num}
        except:
            return None

    # Binary operators
    operators = ["+", "-", "*", "/", "^"]
    for op in operators:
        if op in expr:
            parts = expr.split(op, 1)
            if len(parts) == 2:
                try:
                    left = float(parts[0].strip())
                    right = float(parts[1].strip())
                    return {"operator": op, "left": left, "right": right}
                except:
                    continue

    return None
```

### src/utils/formatter.py

```python
"""Result formatting utilities."""

def format_result(value):
    """Format a numeric result for display."""
    if value is None:
        return None

    # Check if it's an integer
    if isinstance(value, float) and value == int(value):
        return str(int(value))

    # Format floats with reasonable precision
    if isinstance(value, float):
        # Remove trailing zeros
        formatted = f"{value:.10f}".rstrip("0").rstrip(".")
        return formatted

    return str(value)
```

### package.json

```json
{
  "name": "calculator",
  "version": "1.0.0",
  "type": "module",
  "main": "dist/main.js",
  "bin": {
    "calc": "./dist/main.js"
  }
}
```

## Compile and Run

```bash
# Create project structure
mkdir -p calculator/src/operations calculator/src/utils
cd calculator

# Copy all .py files to appropriate locations
# Create package.json

# Compile entire project
py2js src/ -o dist/

# Run examples
node dist/main.js 2 + 3
node dist/main.js "10 / 4"
node dist/main.js "sqrt 16"
node dist/main.js "5!"
node dist/main.js 2 ^ 10

# Start REPL
node dist/main.js
```

## Key Patterns

### Package Re-exports

Use `__init__.py` to create a clean public API:

```python
# operations/__init__.py
from .basic import add, subtract, multiply, divide

# Now users can do:
from operations import add
# Instead of:
from operations.basic import add
```

### Relative Imports

```python
# Inside operations/advanced.py
from .basic import add  # Same package
from ..utils import format_result  # Parent package
```

### Lazy Loading

For large modules, import inside functions:

```python
def process_data(data):
    # Only loaded when needed
    from .heavy_module import expensive_function
    return expensive_function(data)
```

### Configuration Module

```python
# config.py
import js

DEBUG = js.process.env.DEBUG == "1"
API_URL = js.process.env.API_URL or "https://api.example.com"
TIMEOUT = 30
```

```python
# main.py
from config import DEBUG, API_URL

if DEBUG:
    js.console.log(f"Using API: {API_URL}")
```

### Type Checking at Runtime

```python
def process(value):
    if not isinstance(value, (int, float)):
        raise TypeError(f"Expected number, got {type(value)}")
    return value * 2
```

## Directory Compilation Details

When compiling a directory:

| Python | JavaScript |
|--------|------------|
| `__init__.py` | `index.js` |
| `module.py` | `module.js` |
| `from x import y` | `import { y } from './x.js'` |
| `import x` | `import * as x from './x.js'` |

The `-o` flag specifies the output directory:

```bash
py2js src/ -o dist/
# src/main.py → dist/main.js
# src/utils/parser.py → dist/utils/parser.js
```

## Bundling for Single-File Output

For environments that require a single JavaScript file (browser extensions, embedded scripts, serverless functions), use the `--bundle` flag:

```bash
# Bundle everything into one file
py2js src/main.py -o dist/bundle.js --bundle -M src/
```

This produces a single `bundle.js` containing:

- All stdlib functions used by ANY module (combined tree-shaking)
- All imported modules in dependency order
- No ES6 import statements (self-contained)

### When to Bundle vs Directory Compile

| Scenario | Command | Output |
|----------|---------|--------|
| Node.js app | `py2js src/ -o dist/` | Multiple ES6 modules |
| Browser (modern) | `py2js src/ -o dist/` | Multiple ES6 modules |
| Browser extension | `py2js src/main.py -o bundle.js --bundle -M src/` | Single file |
| Embedded script | `py2js src/main.py -o bundle.js --bundle -M src/` | Single file |
| npm library | `py2js src/ -o dist/ -m` | Multiple ES6 modules with exports |

### Bundle Output Structure

The bundled output looks like:

```javascript
// Tree-shaken stdlib (only functions used by any module)
var _pyfunc_str = function(x) { ... };
var _pyfunc_create_dict = function() { ... };
// ... other used functions

// === Module: utils/formatter.py ===
var format_result = function(value) { ... };

// === Module: utils/parser.py ===
var parse_expression = function(expr) { ... };

// === Module: operations/basic.py ===
var add = function(a, b) { ... };
// ...

// === Module: main.py ===
/* bundled: from operations import add, subtract, ... */
var calculate = function(expression) { ... };
// ...
```

## Testing Multi-file Projects

Create a test file:

```python
# test_operations.py
from operations.basic import add, subtract, multiply, divide
from operations.advanced import power, sqrt, factorial

def test_basic():
    assert add(2, 3) == 5
    assert subtract(5, 3) == 2
    assert multiply(4, 3) == 12
    assert divide(10, 2) == 5

def test_advanced():
    assert power(2, 3) == 8
    assert sqrt(16) == 4
    assert factorial(5) == 120

test_basic()
test_advanced()
print("All tests passed!")
```

```bash
py2js test_operations.py -o test_operations.js -M src/
node test_operations.js
```

## See Also

- [Module System](../guide/modules.md) - Import/export details
- [CLI Reference](../guide/cli.md) - Compilation options
- [Browser App](browser-app.md) - Client-side example
