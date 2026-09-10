# mcp-server-bwt

> MCP server for Bing Webmaster Tools (Fixed & Compatible Edition for **Claude Desktop** and **Antigravity**)

This MCP ([Model Context Protocol](https://modelcontextprotocol.io/introduction)) server provides a bridge between AI assistants (such as **Claude Desktop**, **Antigravity**, Cursor, etc.) and the Bing Webmaster Tools API. It exposes all Bing Webmaster Tools functionality available via [`bing-webmaster-tools`](https://github.com/merj/bing-webmaster-tools) as MCP tools.

### Key Fixes in this Fork
- **Fixed Date Serialization Error (Issue #6)**: Resolved the bug where `get_query_stats`, `get_page_stats`, `get_rank_and_traffic_stats`, and `get_page_query_stats` failed with `Date must match format "date-time"`. All date objects are normalized to UTC timezone-aware datetimes producing RFC 3339 compliant ISO strings with `'Z'` suffix.
- **Fixed FastMCP / MCP SDK Pinning**: Standardized dependencies to `mcp[cli]>=1.2.0,<2.0.0` ensuring seamless fastmcp stdio transport operation across all client applications.

---

## Installation & Configuration

### 1. Configuration for Antigravity

Add the following entry to your Antigravity MCP configuration (or `mcpServers` settings):

```json
{
  "mcpServers": {
    "bing_webmaster": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/agalliani/mcp-server-bwt.git",
        "mcp_server_bwt"
      ],
      "env": {
        "BING_WEBMASTER_API_KEY": "YOUR_BING_API_KEY_HERE"
      }
    }
  }
}
```

Or for local development:

```json
{
  "mcpServers": {
    "bing_webmaster": {
      "command": "/PATH/TO/mcp-bing-webmaster/.venv/bin/mcp-server-bwt",
      "env": {
        "BING_WEBMASTER_API_KEY": "YOUR_BING_API_KEY_HERE"
      }
    }
  }
}
```

### 2. Configuration for Claude Desktop

In your `claude_desktop_config.json` (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "mcp_server_bwt": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/agalliani/mcp-server-bwt.git",
        "mcp_server_bwt"
      ],
      "env": {
        "BING_WEBMASTER_API_KEY": "YOUR_BING_API_KEY_HERE"
      }
    }
  }
}
```

---

## Example Prompts

Once configured in Antigravity or Claude Desktop, you can ask your AI assistant:

- *"List all my verified sites in Bing Webmaster Tools"*
- *"Get query performance and traffic statistics for my site https://example.com"*
- *"Submit https://example.com/new-article for indexing"*
- *"Check crawl statistics and crawl issues for my site"*

---

## Available Tools

- **Site Management**: `get_sites`, `add_site`, `verify_site`, `remove_site`, `get_site_roles`, `add_site_roles`, `remove_site_role`, `get_site_moves`, `submit_site_move`
- **URL Submission**: `submit_url`, `submit_url_batch`, `submit_content`, `submit_feed`, `get_feeds`, `get_feed_details`, `remove_feed`, `get_url_submission_quota`, `get_content_submission_quota`, `fetch_url`, `get_fetched_urls`, `get_fetched_url_details`
- **Traffic Analysis**: `get_query_stats`, `get_query_traffic_stats`, `get_query_page_stats`, `get_query_page_detail_stats`, `get_page_stats`, `get_page_query_stats`, `get_rank_and_traffic_stats`
- **Crawling**: `get_crawl_stats`, `get_crawl_settings`, `save_crawl_settings`, `get_crawl_issues`
- **Keyword Analysis**: `get_keyword`, `get_keyword_stats`, `get_related_keywords`
- **Link Analysis**: `get_link_counts`, `get_url_links`, `get_deep_link`, `get_deep_link_blocks`, `add_deep_link_block`, `remove_deep_link_block`, `update_deep_link`, `get_deep_link_algo_urls`, `get_connected_pages`, `add_connected_page`
- **Content Management**: `get_url_info`, `get_url_traffic_info`, `get_children_url_info`, `get_children_url_traffic_info`
- **Content Blocking**: `get_blocked_urls`, `add_blocked_url`, `remove_blocked_url`, `get_active_page_preview_blocks`, `add_page_preview_block`, `remove_page_preview_block`
- **Regional Settings**: `get_country_region_settings`, `add_country_region_settings`, `remove_country_region_settings`
- **URL Management**: `get_query_parameters`, `add_query_parameter`, `remove_query_parameter`, `enable_disable_query_parameter`

---

## Development & Testing

Run all unit tests and quality checks:

```bash
uv run pytest
uv run ruff check .
uv run mypy mcp_server_bwt
```

## License

`mcp-server-bwt` is licensed under the MIT License.
