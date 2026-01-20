"""Browser Extension Content Script

A content script that runs on web pages and enhances them.
Demonstrates writing browser extension logic in Python.

Features:
- Price highlighting (marks expensive items)
- Reading time estimation
- Link analysis
- Text statistics
"""
import js


# ============================================================================
# Configuration
# ============================================================================

class Config:
    """Extension configuration."""
    price_threshold = 100.0
    reading_speed = 200


# ============================================================================
# Price Highlighting
# ============================================================================

def parse_price(text: str) -> float:
    """Extract numeric price from text like '$99.99'."""
    cleaned = text.strip()

    for symbol in ["$", "USD"]:
        cleaned = cleaned.replace(symbol, "")

    cleaned = cleaned.strip()

    if "," in cleaned:
        cleaned = cleaned.replace(",", "")

    try:
        return float(cleaned)
    except ValueError:
        return -1.0


def highlight_prices() -> int:
    """Find and highlight prices above threshold."""
    highlighted = 0

    elements = js.document.querySelectorAll(".price")
    for el in elements:
        text = el.textContent
        price = parse_price(text)

        if price > Config.price_threshold:
            if "prescrypt-highlighted" not in el.className:
                el.className += " prescrypt-highlighted"
                el.style.backgroundColor = "#fef3c7"
                el.style.border = "2px solid #f59e0b"
                el.style.borderRadius = "4px"
                el.style.padding = "2px 6px"
                highlighted += 1

    return highlighted


# ============================================================================
# Reading Time Estimation
# ============================================================================

def count_words(text: str) -> int:
    """Count words in text."""
    words = text.split()
    return len(words)


def estimate_reading_time() -> dict:
    """Estimate reading time for the page."""
    main_content = js.document.querySelector("article")
    if not main_content:
        main_content = js.document.querySelector("main")
    if not main_content:
        main_content = js.document.body

    text = main_content.textContent or ""
    words = count_words(text)
    minutes = words / Config.reading_speed

    return {
        "words": words,
        "minutes": round(minutes, 1),
    }


# ============================================================================
# Link Analysis
# ============================================================================

def analyze_links() -> dict:
    """Analyze links on the page."""
    links = js.document.querySelectorAll("a[href]")
    current_host = js.window.location.hostname

    total = 0
    external = 0
    internal = 0

    for link in links:
        href = link.href
        total += 1

        if current_host in href:
            internal += 1
        else:
            external += 1

    return {
        "total": total,
        "external": external,
        "internal": internal,
    }


# ============================================================================
# Text Statistics
# ============================================================================

def get_text_stats() -> dict:
    """Get statistics about text on the page."""
    text = js.document.body.textContent or ""

    chars = len(text)
    words = count_words(text)
    sentences = text.count(".") + text.count("!") + text.count("?")
    paragraphs = len(js.document.querySelectorAll("p"))
    headings = len(js.document.querySelectorAll("h1, h2, h3, h4, h5, h6"))

    return {
        "characters": chars,
        "words": words,
        "sentences": sentences,
        "paragraphs": paragraphs,
        "headings": headings,
    }


# ============================================================================
# UI Overlay
# ============================================================================

def create_info_panel():
    """Create the info panel overlay."""
    if js.document.getElementById("prescrypt-panel"):
        return

    panel = js.document.createElement("div")
    panel.id = "prescrypt-panel"

    # Create header
    header = js.document.createElement("div")
    header.className = "prescrypt-header"
    header.textContent = "Page Analyzer"

    # Create content area
    content = js.document.createElement("div")
    content.className = "prescrypt-content"
    content.id = "prescrypt-content"
    content.textContent = "Analyzing..."

    panel.appendChild(header)
    panel.appendChild(content)

    # Apply styles
    panel.style.position = "fixed"
    panel.style.top = "20px"
    panel.style.right = "20px"
    panel.style.width = "280px"
    panel.style.background = "#1e293b"
    panel.style.borderRadius = "12px"
    panel.style.boxShadow = "0 10px 40px rgba(0,0,0,0.3)"
    panel.style.fontFamily = "system-ui, sans-serif"
    panel.style.fontSize = "14px"
    panel.style.color = "#e2e8f0"
    panel.style.zIndex = "999999"
    panel.style.overflow = "hidden"

    header.style.padding = "12px 15px"
    header.style.background = "#6366f1"
    header.style.fontWeight = "600"

    content.style.padding = "15px"

    js.document.body.appendChild(panel)


def update_panel(data: dict):
    """Update the panel with analysis results."""
    content = js.document.getElementById("prescrypt-content")
    if not content:
        return

    rt = data["reading_time"]
    links = data["links"]
    stats = data["stats"]
    prices = data["prices_highlighted"]

    # Build content
    lines = []
    lines.append("Reading Time: " + str(rt["minutes"]) + " min")
    lines.append("Words: " + str(rt["words"]))
    lines.append("")
    lines.append("Prices highlighted: " + str(prices))
    lines.append("")
    lines.append("Links: " + str(links["internal"]) + " internal, " + str(links["external"]) + " external")
    lines.append("")
    lines.append("Paragraphs: " + str(stats["paragraphs"]))
    lines.append("Headings: " + str(stats["headings"]))

    # Clear and rebuild content
    content.innerHTML = ""
    for line in lines:
        p = js.document.createElement("div")
        p.textContent = line
        p.style.marginBottom = "5px"
        if line == "":
            p.style.height = "10px"
        content.appendChild(p)


# ============================================================================
# Main Entry Point
# ============================================================================

def analyze_page():
    """Run all analyses and show results."""
    create_info_panel()

    prices_highlighted = highlight_prices()
    reading_time = estimate_reading_time()
    links = analyze_links()
    stats = get_text_stats()

    update_panel({
        "prices_highlighted": prices_highlighted,
        "reading_time": reading_time,
        "links": links,
        "stats": stats,
    })


def on_load(e):
    """Handle page load event."""
    analyze_page()


def init():
    """Initialize the content script."""
    if js.document.readyState == "complete":
        analyze_page()
    else:
        js.window.addEventListener("load", on_load)


# Initialize
init()
