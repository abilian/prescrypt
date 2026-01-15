# Browser Application Example

Build an interactive todo list application that runs in the browser.

## Project Structure

```
todo-app/
├── src/
│   └── app.py
├── dist/
│   └── app.js     # Generated
└── index.html
```

## The Code

### app.py

```python
"""Todo List Application"""
import js

# Application state
todos = []
next_id = 1


def add_todo(text):
    """Add a new todo item."""
    global next_id
    todo = {
        "id": next_id,
        "text": text,
        "completed": False
    }
    todos.append(todo)
    next_id += 1
    render()


def toggle_todo(todo_id):
    """Toggle a todo's completed status."""
    for todo in todos:
        if todo["id"] == todo_id:
            todo["completed"] = not todo["completed"]
            break
    render()


def delete_todo(todo_id):
    """Delete a todo item."""
    global todos
    todos = [t for t in todos if t["id"] != todo_id]
    render()


def make_toggle_handler(todo_id):
    """Create a toggle handler for a specific todo."""
    def handler(e):
        toggle_todo(todo_id)
    return handler


def make_delete_handler(todo_id):
    """Create a delete handler for a specific todo."""
    def handler(e):
        delete_todo(todo_id)
    return handler


def render():
    """Render the todo list to the DOM."""
    container = js.document.getElementById("todo-list")
    container.innerHTML = ""

    for todo in todos:
        item = js.document.createElement("div")
        item.className = "todo-item"
        if todo["completed"]:
            item.className += " completed"

        # Checkbox
        checkbox = js.document.createElement("input")
        checkbox.type = "checkbox"
        checkbox.checked = todo["completed"]
        checkbox.addEventListener("change", make_toggle_handler(todo["id"]))

        # Text
        span = js.document.createElement("span")
        span.textContent = todo["text"]

        # Delete button
        btn = js.document.createElement("button")
        btn.textContent = "Delete"
        btn.addEventListener("click", make_delete_handler(todo["id"]))

        item.appendChild(checkbox)
        item.appendChild(span)
        item.appendChild(btn)
        container.appendChild(item)

    # Update count
    completed = len([t for t in todos if t["completed"]])
    total = len(todos)
    js.document.getElementById("status").textContent = f"{completed}/{total} completed"


def handle_submit(event):
    """Handle form submission."""
    event.preventDefault()
    input_el = js.document.getElementById("todo-input")
    text = input_el.value.strip()
    if text:
        add_todo(text)
        input_el.value = ""


def handle_load(e):
    """Handle page load."""
    init()


def init():
    """Initialize the application."""
    form = js.document.getElementById("todo-form")
    form.addEventListener("submit", handle_submit)

    # Add some sample todos
    add_todo("Learn Prescrypt")
    add_todo("Build something cool")


# Run on page load
js.window.addEventListener("DOMContentLoaded", handle_load)
```

### index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo App - Prescrypt</title>
    <style>
        body {
            font-family: system-ui, sans-serif;
            max-width: 500px;
            margin: 50px auto;
            padding: 20px;
        }
        .todo-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        .todo-item.completed span {
            text-decoration: line-through;
            color: #888;
        }
        .todo-item span {
            flex: 1;
        }
        form {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input[type="text"] {
            flex: 1;
            padding: 10px;
            font-size: 16px;
        }
        button {
            padding: 10px 20px;
            cursor: pointer;
        }
        #status {
            color: #666;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>Todo List</h1>

    <form id="todo-form">
        <input type="text" id="todo-input" placeholder="What needs to be done?">
        <button type="submit">Add</button>
    </form>

    <div id="todo-list"></div>
    <div id="status"></div>

    <script type="module" src="dist/app.js"></script>
</body>
</html>
```

## Compile and Run

```bash
# Create project structure
mkdir -p todo-app/src todo-app/dist
cd todo-app

# Copy app.py to src/
# Copy index.html to project root

# Compile
py2js src/app.py -m -o dist/app.js

# Serve (any static server works)
python -m http.server 8000

# Open http://localhost:8000 in browser
```

## With Source Maps

For debugging, add source maps:

```bash
py2js src/app.py -m -s -o dist/app.js
```

Now you can:

1. Open browser DevTools (F12)
2. Go to Sources tab
3. Find `app.py` in the file tree
4. Set breakpoints in Python code
5. Step through Python while running JavaScript

## Key Patterns

### Event Handlers

```python
# Named function handler
def handle_click(event):
    event.preventDefault()
    process_click()

button.addEventListener("click", handle_click)
```

### Closure for Loop Variables

Use factory functions to capture loop variables:

```python
def make_delete_handler(todo_id):
    """Create a handler that captures the current todo_id."""
    def handler(e):
        delete_todo(todo_id)
    return handler

for todo in todos:
    btn.addEventListener("click", make_delete_handler(todo["id"]))
```

### DOM Creation

```python
# Create element
el = js.document.createElement("div")
el.className = "my-class"
el.textContent = "Content"

# Append to parent
parent.appendChild(el)

# Set HTML (be careful with user input!)
el.innerHTML = "<strong>Bold</strong>"
```

### State Management

```python
# Module-level state
state = {"count": 0}

def increment():
    state["count"] += 1
    render()

def render():
    js.document.getElementById("count").textContent = str(state["count"])
```

## Async Version

Here's the same app with async data persistence:

```python
import js

API_URL = "/api/todos"


async def load_todos():
    """Load todos from API."""
    global todos
    response = await js.fetch(API_URL)
    todos = await response.json()
    render()


async def save_todo(todo):
    """Save a new todo to API."""
    await js.fetch(API_URL, {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": js.JSON.stringify(todo)
    })


async def add_todo(text):
    """Add and save a new todo."""
    todo = {"text": text, "completed": False}
    await save_todo(todo)
    await load_todos()


def init():
    # Load initial data
    load_todos()
```

## See Also

- [JavaScript Interop](../guide/js-interop.md) - Browser API reference
- [Source Maps](../guide/source-maps.md) - Debugging guide
- [Node.js CLI](nodejs-cli.md) - Server-side example
