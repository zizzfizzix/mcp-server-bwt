"""Compatibility shim for the `mcp` Python SDK's FastMCP server class.

mcp>=2.0.0 removed `mcp.server.fastmcp.FastMCP` and replaced it with
`mcp.server.mcpserver.MCPServer`, which exposes the same `.tool()` decorator
and `.run(transport=...)` API used throughout this package. Import from here
instead of `mcp.server.fastmcp` so the package works with both the 1.x and
2.x SDK lines.
"""

try:
    # mcp < 2.0.0
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # mcp >= 2.0.0: FastMCP was renamed to MCPServer and moved.
    from mcp.server.mcpserver import MCPServer as FastMCP

__all__ = ["FastMCP"]
