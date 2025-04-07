import os
from mcp.server.fastmcp import FastMCP
from mcp_server_bwt.services.bing_webmaster import BingWebmasterService
from mcp_server_bwt.tools.bing_webmaster import add_bing_webmaster_tools

mcp = FastMCP("mcp-server-bwt")

# Initialize Bing Webmaster Tools service
api_key = os.getenv("BING_WEBMASTER_API_KEY")
if not api_key:
    raise ValueError("BING_WEBMASTER_API_KEY environment variable is required")

# Create the service with the API key
bing_service = BingWebmasterService(api_key=api_key)

# Add the tools to the MCP server
add_bing_webmaster_tools(mcp, bing_service)

if __name__ == "__main__":
    mcp.run(transport="stdio")
