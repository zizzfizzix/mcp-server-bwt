import asyncio
import inspect
import json
from datetime import datetime
from enum import Enum
from types import UnionType
from typing import Annotated, Any, Union, get_args, get_origin, get_type_hints

import pytest
from bing_webmaster_tools import BingWebmasterClient
from bing_webmaster_tools.models.traffic_analysis import QueryStats
from bing_webmaster_tools.services.traffic_analysis import TrafficAnalysisService
from mcp.client.client import Client
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import CallToolResult, TextContent
from pydantic import BaseModel

from mcp_server_bwt.services.bing_webmaster import BingWebmasterService
from mcp_server_bwt.tools.bing_webmaster import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    PAGE_SIZE_ENV,
    PAGINATION_META_KEY,
    SERVICE_CLASSES,
    add_bing_webmaster_tools,
    page_result,
    paginate,
    resolve_page_size,
    returns_list,
    wrap_service_method,
)

ROWS = list(range(5))


@pytest.mark.parametrize(
    ("offset", "limit", "expected"),
    [
        (0, 2, ([0, 1], 5, 2)),  # first page
        (2, 2, ([2, 3], 5, 4)),  # middle page
        (4, 2, ([4], 5, None)),  # last, short page
        (3, 2, ([3, 4], 5, None)),  # last page ending exactly at the end
        (5, 2, ([], 5, None)),  # offset at the end
        (9, 2, ([], 5, None)),  # offset past the end
        (0, None, (ROWS, 5, None)),  # unbounded
        (2, None, ([2, 3, 4], 5, None)),  # unbounded from an offset
    ],
)
def test_paginate(
    offset: int, limit: int | None, expected: tuple[list[int], int, int | None]
) -> None:
    """#39: slices, totals and next offsets cover every page position."""
    assert paginate(ROWS, offset, limit) == expected


def test_paginate_empty_list() -> None:
    assert paginate([], 0, 50) == ([], 0, None)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, DEFAULT_PAGE_SIZE),
        ("", DEFAULT_PAGE_SIZE),
        ("0", None),
        ("1", 1),
        (" 120 ", 120),
        ("500", 500),
    ],
)
def test_resolve_page_size(value: str | None, expected: int | None) -> None:
    """#39: the env var tunes the default page size, 0 disables paging."""
    environ = {} if value is None else {PAGE_SIZE_ENV: value}
    assert resolve_page_size(environ) == expected


@pytest.mark.parametrize("value", ["-1", "501", "ten", "1.5"])
def test_resolve_page_size_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError, match=PAGE_SIZE_ENV):
        resolve_page_size({PAGE_SIZE_ENV: value})


def _server(
    monkeypatch: pytest.MonkeyPatch, rows: int, page_size: str | None = None
) -> MCPServer:
    """A server whose Bing client answers every request with `rows` query stats."""
    if page_size is None:
        monkeypatch.delenv(PAGE_SIZE_ENV, raising=False)
    else:
        monkeypatch.setenv(PAGE_SIZE_ENV, page_size)

    async def fake_request(
        self: BingWebmasterClient, *args: Any, **kwargs: Any
    ) -> dict[str, Any]:
        return {"d": [_query_stats(i) for i in range(rows)]}

    monkeypatch.setattr(BingWebmasterClient, "request", fake_request)
    mcp = MCPServer("test")
    add_bing_webmaster_tools(mcp, BingWebmasterService("dummy"))
    return mcp


def _query_stats(i: int) -> dict[str, object]:
    return {
        "__type": "QueryStats:#Microsoft.Bing.Webmaster.Api",
        "Date": "/Date(1781222400000)/",
        "Query": f"query {i}",
        "AvgClickPosition": 1,
        "AvgImpressionPosition": 1,
        "Clicks": i,
        "Impressions": i,
    }


def _call(mcp: MCPServer, arguments: dict[str, Any]) -> CallToolResult:
    result = asyncio.run(
        mcp.call_tool(
            "get_query_stats", {"site_url": "https://example.com/"} | arguments
        )
    )
    assert isinstance(result, CallToolResult)
    return result


def _pagination(result: CallToolResult) -> dict[str, Any]:
    assert result.meta is not None
    meta: dict[str, Any] = result.meta[PAGINATION_META_KEY]
    return meta


def _texts(result: CallToolResult) -> list[str]:
    return [block.text for block in result.content if isinstance(block, TextContent)]


