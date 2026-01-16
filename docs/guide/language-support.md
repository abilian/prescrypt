# Language Support

Prescrypt supports a substantial subset of Python 3.9+ syntax. This page documents what works and how it translates to JavaScript.

## Data Types

### Primitives

| Python | JavaScript | Notes |
|--------|------------|-------|
| `int` | `number` | No distinction from float |
| `float` | `number` | |
| `str` | `string` | |
| `bool` | `boolean` | `True`→`true`, `False`→`false` |
| `None` | `null` | |

### Collections

| Python | JavaScript | Notes |
|--------|------------|-------|
| `list` | `Array` | Full support |
| `dict` | `Object` | Keys converted to strings |
| `tuple` | `Array` | Treated as list |
| `set` | `Set` | ES6 Set |

```python
# Lists
items = [1, 2, 3]
items.append(4)
first = items[0]

# Dicts
config = {"debug": True, "port": 8080}
debug = config["debug"]
config["host"] = "localhost"

# Sets
unique = {1, 2, 3}
unique.add(4)
```

## Variables

```python
# Variable assignment
x = 42
name = "Alice"

# Multiple assignment
a, b = 1, 2
first, *rest = [1, 2, 3, 4]  # first=1, rest=[2,3,4]

# Augmented assignment
count += 1
text *= 3
```

**Generated JavaScript:**
```javascript
let x = 42;
let name = "Alice";

let [a, b] = [1, 2];
let [first, ...rest] = [1, 2, 3, 4];

count += 1;
text = text.repeat(3);  // string repeat
```

## Strings

### F-Strings

```python
name = "World"
greeting = f"Hello, {name}!"
formatted = f"Value: {x:.2f}"
```

**Compiles to** (using stdlib helpers):
```javascript
// Simplified - actual output uses _pymeth_format helper
let greeting = _pymeth_format.call("Hello, {}!", name);
let formatted = _pyfunc_format(x, ".2f");
```

!!! note "F-string optimization"
    When interpolated values have known primitive types and no format specs, Prescrypt optimizes f-strings to direct concatenation:
    ```python
    def greet(name: str) -> str:
        return f"Hello, {name}!"
    # → return ('Hello, ' + name + '!');
    ```
    F-strings with format specs (like `:.2f`) or unknown types use stdlib helpers for Python-compatible formatting.

### String Methods

| Python | JavaScript |
|--------|------------|
| `s.upper()` | `s.toUpperCase()` |
| `s.lower()` | `s.toLowerCase()` |
| `s.strip()` | `s.trim()` |
| `s.split(sep)` | `s.split(sep)` |
| `s.join(items)` | `items.join(s)` |
| `s.startswith(x)` | `s.startsWith(x)` |
| `s.endswith(x)` | `s.endsWith(x)` |
| `s.replace(a, b)` | `s.replace(a, b)` |

## Functions

### Basic Functions

```python
def greet(name):
    return "Hello, " + name + "!"

def add(a, b=0):
    return a + b
```

**Compiles to** (stdlib definitions omitted):
```javascript
function greet(name) {
    return _pyfunc_op_add(_pyfunc_op_add("Hello, ", name), "!");
}

function add(a, b) {
    b = b ?? 0;  // default value
    return _pyfunc_op_add(a, b);
}
```

!!! note "Why `_pyfunc_op_add`?"
    Python's `+` is polymorphic—it concatenates strings/lists and adds numbers. Without type information, Prescrypt uses a runtime helper to preserve this behavior.

