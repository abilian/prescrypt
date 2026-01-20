"""Simple compile server for the Python Playground.

Receives Python code via POST and returns compiled JavaScript.
"""
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

from prescrypt.compiler import Compiler


class PlaygroundHandler(SimpleHTTPRequestHandler):
    """Handler that serves static files and handles /compile endpoint."""

    def do_POST(self):
        """Handle POST requests to /compile."""
        path = urlparse(self.path).path

        if path == "/compile":
            self.handle_compile()
        else:
            self.send_error(404, "Not Found")

    def handle_compile(self):
        """Compile Python code to JavaScript."""
        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        try:
            data = json.loads(body)
            python_code = data.get("code", "")

            # Compile to JavaScript
            compiler = Compiler()
            js_code = compiler.compile(
                python_code,
                include_stdlib=True,
                tree_shake=True,
            )

            # Send success response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            response = json.dumps({"success": True, "js": js_code})
            self.wfile.write(response.encode("utf-8"))

        except Exception as e:
            # Send error response
            self.send_response(200)  # Use 200 so JS can read the error
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            response = json.dumps({"success": False, "error": str(e)})
            self.wfile.write(response.encode("utf-8"))

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def end_headers(self):
        """Add CORS headers to all responses."""
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


def main():
    port = 8000
    server = HTTPServer(("", port), PlaygroundHandler)
    print(f"Python Playground server running at http://localhost:{port}")
    print("Press Ctrl+C to stop")
    server.serve_forever()


if __name__ == "__main__":
    main()
