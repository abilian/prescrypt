# Feature Matrix

Complete reference of Python features and their support status in Prescrypt.

## Legend

| Symbol | Meaning |
|--------|---------|
| :white_check_mark: | Fully supported |
| :material-check-circle-outline: | Partially supported |
| :x: | Not supported |

## Data Types

| Feature | Status | Notes |
|---------|--------|-------|
| `int` | :white_check_mark: | Maps to JavaScript `number` |
| `float` | :white_check_mark: | Maps to JavaScript `number` |
| `str` | :white_check_mark: | Full support including f-strings |
| `bool` | :white_check_mark: | `True`/`False` → `true`/`false` |
| `None` | :white_check_mark: | Maps to `null` |
| `list` | :white_check_mark: | Maps to `Array` |
| `dict` | :white_check_mark: | Maps to `Object` |
| `tuple` | :white_check_mark: | Treated as list |
| `set` | :white_check_mark: | Maps to ES6 `Set` |
| `frozenset` | :x: | Use `set` instead |
| `bytes` | :x: | Use `Uint8Array` via `js` |
| `bytearray` | :x: | Use typed arrays via `js` |
| `complex` | :x: | Not supported |

## Operators

### Arithmetic

| Operator | Status | Notes |
|----------|--------|-------|
| `+` | :white_check_mark: | Addition, string concatenation |
| `-` | :white_check_mark: | Subtraction |
| `*` | :white_check_mark: | Multiplication, string repeat |
| `/` | :white_check_mark: | True division |
| `//` | :white_check_mark: | Floor division |
| `%` | :white_check_mark: | Modulo |
| `**` | :white_check_mark: | Exponentiation |
| `@` | :x: | Matrix multiplication |

### Comparison

| Operator | Status | Notes |
|----------|--------|-------|
| `==`, `!=` | :white_check_mark: | Value equality (deep for objects) |
| `<`, `<=`, `>`, `>=` | :white_check_mark: | |
| `is`, `is not` | :white_check_mark: | Identity (`===`) |
| `in`, `not in` | :white_check_mark: | Membership |

### Logical

| Operator | Status | Notes |
|----------|--------|-------|
| `and` | :white_check_mark: | Short-circuit evaluation |
| `or` | :white_check_mark: | Short-circuit evaluation |
| `not` | :white_check_mark: | |

### Bitwise

| Operator | Status | Notes |
|----------|--------|-------|
| `&` | :white_check_mark: | Bitwise AND |
| `\|` | :white_check_mark: | Bitwise OR |
| `^` | :white_check_mark: | Bitwise XOR |
| `~` | :white_check_mark: | Bitwise NOT |
| `<<` | :white_check_mark: | Left shift |
| `>>` | :white_check_mark: | Right shift |

## Control Flow

| Feature | Status | Notes |
|---------|--------|-------|
| `if`/`elif`/`else` | :white_check_mark: | |
| `for` loop | :white_check_mark: | |
| `while` loop | :white_check_mark: | |
| `break` | :white_check_mark: | |
| `continue` | :white_check_mark: | |
| `pass` | :white_check_mark: | |
| `match`/`case` | :x: | Python 3.10+ pattern matching |

## Functions

| Feature | Status | Notes |
|---------|--------|-------|
| Basic functions | :white_check_mark: | |
| Default arguments | :white_check_mark: | |
| Keyword arguments | :white_check_mark: | |
| `*args` | :white_check_mark: | Rest parameters |
| `**kwargs` | :white_check_mark: | Object parameter |
| Lambda functions | :white_check_mark: | Arrow functions |
| Closures | :white_check_mark: | |
| Decorators | :material-check-circle-outline: | Basic support |
| `@staticmethod` | :material-check-circle-outline: | |
| `@classmethod` | :material-check-circle-outline: | |
| `@property` | :material-check-circle-outline: | |
| Generator functions | :x: | Use lists instead |
| `yield` | :x: | |
| `yield from` | :x: | |

## Classes

| Feature | Status | Notes |
|---------|--------|-------|
| Basic classes | :white_check_mark: | |
| `__init__` | :white_check_mark: | |
| Instance methods | :white_check_mark: | |
| Instance attributes | :white_check_mark: | |
| Single inheritance | :white_check_mark: | |
| Multiple inheritance | :x: | |
| `super()` | :white_check_mark: | |
| Class attributes | :white_check_mark: | |
| Private attributes (`_x`) | :white_check_mark: | Convention only |
| Properties | :material-check-circle-outline: | |
| `__str__`, `__repr__` | :material-check-circle-outline: | |
| `__eq__`, `__ne__` | :material-check-circle-outline: | |
| `__lt__`, `__le__`, etc. | :x: | |
| `__len__` | :material-check-circle-outline: | |
| `__getitem__`, `__setitem__` | :material-check-circle-outline: | |
| `__call__` | :x: | |
| `__enter__`, `__exit__` | :x: | |
| Metaclasses | :x: | |
| `@dataclass` | :x: | |
| ABC/abstract methods | :x: | |

