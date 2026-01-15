# Limitations

Prescrypt supports a substantial subset of Python, but some features cannot be transpiled to JavaScript. This page explains what's not supported and suggests alternatives.

## Fundamental Limitations

These limitations arise from fundamental differences between Python and JavaScript.

### No Multiple Inheritance

JavaScript's prototype chain supports single inheritance only.

```python
# Not supported
class C(A, B):
    pass
```

**Alternative:** Use composition or mixins:

```python
class C(A):
    def __init__(self):
        super().__init__()
        self._b = B()

    def b_method(self):
        return self._b.method()
```

### No Metaclasses

JavaScript has no equivalent to Python's metaclass system.

```python
# Not supported
class MyMeta(type):
    pass

class MyClass(metaclass=MyMeta):
    pass
```

**Alternative:** Use class decorators or factory functions.

### No `eval()` or `exec()`

Dynamic code execution isn't supported.

```python
# Not supported
result = eval("2 + 2")
exec("x = 42")
```

**Alternative:** Restructure to avoid dynamic code. If absolutely needed, use `js.eval()` (with all the security concerns that implies).

### Limited Lambda Support

Basic lambdas work, but lambdas with default arguments do not compile.

```python
# Works
double = lambda x: x * 2
items.filter(lambda x: x > 0)

# Does NOT work - default arguments
f = lambda x=1: x
callback = lambda e, data=value: handle(e, data)
```

**Alternative:** Use factory functions:

```python
def make_handler(data):
    def handler(e):
        handle(e, data)
    return handler

callback = make_handler(value)
```

### No Generator Functions

Python generators don't translate to JavaScript generators automatically.

```python
# Not supported
def count():
    i = 0
    while True:
        yield i
        i += 1
```

**Alternative:** Return a list or use callbacks:

```python
def count(n):
    return list(range(n))

# Or use iteration
def process_items(items, callback):
    for item in items:
        callback(item)
```

### Limited Context Managers

The `with` statement syntax compiles, but `__enter__`/`__exit__` methods on custom classes don't work correctly. The context manager protocol is not properly implemented.

```python
# Syntax compiles but behavior is incorrect
with MyContextManager() as ctx:
    do_something()
```

**Alternative:** Use try/finally:

```python
import js
fs = js.require("fs")

try:
    content = fs.readFileSync("file.txt", "utf8")
    # process content
finally:
    # cleanup if needed
    pass
```

## Type System Limitations

### No Type Annotations at Runtime

Type hints are stripped; no runtime type checking.

```python
def add(a: int, b: int) -> int:  # Hints ignored
    return a + b
```

**Note:** This is fine—type hints are primarily for documentation and static analysis.

### Integer/Float Distinction Lost

JavaScript has only `number`.

```python
x = 5      # In JS: 5.0
y = 5.0    # In JS: 5.0
x == y     # True in both Python and JS
```

**Watch out for:**
```python
# Python: 5 // 2 = 2
# JS: Math.floor(5 / 2) = 2 (same)

# Python: 5 / 2 = 2.5
# JS: 5 / 2 = 2.5 (same)

# But: Python int can be arbitrarily large
# JS number has precision limits
```

### No `bytes` or `bytearray`

Binary data types aren't supported natively.

```python
# Not supported
data = b"hello"
```

**Alternative:** Use JavaScript typed arrays:

```python
import js

# Create byte array
data = js.Uint8Array([104, 101, 108, 108, 111])

# Or from string
encoder = js.TextEncoder()
data = encoder.encode("hello")
```

## Standard Library Limitations

### Most stdlib Modules Unavailable

Python's standard library doesn't exist in JavaScript.

```python
# Not supported
import os
import sys
import json
import re
```

**Alternative:** Use JavaScript equivalents:

```python
import js

# File system (Node.js)
fs = js.require("fs")
path = js.require("path")

# JSON
data = js.JSON.parse(text)
text = js.JSON.stringify(data)

# Regular expressions
regex = js.RegExp(r"\d+", "g")
matches = text.match(regex)

# Environment
env_var = js.process.env.MY_VAR
```

### No `re` Module

Python regex isn't available.

```python
# Not supported
import re
match = re.search(r"\d+", text)
```

**Alternative:** Use JavaScript regex:

```python
import js

# Create regex
pattern = js.RegExp(r"\d+")

# Test
if pattern.test(text):
    print("Found!")

# Match
match = text.match(pattern)

# Replace
result = text.replace(pattern, "X")
```

### No `datetime`

Date/time operations need JavaScript's Date.

```python
# Not supported
from datetime import datetime
now = datetime.now()
```

**Alternative:**

```python
import js

# Current time
now = js.Date()
timestamp = now.getTime()

# Create specific date
date = js.Date(2024, 0, 15)  # Jan 15, 2024 (month is 0-indexed!)

# Format
iso = date.toISOString()
local = date.toLocaleDateString()
```

### No `json` Module

JSON operations use JavaScript's JSON object.

```python
# Not supported
import json
data = json.loads(text)
```

**Alternative:**

```python
import js

# Parse JSON
data = js.JSON.parse(text)

# Stringify
text = js.JSON.stringify(data)
text = js.JSON.stringify(data, None, 2)  # Pretty print
```

## Class Limitations

### No `@dataclass`

Dataclasses aren't supported.

```python
# Not supported
@dataclass
class Point:
    x: int
    y: int
```

**Alternative:** Write explicit `__init__`:

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

### Limited Special Methods

Only some dunder methods work.

| Works | Doesn't Work |
|-------|-------------|
| `__init__` | `__new__` |
| `__str__` | `__repr__` (same as str) |
| `__eq__` | `__hash__` |
| `__len__` | `__bool__` |
| `__getitem__` | `__missing__` |
| `__setitem__` | `__contains__` |
| `__delitem__` | `__iter__` |

### No Abstract Base Classes

ABCs and `@abstractmethod` aren't supported.

```python
# Not supported
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass
```

**Alternative:** Document the interface and check at runtime:

```python
class Shape:
    def area(self):
        raise NotImplementedError("Subclass must implement area()")
```

## Async Limitations

### No `async for`

Async iteration isn't supported.

```python
# Not supported
async for item in async_generator():
    process(item)
```

**Alternative:** Collect all items first:

```python
items = await get_all_items()
for item in items:
    process(item)
```

### No `async with`

Async context managers aren't supported.

```python
# Not supported
async with session.get(url) as response:
    data = await response.json()
```

**Alternative:**

```python
response = await session.get(url)
try:
    data = await response.json()
finally:
    # cleanup if needed
    pass
```

## Other Limitations

### No `match`/`case`

Python 3.10+ pattern matching isn't supported.

```python
# Not supported
match command:
    case "start":
        start()
    case "stop":
        stop()
```

**Alternative:** Use if/elif:

```python
if command == "start":
    start()
elif command == "stop":
    stop()
```

### No Walrus Operator

Assignment expressions aren't supported.

```python
# Not supported
if (n := len(items)) > 10:
    print(f"Too many: {n}")
```

**Alternative:**

```python
n = len(items)
if n > 10:
    print(f"Too many: {n}")
```

### No Positional-Only Parameters

Python 3.8+ `/` syntax isn't supported.

```python
# Not supported
def func(x, /, y):
    pass
```

**Alternative:** Just use regular parameters.

## See Also

- [Feature Matrix](features.md) - Complete feature support table
- [Semantic Differences](differences.md) - Behavioral differences
- [JavaScript Interop](../guide/js-interop.md) - Using JS as alternative
