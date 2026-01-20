# Edge Worker Demo - Cloudflare Workers in Python

Write edge computing logic in Python, deploy to Cloudflare's global network.

## Use Case

Edge workers run JavaScript on Cloudflare's 300+ data centers worldwide.
With Prescrypt, you can write that logic in Python:

- **Request filtering**: Bot detection, geo-blocking
- **A/B testing**: Consistent variant assignment
- **Response transformation**: Inject headers, modify HTML
- **Rate limiting**: Protect your origin
- **Caching strategies**: Custom cache keys, stale-while-revalidate

## Features Demonstrated

```python
# Bot detection
def is_bot(user_agent: str) -> bool:
    ua_lower = user_agent.lower()
    for pattern in ["bot", "crawler", "spider"]:
        if pattern in ua_lower:
            return True
    return False

# A/B test assignment
def get_ab_variant(client_ip: str) -> str:
    h = hash_string(client_ip)
    # Deterministic assignment based on IP hash
    ...

# Security headers
def add_security_headers(response):
    headers.set("X-Content-Type-Options", "nosniff")
    headers.set("X-Frame-Options", "DENY")
    ...
```

## Build

```bash
make build   # Compile Python to JavaScript
```

## Test Locally

Using [Miniflare](https://miniflare.dev/) (Cloudflare Workers simulator):

```bash
npm install -g miniflare
make build
miniflare dist/worker.js
```

Or with Wrangler:

```bash
npm install -g wrangler
wrangler dev dist/worker.js
```

## Deploy to Cloudflare

1. Sign up at [Cloudflare Workers](https://workers.cloudflare.com/)
2. Configure `wrangler.toml` with your account
3. Run:

```bash
wrangler login
wrangler deploy
```

## Why Prescrypt for Edge?

| Metric | Prescrypt | Pyodide |
|--------|-----------|---------|
| Bundle size | ~20 KB | 10+ MB |
| Cold start | <5 ms | N/A (too large) |
| Memory | ~10 MB | 128+ MB |

Cloudflare Workers have strict limits (1 MB bundle, 128 MB memory).
Prescrypt fits easily; Pyodide does not.

## Production Enhancements

For production use, consider:

- **KV Storage**: For rate limit counters, session data
- **Durable Objects**: For stateful edge logic
- **Workers Analytics**: Track request patterns
- **Custom domains**: Route specific paths to your worker
