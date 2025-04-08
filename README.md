# mcp-server-bwt

> MCP server for Bing Webmaster Tools

This MCP ([Model Context Protocol](https://modelcontextprotocol.io/introduction)) server provides a bridge between [supported AI assistants](https://modelcontextprotocol.io/clients) like Claude or Cursor and the Bing Webmaster Tools API. It exposes all Bing Webmaster Tools functionality available via [`bing-webmaster-tools`](https://github.com/merj/bing-webmaster-tools) as MCP tools that can be used by AI assistants to interact with your Bing Webmaster Tools account.

## Example Usage with Claude

Once configured, you can use the MCP server with Claude to interact with your Bing Webmaster Tools account. Here are some example prompts:

- "List all my verified sites in Bing Webmaster Tools"
- "Submit my homepage for indexing"
- "Get traffic statistics for my website"
- "Check for any crawling issues on my site"
- "Get keyword statistics for 'my product'"

Claude will use the appropriate MCP tools to fulfill your requests.

## Requirements

- [Python](https://www.python.org) >= 3.13
- [Nodejs](https://nodejs.org)
- [Bing Webmaster Tools API Key](https://learn.microsoft.com/en-us/bingwebmaster/getting-access#using-api-key)

## Installation

To install project dependencies, run the following command:
```bash
make install
```

### MCP Client Configuration Example (Claude, Cursor, etc.)

For Claude or other MCP clients, you can [configure the server in your settings](https://modelcontextprotocol.io/quickstart/user):

```json
{
  "mcpServers": {
    "bwtServer": {
      "command": "/PATH/TO/mcp-server-bwt/.venv/bin/python",
      "args": ["/PATH/TO/mcp-server-bwt/mcp_server_bwt/main.py"],
      "env": {
        "BING_WEBMASTER_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

## Available Tools

The server provides the following Bing Webmaster Tools API functionality (more info in the [API docs](https://learn.microsoft.com/en-us/dotnet/api/microsoft.bing.webmaster.api.interfaces?view=bing-webmaster-dotnet)):

### Site Management
- `get_sites`: List all verified sites in your Bing Webmaster Tools account
- `add_site`: Add a new site to your account
- `verify_site`: Verify ownership of a site
- `remove_site`: Remove a site from your account
- `get_site_roles`: Get roles for a specific site
- `add_site_roles`: Add roles to a site
- `remove_site_role`: Remove a role from a site
- `get_site_moves`: Get information about site moves
- `submit_site_move`: Submit a site move request

### URL Submission
- `submit_url`: Submit a single URL for indexing
- `submit_url_batch`: Submit multiple URLs for indexing in a batch
- `submit_content`: Submit content for indexing
- `submit_feed`: Submit a feed for indexing
- `get_feeds`: Get all submitted feeds
- `get_feed_details`: Get details about a specific feed
- `remove_feed`: Remove a feed from your account
- `get_url_submission_quota`: Check your URL submission quota
- `get_content_submission_quota`: Check your content submission quota
- `fetch_url`: Fetch a URL for indexing
- `get_fetched_urls`: Get all fetched URLs
- `get_fetched_url_details`: Get details about a specific fetched URL

### Traffic Analysis
- `get_query_stats`: Get statistics for search queries
- `get_query_traffic_stats`: Get traffic statistics for search queries
- `get_query_page_stats`: Get page statistics for search queries
- `get_query_page_detail_stats`: Get detailed page statistics for search queries
- `get_page_stats`: Get statistics for pages
- `get_page_query_stats`: Get query statistics for pages
- `get_rank_and_traffic_stats`: Get rank and traffic statistics

### Crawling
- `get_crawl_stats`: Get crawling statistics
- `get_crawl_settings`: Get crawling settings
- `save_crawl_settings`: Save crawling settings
- `get_crawl_issues`: Get crawling issues

### Keyword Analysis
- `get_keyword`: Get information about a keyword
- `get_keyword_stats`: Get statistics for a keyword
- `get_related_keywords`: Get related keywords

### Link Analysis
- `get_link_counts`: Get link counts
- `get_url_links`: Get links for a URL
- `get_deep_link`: Get deep link information
- `get_deep_link_blocks`: Get deep link blocks
- `add_deep_link_block`: Add a deep link block
- `remove_deep_link_block`: Remove a deep link block
- `update_deep_link`: Update a deep link
- `get_deep_link_algo_urls`: Get deep link algorithm URLs
- `get_connected_pages`: Get connected pages
- `add_connected_page`: Add a connected page

### Content Management
- `get_url_info`: Get information about a URL
- `get_url_traffic_info`: Get traffic information for a URL
- `get_children_url_info`: Get information about child URLs
- `get_children_url_traffic_info`: Get traffic information for child URLs

### Content Blocking
- `get_blocked_urls`: Get blocked URLs
- `add_blocked_url`: Add a URL to the blocked list
- `remove_blocked_url`: Remove a URL from the blocked list
- `get_active_page_preview_blocks`: Get active page preview blocks
- `add_page_preview_block`: Add a page preview block
- `remove_page_preview_block`: Remove a page preview block

### Regional Settings
- `get_country_region_settings`: Get country/region settings
- `add_country_region_settings`: Add country/region settings
- `remove_country_region_settings`: Remove country/region settings

### URL Management
- `get_query_parameters`: Get query parameters
- `add_query_parameter`: Add a query parameter
- `remove_query_parameter`: Remove a query parameter
- `enable_disable_query_parameter`: Enable or disable a query parameter

## Development

To run all tests:
```bash
make test
```

To build the app:
```bash
make build
```

To lint the project:
```bash
make lint
```

To format the project:
```bash
make format
```

### Environment Variables

The following environment variables are required:

- `BING_WEBMASTER_API_KEY`: Your Bing Webmaster Tools API key

### Starting the Server

To start the MCP server:
```bash
make start
```

### MCP Inspector

You can use the MCP inspector to test the server:
```bash
make mcp_inspector
```

## License

MIT
