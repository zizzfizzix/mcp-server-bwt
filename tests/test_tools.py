import pytest
from mcp.server.fastmcp import FastMCP

from mcp_server_bwt.services.bing_webmaster import BingWebmasterService
from mcp_server_bwt.tools.bing_webmaster import add_bing_webmaster_tools


@pytest.fixture
def mcp_server():
    server = FastMCP("test-bwt")
    service = BingWebmasterService(api_key="test_api_key")
    add_bing_webmaster_tools(server, service)
    return server


@pytest.mark.asyncio
async def test_tools_registration(mcp_server):
    tools = await mcp_server.list_tools()
    tool_names = {t.name for t in tools}

    # Check essential tools exist
    expected_tools = {
        "get_sites",
        "get_query_stats",
        "get_page_stats",
        "get_rank_and_traffic_stats",
        "get_page_query_stats",
        "get_crawl_stats",
        "get_crawl_issues",
        "submit_url",
    }
    assert expected_tools.issubset(tool_names)


@pytest.mark.asyncio
async def test_traffic_tools_output_schemas(mcp_server):
    tools = await mcp_server.list_tools()
    tools_dict = {t.name: t for t in tools}

    for tool_name in [
        "get_query_stats",
        "get_page_stats",
        "get_rank_and_traffic_stats",
    ]:
        tool = tools_dict[tool_name]
        schema = tool.outputSchema
        assert schema is not None
        assert "properties" in schema
        assert "result" in schema["properties"]