!!! tip "Type Annotations Enable Cleaner Output"
    When parameter types are annotated, Prescrypt generates native operators:
    ```python
    def add(a: int, b: int) -> int:
        return a + b
    # → return (a + b);
    ```
    See [Optimization](optimization.md#type-informed-code-generation) for details.

### Lambda Functions

```python
double = lambda x: x * 2
items.sort(key=lambda x: x.name)
```

**Compiles to:**
```javascript
let double = (x) => x * 2;
items.sort((a, b) => { /* comparison using x.name */ });
```

### *args and **kwargs

```python
def log(*args):
    for arg in args:
        print(arg)

def configure(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}={value}")
```

**Compiles to:**
```javascript
function log(...args) {
    for (let arg of args) {
        console.log(arg);
    }
}

function configure(kwargs) {
    for (let [key, value] of Object.entries(kwargs)) {
        console.log(key + "=" + value);
    }
}
```

## Classes

### Basic Classes

```python
class Counter:
    def __init__(self, start=0):
        self.value = start

    def increment(self):
        self.value += 1
        return self.value

    def reset(self):
        self.value = 0
```

**Compiles to:**
```javascript
const Counter = function() {
    if (!(this instanceof Counter)) {
        return new Counter(...arguments);
    }
    this.value = arguments[0] ?? 0;
};

Counter.prototype.increment = function() {
    this.value += 1;
    return this.value;
};

Counter.prototype.reset = function() {
    this.value = 0;
};
```

### Inheritance

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return f"{self.name} says woof!"
```

## Control Flow

### If/Elif/Else

```python
if x > 0:
    print("positive")
elif x < 0:
    print("negative")
else:
    print("zero")
```

### For Loops

```python
# Iterate over list
for item in items:
    print(item)

# Iterate with index
for i, item in enumerate(items):
    print(f"{i}: {item}")

# Range-based loops
for i in range(10):
    print(i)

for i in range(1, 10, 2):  # 1, 3, 5, 7, 9
    print(i)
```

### While Loops

```python
while condition:
    do_something()
    if should_stop:
        break
    if should_skip:
        continue
```

### Comprehensions

```python
# List comprehension
squares = [x**2 for x in range(10)]
evens = [x for x in items if x % 2 == 0]

# Dict comprehension
counts = {word: len(word) for word in words}

# Set comprehension
unique_lengths = {len(word) for word in words}
```

**Compiles to:**
```javascript
let squares = Array.from({length: 10}, (_, x) => x ** 2);
let evens = items.filter(x => x % 2 === 0);

let counts = Object.fromEntries(words.map(word => [word, word.length]));

let unique_lengths = new Set(words.map(word => word.length));
```

## Exception Handling

```python
try:
    result = risky_operation()
except ValueError as e:
    print(f"Value error: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    cleanup()
```

**Compiles to:**
```javascript
try {
    let result = risky_operation();
} catch (_err) {
    if (_err instanceof ValueError) {
        let e = _err;
        console.log("Value error: " + e);
    } else {
        let e = _err;
        console.log("Error: " + e);
    }
} finally {
    cleanup();
}
```

## Async/Await

```python
async def fetch_data(url):
    response = await fetch(url)
    return await response.json()

async def main():
    data = await fetch_data("/api/users")
    print(data)
```

**Compiles to:**
```javascript
async function fetch_data(url) {
    let response = await fetch(url);
    return await response.json();
}

async function main() {
    let data = await fetch_data("/api/users");
    console.log(data);
}
```

## Built-in Functions

### Fully Supported

| Function | Notes |
|----------|-------|
| `len(x)` | Works on strings, lists, dicts |
| `range(...)` | All forms supported |
| `enumerate(x)` | Returns index-value pairs |
| `zip(a, b)` | Pairs from two iterables |
| `map(fn, x)` | Apply function to each item |
| `filter(fn, x)` | Keep items where fn returns true |
| `sorted(x)` | Return sorted copy |
| `reversed(x)` | Return reversed iterator |
| `sum(x)` | Sum of numbers |
| `min(x)`, `max(x)` | Min/max value |
| `abs(x)` | Absolute value |
| `round(x)` | Round to nearest integer |
| `int(x)`, `float(x)`, `str(x)` | Type conversion |
| `bool(x)` | Convert to boolean |
| `list(x)`, `dict(x)`, `set(x)` | Collection conversion |
| `isinstance(x, T)` | Type checking |
| `hasattr(x, name)` | Check attribute exists |
| `getattr(x, name)` | Get attribute value |
| `setattr(x, name, value)` | Set attribute value |
| `print(...)` | Output to console |

## Operators

### Comparison

```python
x == y    # equality (uses _pyfunc_op_equals for deep comparison)
x != y    # inequality
x < y     # less than
x <= y    # less or equal
x > y     # greater than
x >= y    # greater or equal
x is y    # identity (=== in JS)
x is not y
x in container    # membership
x not in container
```

### Logical

```python
a and b   # logical and
a or b    # logical or
not a     # logical not
```

### Arithmetic

```python
a + b     # addition / string concatenation
a - b     # subtraction
a * b     # multiplication / string repeat
a / b     # true division
a // b    # floor division
a % b     # modulo
a ** b    # exponentiation
-a        # negation
```

## See Also

- [Limitations](../reference/limitations.md) - What's not supported
- [Semantic Differences](../reference/differences.md) - Behavioral differences from Python
- [JavaScript Interop](js-interop.md) - Accessing JS APIs
