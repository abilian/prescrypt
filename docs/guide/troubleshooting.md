# Troubleshooting

Solutions to common problems when using Prescrypt.

## Common Errors

### "Unsupported feature: yield"

Prescrypt doesn't support generators. Use lists or async/await instead:

```python
# Instead of:
def gen():
    yield 1
    yield 2

# Use:
def get_items():
    return [1, 2]
```

For lazy evaluation, consider using callbacks or async iterators.

### "Multiple inheritance not supported"

JavaScript prototypes only support single inheritance:

```python
# Instead of:
class C(A, B):
    pass

# Use composition:
class C(A):
    def __init__(self):
        super().__init__()
        self.b = B()

    def b_method(self):
        return self.b.method()
```

### "Module not found"

Check your module paths:

```bash
# Add search paths with -M
py2js src/ -o dist/ -M lib/ -M vendor/
```

Ensure the module exists and the path is correct relative to the source file.

### "Invalid iterator target in for-loop"

Complex unpacking in for loops may not be supported:

```python
# Instead of:
for (a, b), c in items:
    pass

# Use:
for item in items:
    (a, b), c = item
```

### "Class decorators not supported"

Only `@property`, `@staticmethod`, and `@classmethod` are supported:

```python
# Not supported:
@dataclass
class Point:
    x: int
    y: int

# Use explicit __init__:
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

### ReferenceError in Browser

If you see `ReferenceError: X is not defined` in the browser console:

1. **Check module mode**: Browser ES6 modules run in strict mode. Compile with `-m`:
   ```bash
   py2js app.py -m -o app.js
   ```

2. **Check script type**: Use `type="module"` in your HTML:
   ```html
   <script type="module" src="app.js"></script>
   ```

3. **Check variable declarations**: All variables must be declared. This is usually a compiler bug - please report it.

### SyntaxError: Unexpected token 'export'

You're trying to run module-mode code in a non-module context:

**Node.js**: Add `"type": "module"` to package.json:
```json
{
  "type": "module"
}
```

**Browser**: Use `type="module"` on the script tag.

**Or compile without module mode** for standalone scripts:
```bash
py2js app.py  # No -m flag
```

## Debugging Tips

### Use Verbose Mode

See detailed compilation information:

```bash
py2js app.py -v
```

This shows:
- Files being compiled
- Module resolution
- Optimization passes applied

### Check Generated Code

Inspect the output without stdlib noise:

```bash
py2js app.py --no-stdlib
cat app.js
```

This makes it easier to see how your Python maps to JavaScript.

### Enable Source Maps

For browser debugging with original Python source:

```bash
py2js src/ -o dist/ -s
```

Then in browser DevTools:
1. Open Sources tab
2. Find your `.py` file
3. Set breakpoints in Python code

### Disable Optimizations

See unoptimized output to understand what the compiler generates:

```bash
py2js app.py --no-optimize
```

Constant folding and other optimizations are disabled, showing the raw translation.

### Compare Python and JavaScript

Run both and compare:

```bash
# Run Python
python app.py > py_output.txt

# Compile and run JavaScript
py2js app.py
node app.js > js_output.txt

# Compare
diff py_output.txt js_output.txt
```

### Debug with Console Logging

Add strategic print statements:

```python
import js

def process(data):
    js.console.log("Processing:", data)  # Browser console
    # or
    print("Processing:", data)  # stdout

    result = transform(data)
    js.console.log("Result:", result)
    return result
```

## Runtime Differences

### Numbers

JavaScript has only `number` (64-bit float), no separate integer type:

```python
# Python: arbitrary precision integers
big = 2 ** 100  # Works in Python

# JavaScript: loses precision beyond 2^53
# Use BigInt for large integers via js module
```

### Truthiness

Empty lists and dicts are falsy in Python but truthy in JavaScript:

```python
# Python: empty list is falsy
if []:
    print("truthy")  # Never prints

# In compiled JS, Prescrypt handles this correctly
# by using _pyfunc_truthy() helper
```

### String Methods

Most work identically, but some edge cases differ:

```python
# split() with no args
"a b  c".split()  # Python: ["a", "b", "c"]
# Prescrypt handles this correctly
```

## Performance Issues

### Large Stdlib

If your output is too large:

```bash
# Use tree-shaking (default)
py2js app.py  # Only includes used functions

# Check what's included
py2js app.py -v  # Shows stdlib functions used
```

### Slow Compilation

For large projects:

```bash
# Compile only changed files (coming soon)
# For now, use make or a build tool to track changes

# Or compile files individually
py2js src/changed_file.py -m -o dist/changed_file.js
```

## Getting Help

### Check the Documentation

- [Language Support](language-support.md) - What Python features work
- [Limitations](../reference/limitations.md) - What's not supported
- [Semantic Differences](../reference/differences.md) - Behavioral differences

### Report Issues

File bugs at: https://git.sr.ht/~sfermigier/prescrypt/issues

Include:
- Python code that fails
- Expected behavior
- Actual behavior or error message
- Prescrypt version (`py2js --version`)

### Minimal Reproduction

Create a minimal example that reproduces the issue:

```python
# minimal.py - smallest code that shows the bug
x = [1, 2, 3]
# ... minimal code here
print(result)
```

```bash
py2js minimal.py
node minimal.js
```
