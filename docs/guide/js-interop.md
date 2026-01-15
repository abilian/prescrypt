# JavaScript Interop

Prescrypt provides seamless access to JavaScript APIs through the `js` module.

## The `js` Module

Import `js` to access any JavaScript global:

```python
import js

# Access browser APIs
js.console.log("Hello from Python!")
js.document.getElementById("app").innerHTML = "Hello!"

# Access Node.js APIs
data = js.JSON.parse('{"name": "Alice"}')
```

The `js` module is special—it doesn't compile to an import. Instead, `js.X` becomes just `X` in JavaScript:

```python
js.console.log("Hello")    # → console.log("Hello")
js.window.location.href    # → window.location.href
js.Math.random()           # → Math.random()
```

## Browser APIs

### DOM Manipulation

```python
import js

# Get elements
element = js.document.getElementById("myId")
elements = js.document.querySelectorAll(".myClass")

# Modify content
element.innerHTML = "<strong>Bold text</strong>"
element.textContent = "Plain text"

# Modify styles
element.style.color = "red"
element.style.display = "none"

# Add/remove classes
element.classList.add("active")
element.classList.remove("hidden")
element.classList.toggle("selected")

# Attributes
element.setAttribute("data-id", "123")
value = element.getAttribute("data-id")
```

### Events

```python
import js

def handle_click(event):
    js.console.log("Clicked!", event.target)

button = js.document.getElementById("myButton")
button.addEventListener("click", handle_click)

# Remove listener
button.removeEventListener("click", handle_click)
```

### Fetch API

```python
import js

async def load_users():
    response = await js.fetch("/api/users")
    if response.ok:
        return await response.json()
    raise Exception(f"HTTP {response.status}")

async def post_data(url, data):
    response = await js.fetch(url, {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": js.JSON.stringify(data)
    })
    return await response.json()
```

### Timers

```python
import js

def delayed_action():
    js.console.log("Delayed!")

# setTimeout / setInterval
timer_id = js.setTimeout(delayed_action, 1000)
js.clearTimeout(timer_id)

interval_id = js.setInterval(delayed_action, 1000)
js.clearInterval(interval_id)
```

### Local Storage

```python
import js

# Store data
js.localStorage.setItem("username", "alice")

# Retrieve data
username = js.localStorage.getItem("username")

# Remove data
js.localStorage.removeItem("username")
js.localStorage.clear()
```

## Node.js APIs

### File System (fs)

```python
import js

# Synchronous read
content = js.require("fs").readFileSync("data.txt", "utf8")

# Or import the module
fs = js.require("fs")
data = fs.readFileSync("config.json", "utf8")
config = js.JSON.parse(data)
```

### Path Module

```python
import js

path = js.require("path")
full_path = path.join("/home", "user", "file.txt")
ext = path.extname("file.txt")  # ".txt"
base = path.basename("/home/user/file.txt")  # "file.txt"
```

### Process

```python
import js

# Environment variables
api_key = js.process.env.API_KEY

# Command line arguments
args = js.process.argv

# Current working directory
cwd = js.process.cwd()
```

## Creating JavaScript Objects

### Object Literals

Python dicts become JavaScript objects:

```python
import js

options = {
    "method": "POST",
    "headers": {
        "Content-Type": "application/json"
    },
    "body": js.JSON.stringify(data)
}

response = await js.fetch(url, options)
```

### Using `new`

For JavaScript constructors, call them directly (Prescrypt handles `new`):

```python
import js

# Create instances
date = js.Date()
regex = js.RegExp(r"\d+", "g")
map_obj = js.Map()
set_obj = js.Set()

# With arguments
date = js.Date(2024, 0, 15)  # January 15, 2024
```

### Typed Arrays

```python
import js

# Create typed arrays
buffer = js.ArrayBuffer(16)
view = js.Uint8Array(buffer)
view[0] = 255

# Float arrays
floats = js.Float32Array([1.0, 2.0, 3.0])
```

## Callbacks

Python functions work as JavaScript callbacks:

```python
import js

def on_load(event):
    js.console.log("Page loaded")

js.window.addEventListener("load", on_load)

# Array methods
items = [1, 2, 3, 4, 5]
doubled = list(js.Array.from(items).map(lambda x: x * 2))
```

## Promises and Async

JavaScript promises work with Python's `async`/`await`:

```python
import js

async def fetch_and_process():
    # fetch() returns a Promise
    response = await js.fetch("/api/data")
    data = await response.json()
    return data

# Multiple concurrent requests
async def fetch_all(urls):
    promises = [js.fetch(url) for url in urls]
    responses = await js.Promise.all(promises)
    return [await r.json() for r in responses]
```

## External JavaScript Libraries

### From CDN (Browser)

```html
<script src="https://cdn.example.com/library.js"></script>
<script type="module" src="app.js"></script>
```

```python
# app.py
import js

# Library is now a global
js.LibraryName.doSomething()
```

### From npm (Node.js)

```python
import js

# CommonJS require
lodash = js.require("lodash")
result = lodash.groupBy(items, "category")

# Or access directly
_ = js.require("lodash")
_.map([1, 2, 3], lambda x: x * 2)
```

## Best Practices

!!! tip "Use `js.` Prefix Consistently"
    Always use `js.` for JavaScript APIs to make it clear which calls are going to JavaScript:
    ```python
    # Clear JavaScript call
    js.console.log(data)

    # Python's print (uses stdlib)
    print(data)
    ```

!!! tip "Type Conversion"
    Be aware that Python collections become JavaScript equivalents:
    - `list` → `Array`
    - `dict` → `Object`
    - `tuple` → `Array`

    JavaScript objects accessed via `js.` return JavaScript types.

!!! warning "No Runtime Type Checking"
    JavaScript APIs don't have Python's type safety. Errors will be JavaScript runtime errors, not Python TypeErrors.

## See Also

- [Language Support](language-support.md) - Supported Python features
- [Async/Await](language-support.md#asyncawait) - Async programming
- [Browser App Example](../examples/browser-app.md) - Complete browser example
