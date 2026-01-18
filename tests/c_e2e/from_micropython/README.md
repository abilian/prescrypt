# MicroPython End-to-End Tests

This directory contains end-to-end tests adapted from the MicroPython project. These tests verify that Prescrypt correctly transpiles Python programs to JavaScript that produces identical output.

## Directory Structure

```
from_micropython/
├── programs/           # Python test programs from MicroPython
├── test_all.py         # pytest test suite (used by CI)
├── check_all.py        # Diagnostic script for analyzing failures
├── update_denylist.py  # Script to check programs under CPython
├── denylist.py         # Programs excluded from testing
├── _compile_helper.py  # Helper for subprocess-based compilation
└── README.md           # This file
```

## How It Works

### Test Pipeline

1. **Compile**: Python source → JavaScript (via `py2js`)
2. **Execute JS**: Run generated JavaScript in Node.js
3. **Execute Python**: Run original Python with CPython
4. **Compare**: Assert that outputs are identical

A test passes only if the JavaScript output exactly matches the Python output.

### The Denylist

The `denylist.py` file contains programs that are excluded from testing. Programs may be denied for several reasons:

- **Compilation timeouts**: Programs that cause the compiler to hang or exhaust memory
- **Compilation errors**: Programs using unsupported Python features
- **Runtime errors**: Programs that crash when executed in Node.js
- **Output mismatches**: Programs that run but produce different output than Python

## Scripts

### test_all.py

The main pytest test suite. Used by CI and `make test`.

```bash
# Run all MicroPython tests
pytest tests/c_e2e/from_micropython/test_all.py

# Run a specific test
pytest tests/c_e2e/from_micropython/test_all.py -k "bool1"
```

### check_all.py

Comprehensive diagnostic script that analyzes all programs and categorizes failures.

```bash
# Run full analysis (shows progress and detailed failure reports)
python tests/c_e2e/from_micropython/check_all.py

# Verbose mode (shows each program as it runs)
python tests/c_e2e/from_micropython/check_all.py -v

# Filter to specific programs
python tests/c_e2e/from_micropython/check_all.py -f string

# Quiet mode (just show failures/total)
python tests/c_e2e/from_micropython/check_all.py -q

# Generate a new denylist
python tests/c_e2e/from_micropython/check_all.py --create-denylist

# Show generated JavaScript for failures
python tests/c_e2e/from_micropython/check_all.py --show-js

# Save results to JSON for analysis
python tests/c_e2e/from_micropython/check_all.py --json results.json
```

#### Failure Categories

The script categorizes failures into:

| Status | Description |
|--------|-------------|
| `compile_timeout` | Compilation hung or exhausted memory |
| `compile_error` | Compilation failed (unsupported feature) |
| `quickjs_timeout` | QuickJS execution timed out |
| `quickjs_error` | QuickJS runtime error |
| `node_timeout` | Node.js execution timed out |
| `node_error` | Node.js runtime error |
| `output_mismatch` | JS runs but output differs from Python |

### update_denylist.py

Checks which programs work under CPython (before transpilation). Useful for identifying programs that use MicroPython-specific features.

```bash
python tests/c_e2e/from_micropython/update_denylist.py
```

## Updating the Denylist

When adding new features or fixing bugs, you may want to update the denylist:

```bash
# 1. Run check_all.py to see current state
python tests/c_e2e/from_micropython/check_all.py -q

# 2. Generate new denylist
python tests/c_e2e/from_micropython/check_all.py --create-denylist > new_denylist.txt

# 3. Review and update denylist.py
# Copy the DENY_LIST from new_denylist.txt to denylist.py

# 4. Verify all tests pass
pytest tests/c_e2e/from_micropython/test_all.py
```

## Timeouts and Resource Limits

The scripts use timeouts to handle programs that hang:

- **Compilation timeout**: 5 seconds (catches infinite loops in compiler)
- **Execution timeout**: 10 seconds (catches infinite loops in generated JS)

On Linux, memory limits (512 MB) are also enforced to prevent OOM errors. On macOS, memory limits are not supported by the OS.

## Adding New Test Programs

1. Add the `.py` file to `programs/`
2. Run `check_all.py -f yourfile` to verify it works
3. If it fails, either fix the issue or add it to `denylist.py`

## Test Program Requirements

Programs should:
- Be self-contained (no imports except stdlib)
- Print output to stdout (this is compared)
- Exit normally (non-zero exit = failure)
- Complete within 10 seconds
