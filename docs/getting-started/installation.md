# Installation

Prescrypt can be installed using pip, pipx, or from source for development.

## Requirements

- Python 3.9 or higher
- Node.js 16+ (for running generated JavaScript)

## Quick Install

### Using pip

```bash
pip install prescrypt
```

### Using pipx (Recommended for CLI)

[pipx](https://pypa.github.io/pipx/) installs Python applications in isolated environments:

```bash
pipx install prescrypt
```

This makes the `py2js` command available globally without affecting your project dependencies.

### Using uv

```bash
uv pip install prescrypt
```

Or add to your project:

```bash
uv add prescrypt
```

## Verify Installation

After installation, verify it works:

```bash
py2js --help
```

You should see:

```
usage: py2js [-h] [-o OUTPUT] [-m] [-M MODULE_PATHS] [--no-stdlib]
             [--no-tree-shake] [--no-optimize] [-s] [-v] [-q]
             input

Compile Python to JavaScript

positional arguments:
  input                 Input Python file or directory
...
```

## Development Installation

To contribute to Prescrypt or run the latest development version:

### Clone the Repository

```bash
git clone https://git.sr.ht/~sfermigier/prescrypt.git
cd prescrypt
```

### Install with Poetry

```bash
uv sync
```

### Run from Source

```bash
uv run py2js --help
```

### Run Tests

```bash
uv run pytest
```

Or use make:

```bash
make test
```

## Optional: Node.js Setup

To run the generated JavaScript, you need Node.js:

=== "macOS"

    ```bash
    brew install node
    ```

=== "Ubuntu/Debian"

    ```bash
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
    ```

=== "Windows"

    Download from [nodejs.org](https://nodejs.org/) or use winget:

    ```powershell
    winget install OpenJS.NodeJS.LTS
    ```

### Enable ES6 Modules in Node.js

For ES6 module support, either:

1. Add `"type": "module"` to your `package.json`:

    ```json
    {
      "type": "module"
    }
    ```

2. Or use the `.mjs` extension for your JavaScript files.

## Next Steps

Now that Prescrypt is installed, try the [Quick Start](quickstart.md) guide to compile your first Python program.
