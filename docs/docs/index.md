# Welcome to the Prescrypt documentation

Prescrypt is a Python-to-JavaScript transpiler that converts a subset of Python 3.9+ to ES6+ JavaScript.

## Quick intro

Prescrypt transpiles Python code to JavaScript at build time. The generated code runs standalone in browsers and Node.js without additional runtime dependencies (beyond a small stdlib for Python-compatible behavior).

### What's supported

- **Core Python**: functions, classes (single inheritance), control flow, comprehensions
- **Data types**: int, float, str, bool, None, list, dict, tuple, set
- **Builtins**: print, len, range, enumerate, zip, map, filter, sorted, etc.
- **String formatting**: f-strings, %-formatting, .format()
- **ES6 modules**: imports/exports with `py2js -m`
- **JS interop**: Access browser/Node.js APIs via `import js`
- **Async/await**: Basic support for async functions

### What's NOT supported

- Generators (`yield`)
- Multiple inheritance
- Metaclasses
- `eval()`, `exec()`
- Lambda with default arguments
- Context manager protocol (`__enter__`/`__exit__`)
- Most of the Python standard library

## Goals

Prescrypt aims to:

1. Allow writing JavaScript with Python syntax for web projects
2. Generate standalone JavaScript that doesn't require a Python runtime
3. Provide a reasonable subset of Python that maps cleanly to JavaScript

## Prescrypt is just JavaScript

Unlike Brython or Skulpt which aim for full Python compatibility, Prescrypt is a transpiler—your Python becomes JavaScript. This means:

- **Fast**: No interpreter overhead, just native JS
- **Small**: Tree-shaking includes only what you use
- **Interoperable**: Easy access to JS libraries and APIs

But also:

- Not all Python features translate to JS
- Some semantic differences exist (see [Differences](../reference/differences.md))
- You may need some JavaScript knowledge for edge cases

## Pythonic behavior

Prescrypt makes JavaScript more Pythonic:

- Empty lists/dicts are falsy (unlike JS where `[]` and `{}` are truthy)
- `==` does deep comparison for objects
- `isinstance()` works correctly
- Negative indexing works (`items[-1]`)
- Most list, dict, and str methods are available

## Caveats

- JavaScript has only `number` (no int/float distinction)
- Dict keys are converted to strings
- Large integers lose precision beyond 2^53
- Accessing undefined attributes returns `undefined` (no AttributeError)
- Lambda functions don't support default arguments

## Credits

Prescrypt is a fork of [PScript](https://github.com/flexxui/pscript) with significant enhancements including ES6 modules, source maps, tree-shaking, and improved tooling.

[More credits](credits.md)
