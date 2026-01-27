# CLI Reference

The `py2js` command compiles Python files to JavaScript.

## Synopsis

```bash
py2js <input> [options]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `input` | Python file (`.py`) or directory to compile |

## Options

### Output Control

| Option | Description |
|--------|-------------|
| `-o`, `--output <path>` | Output file or directory |
| `-m`, `--module-mode` | Enable ES6 module mode with exports |
| `-M`, `--module-path <dir>` | Additional module search path (repeatable) |
| `-b`, `--bundle` | Bundle all imports into a single output file |
| `-w`, `--watch` | Watch for changes and recompile automatically |

### Optimization

| Option | Description |
|--------|-------------|
| `--no-stdlib` | Don't include runtime helpers |
| `--no-tree-shake` | Include full stdlib (disable tree-shaking) |
| `--no-optimize` | Disable constant folding and other optimizations |

### Debugging

| Option | Description |
|--------|-------------|
| `-s`, `--source-maps` | Generate `.js.map` files for debugging |
| `-v`, `--verbose` | Print detailed compilation info |
| `-q`, `--quiet` | Suppress all output except errors |

## Examples

### Single File

```bash
# Compile to same directory
py2js app.py
# Output: app.js

# Compile to specific file
py2js app.py -o build/app.js

# Compile with source maps
py2js app.py -s
# Output: app.js, app.js.map
```

### Directory

```bash
# Compile entire directory
py2js src/ -o dist/
# Note: Module mode is enabled automatically

# Compile with additional module paths
py2js src/ -o dist/ -M lib/ -M vendor/
```

### Module Mode

```bash
# Enable exports in single file
py2js app.py -m -o app.mjs

# Module mode generates ES6 exports
```

**Without `-m`** (core logic, stdlib omitted):
```javascript
function greet(name) { ... }
let message = greet("World");
```

**With `-m`** (core logic, stdlib omitted):
```javascript
export function greet(name) { ... }
export let message = greet("World");
```

### Bundling

Bundle multiple Python modules into a single JavaScript file:

```bash
# Bundle entry file with all its imports
py2js main.py -o bundle.js --bundle -M src/

# The bundler:
# - Recursively resolves all imports
# - Topologically sorts modules (dependencies first)
# - Combines tree-shaking across all modules
```

**Example project structure:**
```
src/
├── main.py           # Entry point
├── utils.py          # Imported by main.py
└── providers/
    ├── base.py       # Imported by github.py
    └── github.py     # Imported by main.py
```

**Bundle command:**
```bash
py2js src/main.py -o dist/bundle.js --bundle -M src/
```

This produces a single `bundle.js` with all modules combined and only the stdlib functions used by ANY module included.

### Watch Mode

Automatically recompile when files change:

```bash
# Watch single file
py2js app.py --watch

# Watch directory
py2js src/ -o dist/ --watch
```

Uses `watchdog` for efficient file system events if installed, otherwise falls back to polling.

### Optimization Control

```bash
# Disable all optimizations (for debugging)
py2js app.py --no-optimize

# Include full stdlib (no tree-shaking)
py2js app.py --no-tree-shake

# No stdlib at all (for embedding)
py2js app.py --no-stdlib
```

## File Handling

### Single File Compilation

```bash
py2js input.py                  # → input.js
py2js input.py -o output.js     # → output.js
py2js input.py -o build/        # → build/input.js
```

### Directory Compilation

When compiling a directory:

- All `.py` files are compiled recursively
- `__pycache__` and hidden directories are skipped
- `__init__.py` becomes `index.js`
- Module mode (`-m`) is enabled automatically

```bash
py2js myproject/ -o dist/

# Structure:
# myproject/           →  dist/
#   __init__.py        →    index.js
#   main.py            →    main.js
#   utils/             →    utils/
#     __init__.py      →      index.js
#     helpers.py       →      helpers.js
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Compilation error(s) |

## Environment

Prescrypt respects standard Python environment variables but doesn't require any special configuration.

## See Also

- [Quick Start](../getting-started/quickstart.md) - Getting started tutorial
- [Module System](modules.md) - How modules and imports work
- [Source Maps](source-maps.md) - Debugging with source maps
