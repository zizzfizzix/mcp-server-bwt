import asyncio
import importlib
import inspect
import json
from typing import Any

import pytest
from bing_webmaster_tools import BingWebmasterClient
from bing_webmaster_tools.errors import BingWebmasterError
from mcp.server.mcpserver.exceptions import ToolError, UnexpectedToolError

from mcp_server_bwt.tools.bing_webmaster import (
    SERVICE_CLASSES,
    ResultCache,
    returns_list,
)

EXPECTED_TOOL_COUNT = 62

SITE = {
    "__type": "Site:#Microsoft.Bing.Webmaster.Api",
    "AuthenticationCode": "code",
    "DnsVerificationCode": "dns",
    "IsVerified": True,
    "Url": "https://example.com/",
}


@pytest.fixture(autouse=True)
def no_cached_results(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every test here shares `main.mcp`, so list results must not carry over (#44)."""
    monkeypatch.setattr(ResultCache, "get", lambda self, key: None)


def test_server_imports_and_lists_all_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression for #8 and #14: the server starts on mcp 2.x and lists every tool."""
    monkeypatch.setenv("BING_WEBMASTER_API_KEY", "dummy")
    main = importlib.import_module("mcp_server_bwt.main")

    tools = asyncio.run(main.mcp.list_tools())

    assert len(tools) == EXPECTED_TOOL_COUNT


def test_tool_schemas_do_not_expose_self(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression for #10: input schemas list only the upstream parameters, minus `self`."""
    monkeypatch.setenv("BING_WEBMASTER_API_KEY", "dummy")
    main = importlib.import_module("mcp_server_bwt.main")

    tools = asyncio.run(main.mcp.list_tools())

    for tool in tools:
        # First match wins: `submit_content` exists on two services and is
        # registered from "submission", which comes first in SERVICE_CLASSES
        method = next(
            getattr(cls, tool.name)
            for cls in SERVICE_CLASSES.values()
            if hasattr(cls, tool.name)
        )
        params = list(inspect.signature(method).parameters.values())[1:]
        required = [p.name for p in params if p.default is inspect.Parameter.empty]
        # List tools also take the pagination parameters (#39)
        paging = ["offset", "limit"] if returns_list(method) else []
        expected = [p.name for p in params] + paging
        assert list(tool.input_schema["properties"]) == expected, tool.name
        assert tool.input_schema.get("required", []) == required, tool.name
        description = inspect.cleandoc(method.__doc__ or "")
        assert (tool.description or "").strip().startswith(description), tool.name


def test_legacy_self_argument_is_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression for #10: clients that still send `self` from the old schema keep working."""
    monkeypatch.setenv("BING_WEBMASTER_API_KEY", "dummy")
    main = importlib.import_module("mcp_server_bwt.main")

    async def fake_request(
        self: BingWebmasterClient, *args: Any, **kwargs: Any
    ) -> dict[str, Any]:
        return {"d": [SITE]}

    monkeypatch.setattr(BingWebmasterClient, "request", fake_request)

    sites = asyncio.run(main.mcp.call_tool("get_sites", {"self": ""}))

    assert not sites.is_error
    assert sites.structured_content == {"result": [SITE]}


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

    submitted = asyncio.run(
        main.mcp.call_tool(
            "submit_url",
            {
                "site_url": "https://example.com/",
                "url": "https://example.com/a",
            },
        )
    )
    sites = asyncio.run(main.mcp.call_tool("get_sites", {}))

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
        asyncio.run(main.mcp.call_tool("get_sites", {}))

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
            main.mcp.call_tool("submit_url_batch", {"site_url": "a", "url_list": []})
        )
    with pytest.raises(ToolError) as bad_site:
        asyncio.run(main.mcp.call_tool("get_sites", {}))

    assert not isinstance(empty_batch.value, UnexpectedToolError)
    assert str(empty_batch.value) == (
        "Error executing tool submit_url_batch: URL list cannot be empty"
    )
    assert not isinstance(bad_site.value, UnexpectedToolError)
    assert "validation errors for Site" in str(bad_site.value)
