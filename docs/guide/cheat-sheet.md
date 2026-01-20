# Prescrypt Cheat Sheet

A quick reference for Python developers writing JavaScript applications with Prescrypt.

---

## Quick Start

```bash
# Compile Python to JavaScript
py2js myapp.py -o myapp.js

# With source maps (for debugging)
py2js myapp.py -o myapp.js -s

# Include full stdlib (no tree-shaking)
py2js myapp.py -o myapp.js -m
```

---

## JavaScript Interop

Access JavaScript globals via the `js` module:

```python
import js

# DOM manipulation
el = js.document.getElementById("myid")
el.textContent = "Hello"
el.classList.add("active")

# Window and console
js.console.log("Debug message")
js.window.alert("Hello!")

# Timers
js.setTimeout(lambda: print("delayed"), 1000)

# JSON
data = js.JSON.parse('{"x": 1}')
text = js.JSON.stringify({"x": 1})
```

### Creating JavaScript Objects

```python
# Use js.eval for object literals (Object.new() doesn't work)
options = js.eval("({method: 'POST', headers: {}})")
options.body = "data"

# Access object properties
value = obj.property      # obj.property
value = obj["key"]        # obj["key"]
```

### Fetch API

```python
def on_response(response):
    response.text().then(handle_text)

def handle_text(text):
    data = js.JSON.parse(text)
    print(data.message)

options = js.eval("({method: 'POST', headers: {'Content-Type': 'application/json'}})")
options.body = js.JSON.stringify({"key": "value"})
js.fetch("/api/endpoint", options).then(on_response)
```

### Event Handlers

```python
def handle_click(event):
    event.preventDefault()
    print("Clicked:", event.target.id)

btn = js.document.getElementById("my-btn")
btn.addEventListener("click", handle_click)

# Factory pattern for closures
def make_handler(value):
    def handler(e):
        print("Value:", value)
    return handler

btn.addEventListener("click", make_handler(42))
```

---

## Supported Python Features

### Classes

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return self.name + " makes a sound"

class Dog(Animal):
    def __init__(self, name):
        super().__init__(name)  # super() works

    def speak(self):
        return self.name + " barks"

# Decorators
class MyClass:
    @staticmethod
    def static_method(x):
        return x * 2

    @classmethod
    def class_method(cls, x):
        return cls(x)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v
```

### Comprehensions

```python
squares = [x * x for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
doubled = {k: v * 2 for k in d}  # dict comprehension
```

### Async/Await

```python
async def fetch_data(url):
    response = await js.fetch(url)
    data = await response.json()
    return data
```

### Generators

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

for x in countdown(5):
    print(x)
```

### Context Managers

```python
class MyContext:
    def __enter__(self):
        print("entering")
        return self

    def __exit__(self, *args):
        print("exiting")

with MyContext() as ctx:
    print("inside")
```

### Lambdas with Defaults

```python
add = lambda x, y=1: x + y
```

---

## What Doesn't Work (Workarounds)

### Tuple Unpacking

```python
# NOT SUPPORTED
a, b = get_pair()
for k, v in dict.items():
for i, x in enumerate(lst):

# WORKAROUND: Use indexing
result = get_pair()
a = result[0]
b = result[1]

for k in my_dict:
    v = my_dict[k]

for i in range(len(lst)):
    x = lst[i]
```

### F-String Format Specifiers

```python
# NOT SUPPORTED (compiler hangs or wrong output)
f"{x:,}"      # thousands separator
f"{x:.2f}"    # fixed precision
f"{x:>10}"    # width/alignment

# WORKAROUND: Use str() and string methods
str(int(x))              # instead of f"{x:.0f}"
str(round(x, 2))         # instead of f"{x:.2f}"
str(x).rjust(10)         # instead of f"{x:>10}"
```

### Variable Scoping in Loops

```python
# PROBLEM: Variables reused across loops cause strict mode errors
for x in list1:
    print(x)
for x in list2:  # Error: x already declared
    print(x)

# WORKAROUND: Use unique variable names
for x1 in list1:
    print(x1)
for x2 in list2:
    print(x2)
```

### Variables First Assigned in Conditionals

```python
# PROBLEM: Variable not declared before conditional
if condition:
    result = "yes"
else:
    result = "no"  # Error: assignment to undeclared variable

# WORKAROUND: Declare before conditional
result = None
if condition:
    result = "yes"
else:
    result = "no"
```

### Chained Assignment with Subscripts

```python
# NOT SUPPORTED
a[0] = a[1] = False

# WORKAROUND: Split into separate statements
a[0] = False
a[1] = False
```

### dict.get() with Default

```python
# May not work as expected
value = d.get("key", default)

# WORKAROUND: Use explicit check
if "key" in d:
    value = d["key"]
else:
    value = default
```

### Generator Expressions in Builtins

```python
# May not work
total = sum(x["value"] for x in data)

# WORKAROUND: Use explicit loop
total = 0
for x in data:
    total += x["value"]
```

---

## JavaScript Differences

| Python | JavaScript (Prescrypt) |
|--------|------------------------|
| `4.0` | `4` (no float distinction) |
| `100/0` → ZeroDivisionError | `Infinity` |
| `print(end="")` | Always adds newline |
| `None` | `null` |
| `True`/`False` | `true`/`false` |

---

## Standard Library

Supported builtins: `print`, `len`, `range`, `enumerate`, `zip`, `map`, `filter`, `sorted`, `reversed`, `sum`, `min`, `max`, `abs`, `round`, `int`, `float`, `str`, `bool`, `list`, `dict`, `set`, `tuple`, `isinstance`, `hasattr`, `getattr`, `setattr`

String methods: Most common methods work (`split`, `join`, `strip`, `replace`, `startswith`, `endswith`, `upper`, `lower`, `count`, `find`, `index`, etc.)

List methods: `append`, `extend`, `insert`, `remove`, `pop`, `clear`, `index`, `count`, `sort`, `reverse`, `copy`

Dict methods: `keys`, `values`, `items`, `get`, `pop`, `update`, `clear`, `copy`

---

## Project Structure Example

```
my-project/
├── src/
│   └── app.py          # Python source
├── dist/
│   └── app.js          # Compiled JavaScript
├── index.html          # HTML that loads app.js
└── Makefile
```

```makefile
build:
	py2js src/app.py -o dist/app.js -s

serve: build
	python -m http.server 8000

clean:
	rm -rf dist/*.js dist/*.map
```

```html
<!DOCTYPE html>
<html>
<head>
    <title>My App</title>
</head>
<body>
    <div id="app"></div>
    <script src="dist/app.js"></script>
</body>
</html>
```

---

## Tips

1. **Test incrementally**: Compile and test small pieces of code to catch unsupported patterns early.

2. **Check browser console**: Runtime errors appear in the browser's developer console.

3. **Use source maps**: The `-s` flag generates source maps for easier debugging.

4. **Avoid Python-isms**: Stick to simple patterns; avoid (for now) advanced unpacking, walrus operator, match statements.

5. **JS objects vs Python dicts**: When working with JS APIs, results are JS objects (use `.property`), not Python dicts (no `.get()` method).
