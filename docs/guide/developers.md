# Developer Guide

This guide explains Prescrypt's architecture and how to extend or modify the compiler.

## Architecture Overview

Prescrypt is a source-to-source compiler (transpiler) that converts Python AST to JavaScript code.

```
┌─────────────┐     ┌──────────┐     ┌────────┐     ┌─────────┐     ┌────────────┐
│ Python      │     │          │     │        │     │         │     │ JavaScript │
│ Source      │────▶│  Parser  │────▶│ Desugar│────▶│ Binder  │────▶│  CodeGen   │
│             │     │          │     │        │     │         │     │            │
└─────────────┘     └──────────┘     └────────┘     └─────────┘     └────────────┘
                         │                │              │               │
                         ▼                ▼              ▼               ▼
                       AST            Simplified      Scoped          JavaScript
                                        AST           AST              Output
```

### Compilation Phases

1. **Parsing**: Python's `ast` module parses source into AST
2. **Desugaring**: Simplifies complex syntax (`a += b` → `a = a + b`)
3. **Binding**: Analyzes scopes, tracks variable declarations
4. **Code Generation**: Produces JavaScript output

## Source Layout

```
src/prescrypt/
├── main.py              # CLI entry point (py2js command)
├── compiler.py          # Main Compiler class
├── constants.py         # Operator mappings, reserved names
├── namespace.py         # Variable scope tracking
├── exceptions.py        # Custom exceptions with location info
├── sourcemap.py         # Source map generation
│
├── front/               # Frontend: parsing and analysis
│   ├── ast/             # AST utilities and custom nodes
│   │   ├── __init__.py  # Re-exports from Python ast
│   │   └── utils.py     # AST helper functions
│   └── passes/          # Compiler passes
│       ├── binder.py    # Scope analysis
│       ├── desugar.py   # Syntax simplification
│       └── type_inference.py  # Basic type inference
│
├── codegen/             # Backend: JavaScript generation
│   ├── main.py          # CodeGen class, singledispatch routing
│   ├── utils.py         # Code generation utilities
│   ├── _expressions/    # Expression handlers
│   │   ├── calls.py     # Function/method calls
│   │   ├── ops.py       # Operators (+, -, ==, etc.)
│   │   ├── comprehensions.py  # List/dict/set comprehensions
│   │   └── ...
│   ├── _statements/     # Statement handlers
│   │   ├── functions.py # Function definitions
│   │   ├── classes.py   # Class definitions
│   │   ├── control_flow.py  # if/for/while/try
│   │   └── ...
│   └── stdlib_py/       # Python stdlib implementations
│       ├── functions.py # Built-in functions (len, range, etc.)
│       └── methods.py   # Built-in methods (str.split, etc.)
│
├── stdlibjs/            # JavaScript runtime library
│   ├── functions.js     # _pyfunc_* implementations
│   └── methods.js       # _pymeth_* implementations
│
└── tools/               # Build tools
    ├── gen_ast.py       # Generate AST documentation
    └── gen_stdlibjs.py  # Bundle stdlib JS files
```

## Key Design Patterns

### Single Dispatch

Code generation uses `functools.singledispatch` for routing AST nodes to handlers:

```python
# In codegen/main.py
from functools import singledispatch

@singledispatch
def gen_expr(node, codegen: CodeGen) -> str:
    """Generate JavaScript for an expression node."""
    raise NotImplementedError(f"gen_expr not implemented for {type(node)}")

# In codegen/_expressions/ops.py
@gen_expr.register
def gen_binop(node: ast.BinOp, codegen: CodeGen) -> str:
    left = codegen.gen_expr(node.left)
    right = codegen.gen_expr(node.right)
    op = get_js_operator(node.op)
    return f"({left} {op} {right})"
```

This allows adding new node handlers in separate files without modifying the core.

### Two-Layer Stdlib

Python built-ins can be implemented in two ways:

1. **Python handlers** (`codegen/stdlib_py/`): Generate inline JS at compile time
2. **JavaScript runtime** (`stdlibjs/`): Runtime functions included in output

Example - `len()` function:

```python
# In codegen/stdlib_py/functions.py
def function_len(codegen: CodeGen, node: ast.Call) -> str:
    """Generate code for len()."""
    arg = codegen.gen_expr(node.args[0])
    # For simple cases, inline the JS
    return f"{arg}.length"
    # For complex cases, use runtime helper
    # return f"_pyfunc_op_len({arg})"
```

```javascript
// In stdlibjs/functions.js
var _pyfunc_op_len = function(x) {
    if (x.__len__) return x.__len__();
    return x.length;
};
```

### Naming Conventions

| Prefix | Meaning | Example |
|--------|---------|---------|
| `_pyfunc_` | Python built-in function | `_pyfunc_range` |
| `_pymeth_` | Python method on built-in type | `_pymeth_split` |
| `_pytmp_` | Compiler-generated temporary | `_pytmp_1_seq` |

## Adding New Features

### Adding a New Built-in Function

1. **Add Python handler** in `codegen/stdlib_py/functions.py`:

```python
def function_mybuiltin(codegen: CodeGen, node: ast.Call) -> str:
    """Handle mybuiltin() calls."""
    if len(node.args) != 1:
        raise JSError("mybuiltin() takes exactly 1 argument", node)
    arg = codegen.gen_expr(node.args[0])
    return f"_pyfunc_mybuiltin({arg})"
```

2. **Register it** in `STDLIB_FUNCTIONS` dict in the same file.

3. **Add JavaScript implementation** in `stdlibjs/functions.js`:

```javascript
var _pyfunc_mybuiltin = function(x) {
    // Implementation
    return result;
};
```

4. **Add to tree-shaking** if it has dependencies (in `stdlib_js.py`).

5. **Add tests** in `tests/integration/` or `codegen/stdlib_py/tests/`.

### Adding a New AST Node Handler

1. **Identify the AST node type** using `ast.dump()`:

```python
import ast
print(ast.dump(ast.parse("your_code_here")))
```

2. **Create handler** in appropriate module:

```python
# For expressions: codegen/_expressions/
# For statements: codegen/_statements/

@gen_expr.register  # or @gen_stmt.register
def gen_mynode(node: ast.MyNode, codegen: CodeGen) -> str:
    # Generate JavaScript
    return "generated_js"
```

3. **Add tests** that compile Python and verify output.

### Adding a New Compiler Pass

1. **Create pass module** in `front/passes/`:

```python
# front/passes/my_pass.py
import ast

class MyPass(ast.NodeTransformer):
    """Transform AST for optimization/analysis."""

    def visit_SomeNode(self, node):
        # Transform node
        return new_node
```

2. **Integrate into compiler** in `compiler.py`:

```python
from .front.passes.my_pass import MyPass

def compile(self, source: str) -> str:
    tree = ast.parse(source)
    tree = MyPass().visit(tree)  # Add your pass
    # ... rest of compilation
```

## Testing

### Test Structure

```
tests/
├── a_unit/           # Fast unit tests
├── b_integration/    # Compile + execute tests
└── c_e2e/            # Full end-to-end tests
```

### Writing Tests

**Unit test** (fast, isolated):

```python
def test_binop_addition():
    js = py2js("x = 1 + 2", include_stdlib=False)
    assert "1 + 2" in js
```

**Integration test** (compile + run):

```python
from prescrypt.testing import js_eval, js_eq

def test_addition():
    code = "result = 1 + 2"
    js = py2js(code)
    result = js_eval(js + "\nresult;")
    assert result == 3
```

**Strict mode test** (catches undeclared variables):

```python
def js_eval_strict(code):
    return js_eval('"use strict";\n' + code)

def test_for_loop_strict():
    code = "for x in [1,2,3]: pass"
    js = py2js(code)
    js_eval_strict(js)  # Throws if variables undeclared
```

### Running Tests

```bash
# All tests
make test

# Specific file
pytest tests/integration/test_expressions.py

# Specific test
pytest -k "test_for_loop"

# With coverage
pytest --cov=prescrypt
```

## Debugging the Compiler

### Print AST

```python
import ast
code = "x = [i for i in range(10)]"
tree = ast.parse(code)
print(ast.dump(tree, indent=2))
```

### Print Generated Code

```python
from prescrypt import py2js
code = "x = 1 + 2"
print(py2js(code, include_stdlib=False))
```

### Step Through Compilation

```python
from prescrypt.compiler import Compiler

compiler = Compiler()
tree = compiler.parse(source)
print("After parse:", ast.dump(tree))

tree = compiler.desugar(tree)
print("After desugar:", ast.dump(tree))

tree = compiler.bind(tree)
print("After bind:", ast.dump(tree))

js = compiler.codegen(tree)
print("Generated:", js)
```

## Code Style

- **Formatting**: Ruff with 88-char lines
- **Type hints**: Required for public functions
- **Docstrings**: Google style
- **Tests**: Required for new features

```bash
# Format
make format

# Lint
make lint

# Type check
mypy src/
```

## Common Pitfalls

### Forgetting Variable Declarations

Always use `let` for temporary variables:

```python
# Wrong - causes ReferenceError in strict mode
code.append(f"{temp_var} = {value};")

# Right
code.append(f"let {temp_var} = {value};")
```

### Not Handling All Node Types

Check what nodes your code might receive:

```python
@gen_expr.register
def gen_subscript(node: ast.Subscript, codegen: CodeGen):
    # node.slice can be Index, Slice, or ExtSlice
    # Handle all cases or raise clear error
```

### Breaking Tree-Shaking

If your stdlib function depends on another, register the dependency:

```python
# In stdlib_js.py
STDLIB_DEPS = {
    "_pyfunc_enumerate": ["_pyfunc_range"],
    # ...
}
```

## Resources

- [Python AST Documentation](https://docs.python.org/3/library/ast.html)
  - [Extra Documentation on the Python AST](https://greentreesnakes.readthedocs.org/en/latest/nodes.html)
- [ES6 Specification](https://262.ecma-international.org/)
- [Source Map V3 Spec](https://sourcemaps.info/spec.html)
