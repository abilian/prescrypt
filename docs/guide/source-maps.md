# Source Maps

Source maps let you debug your Python code in browser DevTools, even though the browser runs JavaScript.

## What Are Source Maps?

A source map is a JSON file that maps positions in generated JavaScript back to the original Python source. With source maps:

- Set breakpoints in Python code
- See Python filenames and line numbers in stack traces
- Step through Python code in the debugger

## Enabling Source Maps

Add `-s` or `--source-maps` to generate `.js.map` files:

```bash
# Single file
py2js app.py -s
# Output: app.js, app.js.map

# Directory
py2js src/ -o dist/ -s
# Output: dist/*.js, dist/*.js.map
```

## How It Works

### Generated Files

For each `.js` file, a corresponding `.js.map` is created:

```
src/
└── app.py

dist/
├── app.js
└── app.js.map
```

### Source Map Reference

The generated JavaScript includes a reference to its source map:

```javascript
// ... generated code ...
//# sourceMappingURL=app.js.map
```

Browsers automatically load this file when DevTools are open.

### Map Contents

The `.js.map` file contains:

```json
{
  "version": 3,
  "file": "app.js",
  "sources": ["../src/app.py"],
  "sourcesContent": ["def main():\n    print('Hello')\n..."],
  "names": [],
  "mappings": "AAAA,SAAS,IAAI..."
}
```

- **sources**: Path to original Python file(s)
- **sourcesContent**: Embedded Python source (for standalone debugging)
- **mappings**: VLQ-encoded position mappings

## Browser Debugging

### Chrome DevTools

1. Open DevTools (F12 or Cmd+Option+I)
2. Go to **Sources** panel
3. In the file tree, find your `.py` file under the page's sources
4. Set breakpoints by clicking line numbers
5. Refresh the page to hit breakpoints

![Chrome DevTools with Python source](../assets/devtools-python.png)

### Firefox Developer Tools

1. Open Developer Tools (F12)
2. Go to **Debugger** panel
3. Find your Python source in the Sources pane
4. Click line numbers to set breakpoints

### Safari Web Inspector

1. Open Web Inspector (Cmd+Option+I)
2. Go to **Sources** tab
3. Locate Python files in the Resources sidebar

## Node.js Debugging

### VS Code

1. Add a launch configuration in `.vscode/launch.json`:

```json
{
  "type": "node",
  "request": "launch",
  "name": "Debug Prescrypt",
  "program": "${workspaceFolder}/dist/main.js",
  "sourceMaps": true,
  "sourceMapPathOverrides": {
    "../src/*": "${workspaceFolder}/src/*"
  }
}
```

2. Set breakpoints in your Python files
3. Press F5 to start debugging

### Command Line

```bash
node --inspect dist/main.js
```

Then open `chrome://inspect` in Chrome to connect.

## Mapping Accuracy

Source maps map **statement-level** positions:

| What's Mapped | Accuracy |
|--------------|----------|
| Function definitions | Exact line |
| Variable assignments | Exact line |
| Control flow (if/for/while) | Exact line |
| Expressions within statements | Statement line |

!!! note "Statement-Level Mapping"
    Prescrypt maps at the statement level, not expression level. Complex expressions on a single line will map to that line, but you can't set breakpoints within the expression.

## Stack Traces

With source maps, error stack traces show Python filenames and lines:

**Without source maps:**
```
Error: Something went wrong
    at process (app.js:42:15)
    at main (app.js:58:5)
```

**With source maps (in DevTools):**
```
Error: Something went wrong
    at process (app.py:23:5)
    at main (app.py:31:1)
```

## Production Considerations

### Performance

Source maps don't affect runtime performance—they're only loaded when DevTools are open.

### File Size

Source maps can be large (often larger than the JS). Consider:

- **Development**: Always use source maps
- **Production**: Generate but don't deploy to public servers

### Hosting Source Maps

Options for production debugging:

1. **Don't deploy**: Keep maps on build server only
2. **Separate server**: Host maps on internal server
3. **DevTools override**: Use DevTools' "Add source map" feature

```javascript
// Reference internal source map server
//# sourceMappingURL=https://internal.example.com/maps/app.js.map
```

## Troubleshooting

### Source Map Not Loading

**Symptoms:** DevTools shows JavaScript, not Python

**Solutions:**
1. Check that `.js.map` file exists alongside `.js`
2. Verify the `sourceMappingURL` comment is at the end of the JS file
3. Ensure the map file is accessible (check network panel)
4. Clear browser cache and reload

### Wrong Line Numbers

**Symptoms:** Breakpoints hit on unexpected lines

**Solutions:**
1. Rebuild with fresh source maps
2. Check that source files haven't been modified since compilation
3. Verify no other tools are modifying the JS output

### Source Content Not Showing

**Symptoms:** DevTools shows "Source not available"

**Solutions:**
1. Prescrypt embeds source content—check the `sourcesContent` field in the map
2. Ensure the original `.py` file path is correct in `sources`

## See Also

- [CLI Reference](cli.md) - Source map options
- [Debugging Guide](../examples/browser-app.md#debugging) - Debugging workflow
