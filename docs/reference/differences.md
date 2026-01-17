# Semantic Differences

While Prescrypt aims to preserve Python semantics, some behaviors differ due to JavaScript's runtime. This page documents these differences.

## Number Handling

### No Integer Type

JavaScript has only `number` (64-bit float). Python's arbitrary-precision integers become floats.

```python
# Python: Works with arbitrary precision
big = 2 ** 100

# JavaScript: Loses precision beyond 2^53
# 2**100 becomes 1.2676506002282294e+30
```

**Safe range:** Integers from -2^53 to 2^53 (about ±9 quadrillion) are exact.

**For large integers:** Use JavaScript's `BigInt`:

```python
import js
big = js.BigInt("12345678901234567890")
```

### Division Behavior

```python
# True division - same behavior
5 / 2    # Python: 2.5, JavaScript: 2.5

# Floor division - same behavior
5 // 2   # Python: 2, JavaScript: 2

# Modulo with negatives - DIFFERENT!
-7 % 3   # Python: 2, JavaScript: -1
```

**Prescrypt handles this:** The generated code uses a helper that matches Python semantics.

### Float Precision

```python
0.1 + 0.2    # Python: 0.30000000000000004
             # JavaScript: 0.30000000000000004 (same!)
```

Both languages have the same IEEE 754 quirks.

## String Handling

### Unicode

Both Python and JavaScript use Unicode strings, but:

```python
# Length counts UTF-16 code units in JavaScript
emoji = "👍"
len(emoji)   # Python: 1
             # JavaScript: 2 (surrogate pair)

# Indexing differs
emoji[0]     # Python: "👍"
             # JavaScript: "\ud83d" (half of surrogate)
```

### String Methods

Most string methods work identically. Exceptions:

```python
# split() with no argument
"a b  c".split()      # Python: ["a", "b", "c"]
                      # Must use custom implementation

# split() with separator
"a,b,c".split(",")    # Same in both: ["a", "b", "c"]
```

Prescrypt provides correct implementations for these cases.

## Boolean Handling

### Truthiness

Python and JavaScript have different "falsy" values:

| Value | Python | JavaScript |
|-------|--------|------------|
| `0` | Falsy | Falsy |
| `""` | Falsy | Falsy |
| `[]` | Falsy | **Truthy** |
| `{}` | Falsy | **Truthy** |
| `None`/`null` | Falsy | Falsy |
| `NaN` | Falsy | Falsy |

```python
# This differs!
if []:         # Python: False
    print("empty list is truthy")  # Never prints

# JavaScript equivalent:
# if ([]) { ... }  // Would print!
```

**Prescrypt handles this:** Boolean coercion uses helpers that match Python semantics.

### Boolean Operations

Short-circuit evaluation returns the deciding value:

```python
# Same behavior in both
x = a or b      # Returns a if truthy, else b
x = a and b     # Returns b if a is truthy, else a
```

## Equality

### `==` vs `is`

```python
a == b    # Value equality (Prescrypt uses deep comparison for objects)
a is b    # Identity (=== in JavaScript)
```

```python
# List comparison
[1, 2] == [1, 2]   # Python: True, Prescrypt: True (deep comparison)
[1, 2] is [1, 2]   # Python: False, JavaScript: false
```

### `None` Comparison

```python
x is None     # Compiles to: x === null
x == None     # Compiles to: x == null (also matches undefined)
```

## Dictionary Behavior

### Key Types

Python dicts can have various hashable keys. JavaScript objects only have string keys.

```python
d = {1: "one", "1": "string one"}
# Python: Two different keys
# JavaScript: Same key! "1" overwrites

d[(1, 2)]: "tuple key"
# Python: Works
# JavaScript: Key becomes "[1,2]" string
```

**Recommendation:** Use string keys for predictable behavior.

### Iteration Order

Both Python 3.7+ and modern JavaScript preserve insertion order.

```python
d = {"b": 2, "a": 1, "c": 3}
for k in d:
    print(k)  # Both: b, a, c
```

## List/Array Behavior

### Negative Indexing

```python
items = [1, 2, 3, 4, 5]
items[-1]    # Python: 5
             # JavaScript native: undefined
```

