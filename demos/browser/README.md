# Browser Demo: Todo App

A simple interactive todo list application demonstrating Prescrypt's browser capabilities.

## Features Demonstrated

- **DOM Manipulation**: Creating and updating HTML elements
- **Event Handling**: Form submission, click events, change events
- **State Management**: Module-level state with reactive rendering
- **List Comprehensions**: Filtering and counting todos

## Quick Start

### 1. Compile the Python source

```bash
# From this directory
py2js src/app.py -m -o dist/app.js

# Or with source maps for debugging
py2js src/app.py -m -s -o dist/app.js
```

### 2. Serve the files

```bash
# Using Python's built-in server
python -m http.server 8000

# Or any other static file server
npx serve .
```

### 3. Open in browser

Navigate to http://localhost:8000

## Project Structure

```
browser/
├── src/
│   └── app.py          # Python source code
├── dist/
│   └── app.js          # Generated JavaScript (after compilation)
├── index.html          # HTML page
└── README.md           # This file
```

## Debugging with Source Maps

When compiled with `-s`, you can debug the Python source directly:

1. Open browser DevTools (F12)
2. Go to **Sources** tab
3. Find `app.py` in the file tree (under `src/`)
4. Set breakpoints on any line
5. Interact with the app to hit breakpoints
6. Step through Python code!

## Key Code Patterns

### Event Handler with Closure

Use a factory function to capture loop variables:

```python
def make_handler(todo_id):
    """Create a handler that captures the current todo_id."""
    def handler(e):
        delete_todo(todo_id)
    return handler

for todo in todos:
    btn.addEventListener("click", make_handler(todo["id"]))
```

### DOM Element Creation

```python
import js

item = js.document.createElement("div")
item.className = "todo-item"
item.textContent = "Hello"
container.appendChild(item)
```

### Global State

```python
todos = []

def add_todo(text):
    global todos  # Not needed for append, but needed for reassignment
    todos.append({"text": text})
    render()
```

## See Also

- [Browser App Example](../../docs/examples/browser-app.md) - Full documentation
- [JavaScript Interop Guide](../../docs/guide/js-interop.md) - Browser API reference