def test_list_tools_are_bounded_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """#39/#2: omitting `limit` returns the default page, not every row."""
    result = _call(_server(monkeypatch, 60), {})

    assert result.structured_content is not None
    rows = result.structured_content["result"]
    assert [row["Query"] for row in rows] == [f"query {i}" for i in range(50)]
    assert _pagination(result) == {
        "total": 60,
        "offset": 0,
        "limit": 50,
        "next_offset": 50,
    }
    assert len(result.content) == 51
    assert _texts(result)[-1] == "Showing 50 of 60 rows from offset 0; next_offset=50"


def test_offset_and_limit_page_through_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    mcp = _server(monkeypatch, 5)

    first = _call(mcp, {"limit": 2})
    last = _call(mcp, {"limit": 2, "offset": 4})
    past = _call(mcp, {"limit": 2, "offset": 9})

    assert first.structured_content is not None
    assert [r["Clicks"] for r in first.structured_content["result"]] == [0, 1]
    assert _pagination(first)["next_offset"] == 2
    assert last.structured_content is not None
    assert [r["Clicks"] for r in last.structured_content["result"]] == [4]
    assert _pagination(last)["next_offset"] is None
    assert _texts(last)[-1] == "Showing 1 of 5 rows from offset 4; last page"
    assert past.structured_content == {"result": []}
    assert _pagination(past)["next_offset"] is None


def test_paged_rows_match_unpaged_serialization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """#39: paged row blocks and structured rows are byte-identical to unpaged ones."""
    paged = _call(_server(monkeypatch, 3), {})
    unpaged = _call(_server(monkeypatch, 3, page_size="0"), {})

    assert unpaged.meta is None
    assert paged.content[:-1] == unpaged.content
    assert paged.structured_content == unpaged.structured_content
    # The date fix from #6 survives the re-serialization
    assert unpaged.structured_content is not None
    assert unpaged.structured_content["result"][0]["Date"] == "2026-06-12T00:00:00Z"


def test_page_size_env_disables_paging(monkeypatch: pytest.MonkeyPatch) -> None:
    """#39: BING_WEBMASTER_PAGE_SIZE=0 restores unbounded results and lifts the cap."""
    mcp = _server(monkeypatch, 600, page_size="0")
    result = _call(mcp, {})
    schema = _limit_schema(mcp)

    assert result.structured_content is not None
    assert len(result.structured_content["result"]) == 600
    assert len(result.content) == 600
    assert schema["default"] is None
    assert "maximum" not in json.dumps(schema)


def test_page_size_env_sets_the_default(monkeypatch: pytest.MonkeyPatch) -> None:
    mcp = _server(monkeypatch, 30, page_size="10")

    assert _pagination(_call(mcp, {}))["limit"] == 10
    assert _limit_schema(mcp)["default"] == 10


def test_limit_schema_and_bounds(monkeypatch: pytest.MonkeyPatch) -> None:
    mcp = _server(monkeypatch, 5)
    schema = _limit_schema(mcp)

    assert schema["default"] == DEFAULT_PAGE_SIZE
    assert schema["minimum"] == 1
    assert schema["maximum"] == MAX_PAGE_SIZE
    for arguments in ({"limit": 0}, {"limit": MAX_PAGE_SIZE + 1}, {"offset": -1}):
        with pytest.raises(ToolError):
            _call(mcp, arguments)


def test_output_schemas_are_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    """#39: list tools keep their `{"result": [...]}` output schema (§2)."""
    tools = {t.name: t for t in asyncio.run(_server(monkeypatch, 0).list_tools())}

    for name in ("get_query_stats", "get_sites", "get_crawl_issues"):
        schema = tools[name].output_schema
        assert schema is not None
        assert list(schema["properties"]) == ["result"], name
    assert "limit" not in tools["get_url_links"].input_schema["properties"]
    assert "limit" not in tools["get_link_counts"].input_schema["properties"]


def test_list_tool_count(monkeypatch: pytest.MonkeyPatch) -> None:
    tools = asyncio.run(_server(monkeypatch, 0).list_tools())

    assert sum("limit" in t.input_schema["properties"] for t in tools) == 27


def test_invalid_page_size_env_fails_registration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ValueError, match=PAGE_SIZE_ENV):
        _server(monkeypatch, 0, page_size="1000")


