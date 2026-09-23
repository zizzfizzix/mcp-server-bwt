import asyncio
import importlib
import json
from typing import Any

import pytest
from bing_webmaster_tools import BingWebmasterClient
from bing_webmaster_tools.errors import BingWebmasterError
from mcp.server.mcpserver.exceptions import ToolError, UnexpectedToolError

EXPECTED_TOOL_COUNT = 62

SITE = {
    "__type": "Site:#Microsoft.Bing.Webmaster.Api",
    "AuthenticationCode": "code",
    "DnsVerificationCode": "dns",
    "IsVerified": True,
    "Url": "https://example.com/",
}


def test_server_imports_and_lists_all_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression for #8 and #14: the server starts on mcp 2.x and lists every tool."""
    monkeypatch.setenv("BING_WEBMASTER_API_KEY", "dummy")
    main = importlib.import_module("mcp_server_bwt.main")

    tools = asyncio.run(main.mcp.list_tools())

    assert len(tools) == EXPECTED_TOOL_COUNT


def test_tool_calls_reach_the_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression for #14: tool calls on mcp 2.x pass arguments through and return results."""
    monkeypatch.setenv("BING_WEBMASTER_API_KEY", "dummy")
    main = importlib.import_module("mcp_server_bwt.main")
    requests: list[tuple[str, str, dict[str, Any] | None]] = []

    async def fake_request(
        self: BingWebmasterClient,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        requests.append((method, endpoint, data))
        return {"d": [SITE]} if endpoint == "GetUserSites" else {"d": None}

    monkeypatch.setattr(BingWebmasterClient, "request", fake_request)

    # Every schema still marks `self` as required (#10), so clients have to send it.
    submitted = asyncio.run(
        main.mcp.call_tool(
            "submit_url",
            {
                "self": "",
                "site_url": "https://example.com/",
                "url": "https://example.com/a",
            },
        )
    )
    sites = asyncio.run(main.mcp.call_tool("get_sites", {"self": ""}))

    assert requests == [
        (
            "POST",
            "SubmitUrl",
            {"siteUrl": "https://example.com/", "url": "https://example.com/a"},
        ),
        ("GET", "GetUserSites", None),
    ]
    assert not submitted.is_error
    assert not sites.is_error
    assert json.loads(sites.content[0].text)["Url"] == "https://example.com/"
    assert sites.structured_content == {"result": [SITE]}


def test_upstream_errors_reach_the_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression for #14: mcp 2.x hides non-ToolError messages, so upstream errors are re-raised."""
    monkeypatch.setenv("BING_WEBMASTER_API_KEY", "dummy")
    main = importlib.import_module("mcp_server_bwt.main")

    async def failing_request(
        self: BingWebmasterClient, *args: Any, **kwargs: Any
    ) -> Any:
        raise BingWebmasterError("Invalid API key", status_code=401)

    monkeypatch.setattr(BingWebmasterClient, "request", failing_request)

    with pytest.raises(ToolError) as excinfo:
        asyncio.run(main.mcp.call_tool("get_sites", {"self": ""}))

    assert not isinstance(excinfo.value, UnexpectedToolError)
    assert str(excinfo.value) == "Error executing tool get_sites: Invalid API key"


def test_upstream_argument_checks_reach_the_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression for #14: upstream ValueError and response ValidationError keep their text."""
    monkeypatch.setenv("BING_WEBMASTER_API_KEY", "dummy")
    main = importlib.import_module("mcp_server_bwt.main")

    async def bad_response(self: BingWebmasterClient, *args: Any, **kwargs: Any) -> Any:
        return {"d": [{"Url": "https://example.com/"}]}

    monkeypatch.setattr(BingWebmasterClient, "request", bad_response)

    with pytest.raises(ToolError) as empty_batch:
        asyncio.run(
            main.mcp.call_tool(
                "submit_url_batch", {"self": "", "site_url": "a", "url_list": []}
            )
        )
    with pytest.raises(ToolError) as bad_site:
        asyncio.run(main.mcp.call_tool("get_sites", {"self": ""}))

    assert not isinstance(empty_batch.value, UnexpectedToolError)
    assert str(empty_batch.value) == (
        "Error executing tool submit_url_batch: URL list cannot be empty"
    )
    assert not isinstance(bad_site.value, UnexpectedToolError)
    assert "validation errors for Site" in str(bad_site.value)
