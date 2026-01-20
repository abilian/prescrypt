"""Interactive Python Playground

A browser-based Python learning environment with server-side compilation.
Write Python code, compile it to JavaScript via the server, and run it instantly.
"""
import js


# ============================================================================
# Example Programs
# ============================================================================

EXAMPLES = [
    {
        "name": "hello",
        "title": "Hello World",
        "code": '''# Hello World - Your First Program
print("Hello, World!")
print("Welcome to Python in the browser!")
print()
print("This code is compiled to JavaScript")
print("by Prescrypt and runs in your browser.")
''',
    },
    {
        "name": "fibonacci",
        "title": "Fibonacci",
        "code": '''# Fibonacci Sequence
def fibonacci(n):
    """Generate first n Fibonacci numbers."""
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib[:n]

result = fibonacci(15)
print("Fibonacci sequence (first 15 numbers):")
print(result)
print()
print("Sum:", sum(result))
''',
    },
    {
        "name": "factorial",
        "title": "Factorial",
        "code": '''# Factorial with Recursion
def factorial(n):
    """Calculate n! recursively."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print("Factorials from 0 to 10:")
for i in range(11):
    print(str(i) + "! = " + str(factorial(i)))
''',
    },
    {
        "name": "primes",
        "title": "Prime Sieve",
        "code": '''# Sieve of Eratosthenes
def sieve(limit):
    """Find all primes up to limit."""
    is_prime = [True] * (limit + 1)
    is_prime[0] = False
    is_prime[1] = False

    i = 2
    while i * i <= limit:
        if is_prime[i]:
            j = i * i
            while j <= limit:
                is_prime[j] = False
                j += i
        i += 1

    result = []
    for i in range(limit + 1):
        if is_prime[i]:
            result.append(i)
    return result

primes = sieve(50)
print("Prime numbers up to 50:")
print(primes)
print()
print("Count:", len(primes))
''',
    },
    {
        "name": "sorting",
        "title": "Quicksort",
        "code": '''# Quicksort Algorithm
def quicksort(arr):
    """Classic quicksort implementation."""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

numbers = [64, 34, 25, 12, 22, 11, 90, 42, 88, 7]
print("Original:", numbers)
print("Sorted:  ", quicksort(numbers))
''',
    },
    {
        "name": "classes",
        "title": "Classes",
        "code": '''# Classes and Inheritance
class Animal:
    def __init__(self, name, sound):
        self.name = name
        self.sound = sound

    def speak(self):
        return self.name + " says " + self.sound + "!"

class Dog(Animal):
    def __init__(self, name):
        super().__init__(name, "Woof")

    def fetch(self):
        return self.name + " fetches the ball!"

class Cat(Animal):
    def __init__(self, name):
        super().__init__(name, "Meow")

rex = Dog("Rex")
print(rex.speak())
print(rex.fetch())
print()

whiskers = Cat("Whiskers")
print(whiskers.speak())
''',
    },
    {
        "name": "comprehensions",
        "title": "Comprehensions",
        "code": '''# Python Comprehensions

# List comprehension
squares = [x * x for x in range(1, 11)]
print("Squares 1-10:", squares)

# Filtered comprehension
evens = [x for x in range(20) if x % 2 == 0]
print("Even numbers:", evens)

# Dict comprehension
word = "hello"
counts = {}
for c in word:
    counts[c] = word.count(c)
print("Letter counts in 'hello':", counts)
''',
    },
    {
        "name": "fizzbuzz",
        "title": "FizzBuzz",
        "code": '''# FizzBuzz - Classic Interview Problem
result = []
for i in range(1, 31):
    if i % 15 == 0:
        result.append("FizzBuzz")
    elif i % 3 == 0:
        result.append("Fizz")
    elif i % 5 == 0:
        result.append("Buzz")
    else:
        result.append(str(i))

print("FizzBuzz 1-30:")
print(result)
''',
    },
]


# ============================================================================
# State
# ============================================================================

current_example = None
is_compiling = False


# ============================================================================
# UI Functions
# ============================================================================

def select_example(example):
    """Select and display an example."""
    global current_example
    current_example = example

    # Update editor
    editor = js.document.getElementById("code-editor")
    editor.value = example["code"]

    # Update active button
    for b in js.document.querySelectorAll(".example-btn"):
        b.classList.remove("active")

    active_btn = js.document.querySelector('[data-example="' + example["name"] + '"]')
    if active_btn:
        active_btn.classList.add("active")

    # Clear output
    output_el = js.document.getElementById("output")
    output_el.textContent = '(Click "Run" to execute)'
    output_el.className = "output empty"


