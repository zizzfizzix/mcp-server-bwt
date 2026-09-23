import asyncio
import importlib

import pytest

EXPECTED_TOOL_COUNT = 62


def test_server_imports_and_lists_all_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression for #8: an mcp release without FastMCP must not be installed."""
    monkeypatch.setenv("BING_WEBMASTER_API_KEY", "dummy")
    main = importlib.import_module("mcp_server_bwt.main")

    tools = asyncio.run(main.mcp.list_tools())

    assert len(tools) == EXPECTED_TOOL_COUNT
