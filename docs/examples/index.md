# Examples

Complete, working examples that demonstrate Prescrypt in real-world scenarios.

## Quick Links

<div class="grid cards" markdown>

-   :material-web: **Browser Application**

    ---

    Interactive web app with DOM manipulation, events, and fetch API.

    [:octicons-arrow-right-24: Browser App](browser-app.md)

-   :material-console: **Node.js CLI Tool**

    ---

    Command-line tool with file I/O and argument parsing.

    [:octicons-arrow-right-24: Node.js CLI](nodejs-cli.md)

-   :material-folder-multiple: **Multi-file Project**

    ---

    Structured project with packages, imports, and shared utilities.

    [:octicons-arrow-right-24: Multi-file](multi-file.md)

</div>

## Running the Examples

Each example can be run with these steps:

### 1. Clone or Create Files

Copy the example code into your project directory.

### 2. Compile

```bash
# Single file
py2js example.py -m

# Project directory
py2js src/ -o dist/
```

### 3. Run

**Browser:**
```html
<script type="module" src="dist/main.js"></script>
```

**Node.js:**
```bash
node dist/main.js
```

## Example Categories

### By Complexity

| Example | Files | Concepts |
|---------|-------|----------|
| [Browser App](browser-app.md) | 1-2 | DOM, events, fetch |
| [Node.js CLI](nodejs-cli.md) | 1-2 | File I/O, process args |
| [Multi-file](multi-file.md) | 5+ | Packages, imports, structure |

### By Feature

| Feature | Best Example |
|---------|--------------|
| DOM manipulation | [Browser App](browser-app.md) |
| Async/await | [Browser App](browser-app.md) |
| File system | [Node.js CLI](nodejs-cli.md) |
| Module imports | [Multi-file](multi-file.md) |
| Class definitions | [Multi-file](multi-file.md) |
| Source maps | All examples |

## Minimal Examples

### Hello World

```python
print("Hello, World!")
```

```bash
py2js hello.py && node hello.js
```

### Browser Alert

```python
import js

js.alert("Hello from Prescrypt!")
```

```html
<script type="module" src="hello.js"></script>
```

### Simple Class

```python
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1
        return self.value

c = Counter()
print(c.increment())  # 1
print(c.increment())  # 2
```

### Async Fetch

```python
import js

async def get_data():
    response = await js.fetch("https://api.github.com")
    data = await response.json()
    print(data)

get_data()
```

## Next Steps

After exploring the examples:

- [Language Support](../guide/language-support.md) - Full feature reference
- [JavaScript Interop](../guide/js-interop.md) - Working with JS APIs
- [Limitations](../reference/limitations.md) - What to avoid