def test_pagination_parameter_collision_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """#39: an upstream `limit` parameter must not be silently shadowed."""

    async def get_query_stats(self: Any, site_url: str, limit: int) -> list[QueryStats]:
        return []

    monkeypatch.setattr(
        TrafficAnalysisService, "get_query_stats", get_query_stats, raising=True
    )
    with pytest.raises(ValueError, match="clash with pagination"):
        wrap_service_method(
            MCPServer("test"),
            BingWebmasterService("dummy"),
            "traffic",
            "get_query_stats",
        )


def _limit_schema(mcp: MCPServer) -> dict[str, Any]:
    tools = asyncio.run(mcp.list_tools())
    tool = next(t for t in tools if t.name == "get_query_stats")
    schema: dict[str, Any] = tool.input_schema["properties"]["limit"]
    return schema


def test_paging_state_reaches_the_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """#39: `_meta`, the rows and the summary block survive the MCP protocol round trip."""
    mcp = _server(monkeypatch, 5)

    async def run() -> CallToolResult:
        async with Client(mcp) as client:
            return await client.call_tool(
                "get_query_stats", {"site_url": "https://example.com/", "limit": 2}
            )

    result = asyncio.run(run())

    assert not result.is_error
    assert _pagination(result) == {
        "total": 5,
        "offset": 0,
        "limit": 2,
        "next_offset": 2,
    }
    assert result.structured_content is not None
    assert len(result.structured_content["result"]) == 2
    assert _texts(result)[-1] == "Showing 2 of 5 rows from offset 0; next_offset=2"


def _sample(tp: Any, name: str = "") -> Any:
    """A raw API value for type `tp`, as the Bing API would send it."""
    origin = get_origin(tp)
    if origin is Annotated:
        return _sample(get_args(tp)[0], name)
    if origin in (Union, UnionType):
        return _sample(next(a for a in get_args(tp) if a is not type(None)), name)
    if origin is list:
        return [_sample(get_args(tp)[0], name)]
    if isinstance(tp, type) and issubclass(tp, BaseModel):
        return _raw_row(tp)
    if isinstance(tp, type) and issubclass(tp, Enum):
        return list(tp)[-1].value
    samples: dict[Any, Any] = {
        bool: True,
        int: 5,
        float: 1.5,
        datetime: "/Date(1781222400000)/",
    }
    if tp in samples:
        return samples[tp]
    return "https://example.com/" if "url" in name else "x"


def _raw_row(model: type[BaseModel]) -> dict[str, Any]:
    hints = get_type_hints(model, include_extras=True)
    # Fields with upstream validators that reject generic samples
    overrides: dict[str, Any] = {
        "crawl_rate": [1] * 24,
        "two_letter_iso_country_code": "us",
    }
    return {
        field.alias or name: overrides.get(name, _sample(hints[name], name))
        for name, field in model.model_fields.items()
    }


LIST_METHODS = [
    (attr, name)
    for attr, cls in SERVICE_CLASSES.items()
    for name, method in inspect.getmembers(cls, inspect.iscoroutinefunction)
    if not name.startswith("_") and returns_list(method)
]


@pytest.mark.parametrize(("attr", "name"), LIST_METHODS)
def test_every_list_tool_pages_like_it_serializes(
    monkeypatch: pytest.MonkeyPatch, attr: str, name: str
) -> None:
    """#39: each list tool's rows pass mcp's re-validation and match unpaged output."""
    monkeypatch.delenv(PAGE_SIZE_ENV, raising=False)
    method = getattr(SERVICE_CLASSES[attr], name)
    element = get_args(get_type_hints(method)["return"])[0]
    rows = [
        element.model_validate(_raw_row(element))
        if isinstance(element, type) and issubclass(element, BaseModel)
        else _sample(element)
        for _ in range(3)
    ]
    mcp = MCPServer("test")
    wrap_service_method(mcp, BingWebmasterService("dummy"), attr, name)
    metadata = mcp._tool_manager.get_tool(name).fn_metadata

    unpaged = metadata.convert_result(rows)
    paged = metadata.convert_result(page_result(rows, 0, 50))

    assert isinstance(unpaged, CallToolResult)
    assert isinstance(paged, CallToolResult)
    assert paged.structured_content == unpaged.structured_content
    assert paged.content[:-1] == unpaged.content
