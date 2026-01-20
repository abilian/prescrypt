# Prescrypt Demos

Example applications showcasing Python-to-JavaScript transpilation with Prescrypt.

## Quick Start

Each demo follows a consistent structure:

```bash
cd demos/<demo-name>
make build   # Compile Python to JavaScript
make serve   # Start local server (optional)
```

## Available Demos

| Demo | Description | Key Features |
|------|-------------|--------------|
| [python-playground](python-playground/) | Interactive Python learning | Pre-compiled examples, live output |
| [validation-library](validation-library/) | Shared form validation | Backend/frontend code reuse |
| [data-dashboard](data-dashboard/) | Sales analytics dashboard | Canvas charts, data aggregation |
| [simulation](simulation/) | Predator-prey simulation | Lotka-Volterra model, animation |
| [browser-extension](browser-extension/) | Chrome/Firefox extension | Page analysis, price highlighting |
| [edge-worker](edge-worker/) | Cloudflare Workers | Bot detection, geo-blocking |
| [browser](browser/) | Basic browser example | Simple DOM manipulation |

## Demo Summaries

### Python Playground

Interactive environment with runnable Python examples: Fibonacci, factorial, prime numbers, sorting algorithms, classes, comprehensions, and FizzBuzz.

```python
def fibonacci(n: int) -> list:
    if n <= 0:
        return []
    fib = [0, 1]
    while len(fib) < n:
        fib.append(fib[-1] + fib[-2])
    return fib[:n]
```

### Validation Library

Share validation logic between Python backend and JavaScript frontend. Includes email validation with typo detection, password strength checking, phone number formatting, and credit card validation (Luhn algorithm).

```python
class ValidationResult:
    @staticmethod
    def ok():
        return ValidationResult(True, [])

    @staticmethod
    def error(message: str):
        return ValidationResult(False, [message])
```

### Data Dashboard

Sales analytics with KPI cards, bar charts, line charts, and pie charts. All rendering done with Canvas 2D API - no external libraries.

```python
def group_by(data: list, key: str) -> dict:
    groups = {}
    for item in data:
        k = item[key]
        if k not in groups:
            groups[k] = []
        groups[k].append(item)
    return groups
```

### Simulation

Predator-prey population dynamics using the Lotka-Volterra equations. Features real-time animation, parameter controls, and phase space visualization.

```python
def lotka_volterra_step(prey, predators, params):
    prey_change = (
        params.prey_birth_rate * prey
        - params.predation_rate * prey * predators
    ) * params.dt
    # ...
```

### Browser Extension

Chrome/Firefox extension written in Python. Analyzes web pages: highlights expensive items, estimates reading time, counts internal/external links, and provides text statistics.

```python
def highlight_prices():
    for el in js.document.querySelectorAll(".price"):
        price = parse_price(el.textContent)
        if price > Config.price_threshold:
            el.style.backgroundColor = "#fef3c7"
```

### Edge Worker

Cloudflare Workers edge computing logic. Includes bot detection, geo-blocking, A/B testing, and security header injection.

```python
def is_bot(user_agent: str) -> bool:
    ua_lower = user_agent.lower()
    for pattern in BOT_PATTERNS:
        if pattern in ua_lower:
            return True
    return False
```

## Common Patterns

### JavaScript FFI

Access browser APIs via `import js`:

```python
import js

# DOM manipulation
el = js.document.getElementById("my-id")
el.textContent = "Hello"

# Canvas
ctx = canvas.getContext("2d")
ctx.fillRect(0, 0, 100, 100)
```

### Event Handlers

Use factory functions to create handlers with closures:

```python
def make_click_handler(item):
    def handler(event):
        process(item)
    return handler

button.addEventListener("click", make_click_handler(data))
```

### Classes

Full class support including `@staticmethod`, `@classmethod`, and `@property`:

```python
class Config:
    @staticmethod
    def default():
        return Config(100, 200)

    @property
    def total(self):
        return self.a + self.b
```

## Requirements

- Python 3.9+
- Prescrypt (`pip install prescrypt` or `uv sync` in repo root)
- Modern browser (Chrome, Firefox, Safari, Edge, Brave)
