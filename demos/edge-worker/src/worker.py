"""Edge Worker - Cloudflare Workers in Python

Write edge computing logic in Python, deploy as JavaScript.
This worker demonstrates common edge computing patterns:

- Request filtering (bot detection, geo-blocking)
- Request/response transformation
- A/B testing
- Rate limiting
- Caching strategies
"""
from __future__ import annotations

import js

# ============================================================================
# Configuration
# ============================================================================

# Blocked countries (ISO codes)
BLOCKED_COUNTRIES = ["XX", "YY"]  # Example placeholder codes

# Bot user agent patterns
BOT_PATTERNS = [
    "bot",
    "crawler",
    "spider",
    "scraper",
    "curl",
    "wget",
    "python-requests",
]

# Rate limit: requests per minute per IP
RATE_LIMIT = 60

# A/B test configuration
AB_TEST_VARIANTS = {
    "control": 0.5,      # 50% get control
    "variant_a": 0.3,    # 30% get variant A
    "variant_b": 0.2,    # 20% get variant B
}


# ============================================================================
# Utilities
# ============================================================================

def is_bot(user_agent: str) -> bool:
    """Check if the request appears to be from a bot."""
    if not user_agent:
        return True  # No user agent is suspicious

    ua_lower = user_agent.lower()
    for pattern in BOT_PATTERNS:
        if pattern in ua_lower:
            return True
    return False


def get_country(request) -> str:
    """Get country code from Cloudflare headers."""
    # Cloudflare adds CF-IPCountry header
    return request.headers.get("CF-IPCountry", "XX")


def get_client_ip(request) -> str:
    """Get client IP from Cloudflare headers."""
    return request.headers.get("CF-Connecting-IP", "0.0.0.0")


def hash_string(s: str) -> int:
    """Simple hash function for A/B testing."""
    h = 0
    for c in s:
        h = (h * 31 + ord(c)) % (2**32)
    return h


def get_ab_variant(identifier: str) -> str:
    """Determine A/B test variant for an identifier (e.g., IP or cookie)."""
    h = hash_string(identifier)
    value = (h % 1000) / 1000.0  # 0.0 to 1.0

    cumulative = 0.0
    for variant in AB_TEST_VARIANTS:
        probability = AB_TEST_VARIANTS[variant]
        cumulative += probability
        if value < cumulative:
            return variant
    return "control"


# ============================================================================
# Request Handlers
# ============================================================================

def handle_blocked(reason: str):
    """Return a blocked response."""
    return js.Response.new(
        f"Access Denied: {reason}",
        {
            "status": 403,
            "headers": {"Content-Type": "text/plain"}
        }
    )


def handle_rate_limited():
    """Return a rate limited response."""
    return js.Response.new(
        "Rate limit exceeded. Please try again later.",
        {
            "status": 429,
            "headers": {
                "Content-Type": "text/plain",
                "Retry-After": "60"
            }
        }
    )


def add_security_headers(response):
    """Add security headers to response."""
    headers = js.Headers.new(response.headers)

    # Security headers
    headers.set("X-Content-Type-Options", "nosniff")
    headers.set("X-Frame-Options", "DENY")
    headers.set("X-XSS-Protection", "1; mode=block")
    headers.set("Referrer-Policy", "strict-origin-when-cross-origin")

    # Custom header to show this was processed by edge
    headers.set("X-Edge-Processed", "true")

    return js.Response.new(response.body, {
        "status": response.status,
        "statusText": response.statusText,
        "headers": headers
    })


def transform_html(html: str, variant: str) -> str:
    """Transform HTML for A/B testing."""
    # Inject A/B test variant as data attribute
    if "<body" in html:
        html = html.replace("<body", f'<body data-variant="{variant}"')

    # Add variant-specific banner
    banner = f"""
    <div style="background: #4f46e5; color: white; padding: 10px; text-align: center;">
        Edge Worker Demo - Variant: {variant.upper()}
    </div>
    """
    if "<body>" in html:
        html = html.replace("<body>", f"<body>{banner}")

    return html


# ============================================================================
# Main Handler
# ============================================================================

async def handle_request(request):
    """
    Main request handler for the edge worker.

    Flow:
    1. Bot detection
    2. Geo-blocking
    3. Rate limiting
    4. A/B test assignment
    5. Fetch from origin
    6. Response transformation
    """
    url = js.URL.new(request.url)
    user_agent = request.headers.get("User-Agent", "")
    client_ip = get_client_ip(request)
    country = get_country(request)

    # --- Step 1: Bot Detection ---
    if is_bot(user_agent):
        # For demo, we'll allow but log
        print(f"[EDGE] Bot detected: {user_agent[:50]}")
        # In production: return handle_blocked("Bot detected")

    # --- Step 2: Geo-blocking ---
    if country in BLOCKED_COUNTRIES:
        return handle_blocked(f"Country {country} is not allowed")

    # --- Step 3: Rate Limiting ---
    # In production, use Cloudflare KV or Durable Objects for state
    # For demo, we just log
    print(f"[EDGE] Request from {client_ip} ({country})")

    # --- Step 4: A/B Test Assignment ---
    variant = get_ab_variant(client_ip)
    print(f"[EDGE] A/B variant: {variant}")

    # --- Step 5: Fetch from Origin ---
    # For this demo, we'll return a synthetic response
    # In production: response = await js.fetch(request)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Edge Worker Demo</title>
    <style>
        body {{
            font-family: system-ui, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f8fafc;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #4f46e5; }}
        .info {{ color: #64748b; margin: 10px 0; }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
        }}
        .badge.variant {{ background: #ddd6fe; color: #5b21b6; }}
        .badge.country {{ background: #fef3c7; color: #92400e; }}
        code {{
            background: #f1f5f9;
            padding: 2px 6px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1>🌐 Edge Worker Response</h1>
        <p>This response was generated by a Cloudflare Worker written in Python!</p>

        <div class="info">
            <strong>Your Info:</strong><br>
            IP: <code>{client_ip}</code><br>
            Country: <span class="badge country">{country}</span><br>
            A/B Variant: <span class="badge variant">{variant}</span>
        </div>

        <div class="info">
            <strong>Request Path:</strong> <code>{url.pathname}</code>
        </div>

        <div class="info">
            <strong>User Agent:</strong><br>
            <code style="font-size: 12px;">{user_agent[:100]}...</code>
        </div>

        <hr style="margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;">

        <p style="color: #64748b; font-size: 14px;">
            The Python code running this worker was compiled to JavaScript by
            <a href="https://github.com/user/prescrypt" style="color: #4f46e5;">Prescrypt</a>.
            Edge workers run on Cloudflare's global network with sub-millisecond cold starts.
        </p>
    </div>
</body>
</html>
"""

    # --- Step 6: Transform Response ---
    transformed = transform_html(html_content, variant)

    response = js.Response.new(transformed, {
        "status": 200,
        "headers": {"Content-Type": "text/html"}
    })

    # Add security headers
    response = add_security_headers(response)

    return response


# ============================================================================
# Worker Entry Point
# ============================================================================

def handle_fetch(event):
    """Fetch event handler - Cloudflare Worker entry point."""
    event.respondWith(handle_request(event.request))


# Register the fetch handler
# In Cloudflare Workers: addEventListener('fetch', handleFetch)
js.self_.addEventListener("fetch", handle_fetch)
