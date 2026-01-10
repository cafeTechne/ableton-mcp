"""
MCPO Proxy Starter
Connects to the MCP SSE server and exposes OpenAPI endpoints
"""
import sys
from mcpo import app

if __name__ == "__main__":
    sys.argv = ['mcpo', '--port', '8001', '--server-type', 'sse', '--', 'http://localhost:8000/sse']
    app()
