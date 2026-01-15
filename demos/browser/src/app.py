"""Todo List Application

A simple interactive todo app demonstrating Prescrypt browser capabilities:
- DOM manipulation
- Event handling
- State management
"""
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
        btn.className = "delete-btn"
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
    add_todo("Deploy to production")


# Run on page load
js.window.addEventListener("DOMContentLoaded", handle_load)
