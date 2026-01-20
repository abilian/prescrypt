# Browser Extension Demo

Write Chrome/Firefox extensions in Python.

## Use Case

Python developers can create browser extensions without learning JavaScript.
The extension logic is written in Python and compiled to JS by Prescrypt.

## Features

This demo extension analyzes web pages:

- **Price Highlighting**: Marks items over $100 with yellow background
- **Reading Time**: Estimates time to read based on word count
- **Link Analysis**: Counts internal vs external links
- **Text Statistics**: Paragraphs, headings, sentences, characters

## Project Structure

```
browser-extension/
├── manifest.json       # Extension manifest (Chrome/Firefox)
├── popup.html          # Extension popup UI
├── src/
│   └── content.py      # Python content script
├── dist/
│   └── content.js      # Compiled JavaScript
├── icons/              # Extension icons
└── test-page.html      # Test page with sample content
```

## Build

```bash
make build   # Compile Python to JavaScript
```

## Install in Browser

### Chrome

1. Go to `chrome://extensions`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select this directory

### Firefox

1. Go to `about:debugging`
2. Click "This Firefox"
3. Click "Load Temporary Add-on"
4. Select `manifest.json`

## Test

```bash
make test   # Opens test page in browser
```

Or manually open `test-page.html` with the extension loaded.

## Python Highlights

```python
def parse_price(text: str) -> float:
    """Extract numeric price from '$99.99' or '€199,00'."""
    # Handle both US and European formats
    ...

def highlight_prices():
    """Find and highlight prices above threshold."""
    for el in js.document.querySelectorAll(".price"):
        price = parse_price(el.textContent)
        if price > Config.price_threshold:
            el.style.backgroundColor = "#fef3c7"
            el.style.border = "2px solid #f59e0b"
```

## Why Prescrypt?

- Write extension logic in familiar Python syntax
- No need to learn JavaScript/TypeScript
- Same analysis code can run on backend
- Tiny output (content script ~15 KB)

## Production Enhancements

- Add options page for configuration
- Persist settings with `chrome.storage`
- Add keyboard shortcuts
- Inject CSS instead of inline styles
- Add i18n support