## Exception Handling

| Feature | Status | Notes |
|---------|--------|-------|
| `try`/`except` | :white_check_mark: | |
| `try`/`finally` | :white_check_mark: | |
| `except ExceptionType` | :white_check_mark: | |
| `except ... as e` | :white_check_mark: | |
| Multiple `except` clauses | :white_check_mark: | |
| `raise` | :white_check_mark: | |
| `raise ... from ...` | :x: | |
| Custom exceptions | :white_check_mark: | |
| `else` clause | :white_check_mark: | |
| Exception groups | :x: | Python 3.11+ |

## Comprehensions

| Feature | Status | Notes |
|---------|--------|-------|
| List comprehension | :white_check_mark: | |
| Dict comprehension | :white_check_mark: | |
| Set comprehension | :white_check_mark: | |
| Generator expression | :material-check-circle-outline: | Converted to list |
| Nested comprehension | :white_check_mark: | |
| Multiple `for` clauses | :white_check_mark: | |
| `if` filtering | :white_check_mark: | |

## Async/Await

| Feature | Status | Notes |
|---------|--------|-------|
| `async def` | :white_check_mark: | |
| `await` | :white_check_mark: | |
| `async for` | :x: | |
| `async with` | :x: | |

## Imports

| Feature | Status | Notes |
|---------|--------|-------|
| `import module` | :white_check_mark: | |
| `from module import name` | :white_check_mark: | |
| `from module import *` | :white_check_mark: | |
| Relative imports | :white_check_mark: | |
| `as` aliases | :white_check_mark: | |
| Dynamic imports | :x: | |

## Built-in Functions

### Fully Supported

`abs`, `all`, `any`, `bool`, `chr`, `dict`, `enumerate`, `filter`, `float`, `hasattr`, `getattr`, `setattr`, `delattr`, `int`, `isinstance`, `len`, `list`, `map`, `max`, `min`, `ord`, `print`, `range`, `reversed`, `round`, `set`, `sorted`, `str`, `sum`, `tuple`, `zip`

### Partially Supported

| Function | Limitations |
|----------|-------------|
| `type()` | Returns string, not type object |
| `isinstance()` | Limited to basic types |
| `format()` | Basic formatting only |

### Not Supported

`__import__`, `breakpoint`, `callable`, `classmethod`, `compile`, `complex`, `dir`, `divmod`, `eval`, `exec`, `frozenset`, `globals`, `hash`, `help`, `hex`, `id`, `input`, `iter`, `locals`, `memoryview`, `next`, `object`, `oct`, `open`, `pow`, `property`, `repr`, `slice`, `staticmethod`, `super`, `vars`

## String Methods

| Method | Status |
|--------|--------|
| `capitalize()` | :white_check_mark: |
| `count()` | :white_check_mark: |
| `endswith()` | :white_check_mark: |
| `find()` | :white_check_mark: |
| `format()` | :material-check-circle-outline: |
| `index()` | :white_check_mark: |
| `isalnum()`, `isalpha()`, etc. | :white_check_mark: |
| `join()` | :white_check_mark: |
| `lower()` | :white_check_mark: |
| `lstrip()`, `rstrip()` | :white_check_mark: |
| `replace()` | :white_check_mark: |
| `split()` | :white_check_mark: |
| `startswith()` | :white_check_mark: |
| `strip()` | :white_check_mark: |
| `upper()` | :white_check_mark: |

## List Methods

| Method | Status |
|--------|--------|
| `append()` | :white_check_mark: |
| `clear()` | :white_check_mark: |
| `copy()` | :white_check_mark: |
| `count()` | :white_check_mark: |
| `extend()` | :white_check_mark: |
| `index()` | :white_check_mark: |
| `insert()` | :white_check_mark: |
| `pop()` | :white_check_mark: |
| `remove()` | :white_check_mark: |
| `reverse()` | :white_check_mark: |
| `sort()` | :white_check_mark: |

## Dict Methods

| Method | Status |
|--------|--------|
| `clear()` | :white_check_mark: |
| `copy()` | :white_check_mark: |
| `get()` | :white_check_mark: |
| `items()` | :white_check_mark: |
| `keys()` | :white_check_mark: |
| `pop()` | :white_check_mark: |
| `setdefault()` | :white_check_mark: |
| `update()` | :white_check_mark: |
| `values()` | :white_check_mark: |

## See Also

- [Limitations](limitations.md) - Detailed limitation explanations
- [Semantic Differences](differences.md) - Behavioral differences
- [Language Support](../guide/language-support.md) - Usage guide
