# Node.js CLI Example

Build a command-line tool that processes files using Node.js.

## Project Structure

```
wordcount/
├── src/
│   └── wc.py
├── dist/
│   └── wc.js        # Generated
└── package.json
```

## The Code

### wc.py

```python
"""Word Count CLI - Count words, lines, and characters in files."""
import js

# Node.js modules
fs = js.require("fs")
path = js.require("path")


def count_file(filepath):
    """Count words, lines, and characters in a file."""
    try:
        content = fs.readFileSync(filepath, "utf8")
    except Exception as e:
        js.console.error(f"Error reading {filepath}: {e}")
        return None

    lines = content.split("\n")
    words = content.split()
    chars = len(content)

    return {
        "lines": len(lines),
        "words": len(words),
        "chars": chars,
        "file": filepath
    }


def format_result(result):
    """Format a count result for display."""
    return f"{result['lines']:>8} {result['words']:>8} {result['chars']:>8} {result['file']}"


def print_help():
    """Print usage information."""
    js.console.log("""
Usage: node wc.js [options] <file>...

Count words, lines, and characters in files.

Options:
  -l, --lines    Show only line counts
  -w, --words    Show only word counts
  -c, --chars    Show only character counts
  -h, --help     Show this help message

Examples:
  node wc.js file.txt
  node wc.js -l *.py
  node wc.js --words file1.txt file2.txt
""".strip())


def parse_args(argv):
    """Parse command-line arguments."""
    options = {
        "lines": False,
        "words": False,
        "chars": False,
        "help": False,
        "files": []
    }

    # Skip 'node' and script name
    args = list(argv)[2:]

    for arg in args:
        if arg in ("-h", "--help"):
            options["help"] = True
        elif arg in ("-l", "--lines"):
            options["lines"] = True
        elif arg in ("-w", "--words"):
            options["words"] = True
        elif arg in ("-c", "--chars"):
            options["chars"] = True
        elif not arg.startswith("-"):
            options["files"].append(arg)
        else:
            js.console.error(f"Unknown option: {arg}")
            js.process.exit(1)

    return options


def format_filtered(result, options):
    """Format result with only selected columns."""
    parts = []
    if options["lines"]:
        parts.append(f"{result['lines']:>8}")
    if options["words"]:
        parts.append(f"{result['words']:>8}")
    if options["chars"]:
        parts.append(f"{result['chars']:>8}")
    parts.append(result["file"])
    return " ".join(parts)


def main():
    """Main entry point."""
    options = parse_args(js.process.argv)

    if options["help"]:
        print_help()
        return

    if not options["files"]:
        js.console.error("Error: No files specified")
        js.console.error("Use --help for usage information")
        js.process.exit(1)

    # If no specific options, show all
    show_all = not (options["lines"] or options["words"] or options["chars"])

    results = []
    totals = {"lines": 0, "words": 0, "chars": 0}

    for filepath in options["files"]:
        result = count_file(filepath)
        if result:
            results.append(result)
            totals["lines"] += result["lines"]
            totals["words"] += result["words"]
            totals["chars"] += result["chars"]

    if not results:
        js.process.exit(1)

    # Print results
    for result in results:
        if show_all:
            js.console.log(format_result(result))
        else:
            js.console.log(format_filtered(result, options))

    # Print totals if multiple files
    if len(results) > 1:
        totals["file"] = "total"
        if show_all:
            js.console.log(format_result(totals))
        else:
            js.console.log(format_filtered(totals, options))


# Run main
main()
```

### package.json

```json
{
  "name": "wordcount",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "wc": "./dist/wc.js"
  }
}
```

## Compile and Run

```bash
# Create project
mkdir -p wordcount/src wordcount/dist
cd wordcount

# Copy wc.py to src/
# Create package.json

# Compile
py2js src/wc.py -m -o dist/wc.js

# Run
node dist/wc.js --help
node dist/wc.js src/wc.py
node dist/wc.js -l *.js
```

## Making It Executable

Add a shebang and make it executable:

```bash
# Add shebang to generated file
echo '#!/usr/bin/env node' | cat - dist/wc.js > dist/wc.tmp && mv dist/wc.tmp dist/wc.js

# Make executable
chmod +x dist/wc.js

# Run directly
./dist/wc.js file.txt
```

Or install globally:

```bash
npm link
wc --help
```

## Key Patterns

### Node.js Modules

```python
import js

# CommonJS require
fs = js.require("fs")
path = js.require("path")
os = js.require("os")

# Use module
content = fs.readFileSync("file.txt", "utf8")
home = os.homedir()
```

### Process and Arguments

```python
import js

# Command-line arguments
args = list(js.process.argv)
# args[0] = 'node'
# args[1] = script path
# args[2:] = user arguments

# Environment variables
api_key = js.process.env.API_KEY or "default"

# Exit codes
js.process.exit(0)  # Success
js.process.exit(1)  # Error

# Current directory
cwd = js.process.cwd()
```

### File System Operations

```python
import js
fs = js.require("fs")

# Read file
content = fs.readFileSync("file.txt", "utf8")

# Write file
fs.writeFileSync("output.txt", content)

# Check if file exists
exists = fs.existsSync("file.txt")

# Read directory
files = fs.readdirSync(".")

# File stats
stats = fs.statSync("file.txt")
is_dir = stats.isDirectory()
size = stats.size
```

### Path Operations

```python
import js
path = js.require("path")

# Join paths
full = path.join("/home", "user", "file.txt")

# Parse path
parsed = path.parse("/home/user/file.txt")
# parsed.dir = "/home/user"
# parsed.base = "file.txt"
# parsed.ext = ".txt"
# parsed.name = "file"

# Resolve relative path
absolute = path.resolve("../file.txt")
```

### Error Handling

```python
import js

def safe_read(filepath):
    try:
        return js.require("fs").readFileSync(filepath, "utf8")
    except Exception as e:
        js.console.error(f"Error: {e}")
        return None
```

## Async File Operations

For better performance with many files:

```python
import js

fs = js.require("fs").promises
path = js.require("path")


async def process_files(filepaths):
    """Process multiple files concurrently."""
    promises = [process_file(fp) for fp in filepaths]
    results = await js.Promise.all(promises)
    return results


async def process_file(filepath):
    """Process a single file."""
    content = await fs.readFile(filepath, "utf8")
    # ... process content
    return result


async def main():
    files = list(js.process.argv)[2:]
    results = await process_files(files)
    for r in results:
        js.console.log(r)


main()
```

## See Also

- [JavaScript Interop](../guide/js-interop.md) - Node.js API reference
- [Multi-file Project](multi-file.md) - Larger project structure
- [Browser App](browser-app.md) - Client-side example