**Prescrypt handles this:** Negative indices are converted at compile time or runtime.

### Slice Behavior

```python
items[1:3]      # Both: [2, 3]
items[::2]      # Python: [1, 3, 5]
                # Prescrypt: Uses helper function
items[::-1]     # Python: [5, 4, 3, 2, 1]
                # Prescrypt: Uses helper function
```

### Out-of-Bounds Access

```python
items = [1, 2, 3]
items[10]    # Python: IndexError
             # JavaScript: undefined
```

**Prescrypt behavior:** Returns `undefined` (JavaScript behavior), not an error.

## Class Behavior

### `self` Translation

```python
class MyClass:
    def method(self):
        print(self.value)

# JavaScript: this.value
```

**Watch out:** JavaScript's `this` binding is different from Python's `self`:

```python
obj = MyClass()
callback = obj.method
callback()  # Python: Works
            # JavaScript: `this` is undefined/wrong
```

**Fix:** Use arrow functions or `.bind()`:

```python
import js
button.addEventListener("click", lambda e: obj.method())
# Or: js.Function.prototype.bind.call(obj.method, obj)
```

### Inheritance

Single inheritance works as expected:

```python
class Child(Parent):
    def __init__(self):
        super().__init__()
```

The prototype chain is set up correctly.

## Exception Handling

### Exception Types

Python built-in exceptions are mapped to JavaScript errors:

```python
raise ValueError("bad value")
# JavaScript: throw new Error("bad value")
```

Catching works, but `except ValueError` catches based on error message patterns:

```python
try:
    something()
except ValueError as e:
    # Catches errors that look like ValueError
    print(e)
```

### Exception Chaining

Not supported:

```python
# Not supported
raise NewError("...") from original_error
```

## Scope

### Variable Declarations

Prescrypt correctly determines `let` vs `const`:

```python
x = 1        # let x = 1
x = 2        # x = 2

CONSTANT = 1  # const CONSTANT = 1 (if never reassigned)
```

### Closure Behavior

Works as expected:

```python
def make_adder(n):
    def add(x):
        return x + n
    return add

add5 = make_adder(5)
add5(3)  # 8
```

### Global Variables

```python
x = 1

def modify():
    global x
    x = 2

modify()
print(x)  # 2
```

Works correctly—`global` is recognized and handled.

## Iteration

### `for` Loop Variables

```python
for i in range(3):
    pass
print(i)  # Python: 2
          # JavaScript: 2 (same with let)
```

### Loop Closures

```python
funcs = []
for i in range(3):
    funcs.append(lambda: i)

[f() for f in funcs]
# Python: [2, 2, 2] (all capture same i)
# Prescrypt: [2, 2, 2] (same behavior)
```

**Fix:** Use a factory function:

```python
def make_func(val):
    return lambda: val

funcs = []
for i in range(3):
    funcs.append(make_func(i))  # Capture current value

[f() for f in funcs]  # [0, 1, 2]
```

!!! warning "Lambda Default Args Not Supported"
    The Python idiom `lambda i=i: i` does NOT work in Prescrypt. Use factory functions instead.

### Generator Iteration Timing

When iterating over generators with `for` loops, Prescrypt converts the generator to an array before iterating. This means all `yield` statements execute before the loop body runs.

```python
def gen():
    print("yielding 1")
    yield 1
    print("yielding 2")
    yield 2

for x in gen():
    print(f"got {x}")

# Python output:
# yielding 1
# got 1
# yielding 2
# got 2

# Prescrypt output:
# yielding 1
# yielding 2
# got 1
# got 2
```

**Why:** JavaScript `for` loops don't natively support iterators in the same way. The generated code uses `[...generator]` to convert to an array first.

**Impact:** This affects interleaved output timing but doesn't affect correctness for most use cases. The final values are the same.

**Workaround:** If you need true lazy evaluation, use `while` with `next()`:

```python
it = gen()
while True:
    try:
        x = next(it)
        print(f"got {x}")
    except StopIteration:
        break
```

## See Also

- [Limitations](limitations.md) - What's not supported
- [Feature Matrix](features.md) - Complete feature support
- [JavaScript Interop](../guide/js-interop.md) - Working around differences
