# Contributing

Thank you for your interest in contributing to Prescrypt!

## Development Setup

### Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) for dependency management
- Node.js 16+ (for running tests)
- [QuickJS](https://bellard.org/quickjs/) (optional, for faster test execution)

### Clone and Install

```bash
git clone https://git.sr.ht/~sfermigier/prescrypt.git
cd prescrypt

# Install dependencies
uv sync

# Install pre-commit hooks
poetry run pre-commit install
```

### Verify Installation

```bash
# Run tests
make test

# Run the CLI
uv run py2js --help
```

## Development Workflow

### Running Tests

```bash
# Run all tests
make test

# Run tests matching a pattern
uv run pytest -k "test_class"

# Run with verbose output
uv run pytest -v
```

### Code Quality

```bash
# Lint and typecheck code
make check

# Format code
make format

```

### Building

```bash
# Regenerate stdlib JavaScript
make build

# Build documentation
poetry run mkdocs build

# Serve documentation locally
poetry run mkdocs serve
```

## Project Structure

```
prescrypt/
├── src/prescrypt/
│   ├── main.py              # CLI entry point
│   ├── compiler.py          # Main compiler class
│   ├── front/               # Frontend: parsing, analysis
│   │   ├── ast/             # AST utilities
│   │   └── passes/          # Compiler passes
│   ├── codegen/             # Backend: code generation
│   │   ├── _expressions/    # Expression handlers
│   │   ├── _statements/     # Statement handlers
│   │   └── stdlib_py/       # Python stdlib implementations
│   └── stdlibjs/            # JavaScript runtime
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── from_micropython/    # E2E tests
└── docs/                    # Documentation
```

## Code Style

### General Guidelines

- Follow PEP 8 with 88-character line length (Black style)
- Use type hints for all public functions
- Write docstrings in Google style
- Keep functions focused and small

### Code Generation Pattern

Code generation uses `@singledispatch` for routing:

```python
from functools import singledispatch
from prescrypt.codegen.main import gen_expr

@gen_expr.register
def gen_my_node(node: ast.MyNode, codegen: CodeGen) -> str:
    """Generate JavaScript for MyNode."""
    # Implementation here
    return "generated_js"
```

### Testing Pattern

Tests compile Python to JavaScript and verify the output:

```python
def test_feature():
    """Test description."""
    src = """
    x = 1 + 2
    print(x)
    """
    result = compile_and_run(src)
    assert result.stdout == "3\n"
```

## Pull Request Process

### Before Submitting

1. **Run tests:** `make test`
2. **Run linting:** `make lint`
3. **Format code:** `make format`
4. **Update documentation** if adding features

### PR Guidelines

- Create a feature branch from `main`
- Write clear commit messages
- Add tests for new functionality
- Update relevant documentation
- Keep PRs focused—one feature or fix per PR

### Commit Message Format

```
type: short description

Longer description if needed.

Fixes #123
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

## Adding Features

### New Python Construct

1. Add handler in appropriate `_expressions/` or `_statements/` module
2. Register with `@gen_expr.register` or `@gen_stmt.register`
3. Add integration test in `tests/integration/`
4. Update documentation

### New Stdlib Function

1. Add Python implementation in `codegen/stdlib_py/`
2. Or add JavaScript implementation in `stdlibjs/`
3. Add to tree-shaking dependency graph if needed
4. Add tests

### New CLI Option

1. Add argument in `main.py`
2. Thread option through to compiler
3. Add CLI test
4. Update documentation

## Reporting Issues

### Bug Reports

Include:
- Python code that fails
- Expected behavior
- Actual behavior (error message or wrong output)
- Prescrypt version (`py2js --version`)

### Feature Requests

Describe:
- The Python feature you want supported
- Use case (why you need it)
- Example code

## Getting Help

- Open an issue for questions
- Check existing issues for similar problems
- Read the documentation first

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