def show_output(text, is_error=False):
    """Display output in the output panel."""
    output_el = js.document.getElementById("output")
    if text:
        output_el.textContent = text
        output_el.className = "output error" if is_error else "output"
    else:
        output_el.textContent = "(No output)"
        output_el.className = "output empty"


def show_compiling():
    """Show compiling state."""
    output_el = js.document.getElementById("output")
    output_el.textContent = "Compiling..."
    output_el.className = "output empty"

    run_btn = js.document.getElementById("run-btn")
    run_btn.textContent = "Compiling..."
    run_btn.disabled = True


def hide_compiling():
    """Hide compiling state."""
    run_btn = js.document.getElementById("run-btn")
    run_btn.textContent = "Run"
    run_btn.disabled = False


# ============================================================================
# Compilation and Execution
# ============================================================================

def execute_js(js_code):
    """Execute compiled JavaScript and capture output."""
    # Intercept console.log since Prescrypt's print() uses it internally
    wrapper_code = """
    (function() {
        var _output = [];
        var _originalLog = console.log;

        // Override console.log to capture output
        console.log = function() {
            var args = Array.prototype.slice.call(arguments);
            var text = args.map(function(a) {
                if (a === null) return 'None';
                if (a === undefined) return 'None';
                if (Array.isArray(a)) return '[' + a.join(', ') + ']';
                if (typeof a === 'object') return JSON.stringify(a);
                return String(a);
            }).join(' ');
            _output.push(text);
        };

        try {
            """ + js_code + """
        } catch (e) {
            console.log = _originalLog;
            return {error: e.toString()};
        }

        console.log = _originalLog;
        return {output: _output.join('\\n')};
    })()
    """

    try:
        result = js.eval(wrapper_code)
        if result.error:
            return {"error": result.error}
        return {"output": result.output}
    except Exception as e:
        return {"error": str(e)}


def handle_compile_response(response):
    """Handle the response from the compile server."""
    global is_compiling
    is_compiling = False
    hide_compiling()

    try:
        data = js.JSON.parse(response)

        if not data.success:
            show_output("Compilation error: " + str(data.error), is_error=True)
            return

        # Execute the compiled JavaScript
        result = execute_js(data.js)

        if "error" in result and result["error"]:
            show_output("Runtime error: " + result["error"], is_error=True)
        else:
            show_output(result.get("output", ""))

    except Exception as e:
        show_output("Error: " + str(e), is_error=True)


def handle_compile_error(error):
    """Handle compilation error."""
    global is_compiling
    is_compiling = False
    hide_compiling()
    show_output("Failed to connect to compile server. Make sure it's running:\n\n  python server.py", is_error=True)


def run_code():
    """Compile and run the code in the editor."""
    global is_compiling

    if is_compiling:
        return

    is_compiling = True
    show_compiling()

    editor = js.document.getElementById("code-editor")
    code = editor.value

    # Send to compile server
    # Create options object, then assign body separately to keep it as a string
    fetch_options = js.eval("({method: 'POST', headers: {'Content-Type': 'application/json'}})")
    fetch_options.body = js.JSON.stringify({"code": code})

    def on_response(response):
        response.text().then(handle_compile_response).catch(handle_compile_error)

    js.fetch("/compile", fetch_options).then(on_response).catch(handle_compile_error)


# ============================================================================
# Event Handlers
# ============================================================================

def make_example_handler(example):
    """Create click handler for example button."""
    def handler(e):
        select_example(example)
    return handler


def handle_keydown(e):
    """Handle keyboard shortcuts."""
    if (e.ctrlKey or e.metaKey) and e.key == "Enter":
        e.preventDefault()
        run_code()


def handle_run_click(e):
    """Handle run button click."""
    run_code()


# ============================================================================
# Initialization
# ============================================================================

def init():
    """Initialize the playground."""
    # Create example buttons
    examples_list = js.document.getElementById("examples")
    for example in EXAMPLES:
        li = js.document.createElement("li")
        btn = js.document.createElement("button")
        btn.textContent = example["title"]
        btn.className = "example-btn"
        btn.dataset.example = example["name"]
        btn.addEventListener("click", make_example_handler(example))
        li.appendChild(btn)
        examples_list.appendChild(li)

    # Run button
    run_btn = js.document.getElementById("run-btn")
    run_btn.addEventListener("click", handle_run_click)

    # Keyboard shortcuts
    editor = js.document.getElementById("code-editor")
    editor.addEventListener("keydown", handle_keydown)

    # Load first example
    select_example(EXAMPLES[0])


# Initialize on load
js.window.addEventListener("DOMContentLoaded", lambda e: init())
