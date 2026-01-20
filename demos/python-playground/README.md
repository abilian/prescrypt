# Python Playground

An interactive Python learning environment in the browser.

## How It Works

1. User writes Python code in the browser editor
2. Code is sent to a local compile server
3. Server uses Prescrypt to compile Python to JavaScript
4. JavaScript is returned and executed in the browser
5. Output is captured and displayed

## Quick Start

```bash
make serve
```

Then open http://localhost:8000 in your browser.

## Features

- **Live compilation**: Edit Python, click Run, see results instantly
- **Example library**: Pre-built examples for learning
- **Keyboard shortcut**: Ctrl+Enter to run
- **Error handling**: Compilation and runtime errors displayed clearly

## Architecture

```
Browser                    Server (server.py)
   │                            │
   │  POST /compile             │
   │  { "code": "..." }         │
   ├───────────────────────────>│
   │                            │  Prescrypt compile
   │  { "js": "..." }           │
   │<───────────────────────────┤
   │                            │
   │  eval(js) + capture output │
   │                            │
```

## Example Programs

- **Hello World**: Basic print statements
- **Fibonacci**: Sequence generation with lists
- **Factorial**: Recursive functions
- **Prime Sieve**: Sieve of Eratosthenes algorithm
- **Quicksort**: Recursive sorting with list comprehensions
- **Classes**: Inheritance with super()
- **Comprehensions**: List and dict comprehensions
- **FizzBuzz**: Classic programming exercise

## Use Case

This demonstrates Prescrypt's value for **interactive Python learning platforms**:

- Fast compilation (milliseconds, not seconds)
- Small output size (<50KB typical)
- Real Python 3 syntax support
- Ideal for embedded tutorials and documentation

## Development

```bash
make build   # Compile frontend
make serve   # Run server on port 8000
make clean   # Remove build artifacts
```

## Files

- `server.py` - Compile server (handles /compile endpoint)
- `src/playground.py` - Frontend logic (compiled to JS)
- `index.html` - UI layout and styles
- `dist/playground.js` - Compiled frontend
