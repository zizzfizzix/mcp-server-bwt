import inspect
import os
import time
import weakref
from collections.abc import Callable, Mapping, Sequence
from functools import wraps
from typing import Annotated, Any, TypeVar, get_origin, get_type_hints

import pydantic_core
from bing_webmaster_tools.errors import BingWebmasterError
from bing_webmaster_tools.services import (
    content_blocking,
    content_management,
    crawling,
    keyword_analysis,
    link_analysis,
    regional_settings,
    site_management,
    submission,
    traffic_analysis,
    url_management,
)
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import CallToolResult, ContentBlock, TextContent
from pydantic import Field, TypeAdapter

from mcp_server_bwt.services.bing_webmaster import BingWebmasterService

T = TypeVar("T")

# Pagination of list results (#39): tools returning a list are sliced locally,
# because the upstream API returns every row in one response
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 500
PAGE_SIZE_ENV = "BING_WEBMASTER_PAGE_SIZE"
PAGINATION_META_KEY = "mcp-server-bwt/pagination"

# Caching of list results (#44): later pages of the same query are sliced from
# the cached upstream list instead of downloading it again
DEFAULT_CACHE_TTL = 300
MAX_CACHE_TTL = 86400
CACHE_TTL_ENV = "BING_WEBMASTER_CACHE_TTL"
CACHE_MAX_ENTRIES = 16


def resolve_page_size(environ: Mapping[str, str] = os.environ) -> int | None:
    """Return the default `limit` for list tools, or None when paging is disabled.

    >>> resolve_page_size({})
    50
    >>> resolve_page_size({"BING_WEBMASTER_PAGE_SIZE": "0"}) is None
    True
    >>> resolve_page_size({"BING_WEBMASTER_PAGE_SIZE": "200"})
    200
    """
    raw = environ.get(PAGE_SIZE_ENV, "").strip()
    if not raw:
        return DEFAULT_PAGE_SIZE
    try:
        value = int(raw)
    except ValueError:
        value = -1
    if not 0 <= value <= MAX_PAGE_SIZE:
        raise ValueError(
            f"{PAGE_SIZE_ENV} must be an integer between 0 and {MAX_PAGE_SIZE}"
        )
    return value or None


def resolve_cache_ttl(environ: Mapping[str, str] = os.environ) -> int:
    """Return how many seconds list tool results are cached, 0 when disabled.

    >>> resolve_cache_ttl({})
    300
    >>> resolve_cache_ttl({"BING_WEBMASTER_CACHE_TTL": "0"})
    0
    >>> resolve_cache_ttl({"BING_WEBMASTER_CACHE_TTL": "60"})
    60
    """
    raw = environ.get(CACHE_TTL_ENV, "").strip()
    if not raw:
        return DEFAULT_CACHE_TTL
    try:
        value = int(raw)
    except ValueError:
        value = -1
    if not 0 <= value <= MAX_CACHE_TTL:
        raise ValueError(
            f"{CACHE_TTL_ENV} must be an integer between 0 and {MAX_CACHE_TTL}"
        )
    return value


def cache_key(args: Sequence[Any], kwargs: Mapping[str, Any]) -> bytes:
    """A hashable key for an upstream call's arguments.

    >>> cache_key((), {"b": 2, "a": "x"}) == cache_key((), {"a": "x", "b": 2})
    True
    >>> cache_key((), {"a": "x"}) == cache_key((), {"a": "y"})
    False
    """
    return pydantic_core.to_json([list(args), sorted(kwargs.items())], fallback=str)


class ResultCache:
    """A small in-memory cache of upstream lists, each kept for `ttl` seconds.

    Holds at most `max_entries` lists and evicts the oldest first. A `ttl` of
    0 disables it. `clear()` drops every entry and bumps `generation`, so a
    list fetched before the clear is not stored after it.
    """

    def __init__(self, ttl: int, max_entries: int = CACHE_MAX_ENTRIES) -> None:
        self.ttl = ttl
        self.max_entries = max_entries
        self.generation = 0
        self._entries: dict[bytes, tuple[float, list[Any]]] = {}

    def clear(self) -> None:
        self._entries.clear()
        self.generation += 1

    def get(self, key: bytes) -> list[Any] | None:
        entry = self._entries.get(key)
        if entry is None:
            return None
        expires_at, rows = entry
        if time.monotonic() >= expires_at:
            del self._entries[key]
            return None
        return rows

    def put(self, key: bytes, rows: list[Any], generation: int | None = None) -> None:
        if self.ttl <= 0 or generation not in (None, self.generation):
            return
        now = time.monotonic()
        for stale in [k for k, (exp, _) in self._entries.items() if exp <= now]:
            del self._entries[stale]
        self._entries.pop(key, None)
        while len(self._entries) >= self.max_entries:
            del self._entries[next(iter(self._entries))]
        self._entries[key] = (now + self.ttl, rows)


# The list caches of each service area, per service instance, so a write tool
# can clear the lists it may have changed (#44). Site writes (removing a site
# or a role) change what every area returns for that site, so they clear all.
GLOBAL_WRITE_AREA = "sites"
_AREA_CACHES: weakref.WeakKeyDictionary[
    BingWebmasterService, dict[str, list[ResultCache]]
] = weakref.WeakKeyDictionary()


def is_write_tool(method_name: str, paged: bool) -> bool:
    """Whether a tool may change data: anything but a list tool or a `get_` tool.

    >>> is_write_tool("add_blocked_url", paged=False)
    True
    >>> is_write_tool("get_crawl_settings", paged=False)
    False
    """
    return not paged and not method_name.startswith("get_")


def paginate[R](
    rows: Sequence[R], offset: int, limit: int | None
) -> tuple[list[R], int, int | None]:
    """Slice `rows` and return (page, total, next_offset).

    `next_offset` is None once the page reaches the end of `rows`.

    >>> paginate([1, 2, 3, 4, 5], 0, 2)
    ([1, 2], 5, 2)
    >>> paginate([1, 2, 3, 4, 5], 4, 2)
    ([5], 5, None)
    >>> paginate([1, 2, 3], 7, 2)
    ([], 3, None)
    """
    total = len(rows)
    stop = total if limit is None else offset + limit
    page = list(rows[offset:stop])
    end = offset + len(page)
    return page, total, end if page and end < total else None


PAGINATION_DOC = """

Returns at most `limit` rows (default {default}{cap}). When the result reports
a `next_offset`, call again with `offset=next_offset` to get more rows."""

_ROWS_ADAPTER: TypeAdapter[list[Any]] = TypeAdapter(list[Any])


def returns_list(method: Callable[..., Any]) -> bool:
    """Whether an upstream service method is annotated to return a list."""
    return get_origin(get_type_hints(method).get("return")) is list


def pagination_parameters(page_size: int | None) -> list[inspect.Parameter]:
    """The `offset` and `limit` parameters appended to every list tool."""
    offset = inspect.Parameter(
        "offset",
        inspect.Parameter.KEYWORD_ONLY,
        default=0,
        annotation=Annotated[int, Field(ge=0, description="Index of the first row.")],
    )
    limit_description = "Maximum number of rows to return."
    if page_size is None:
        limit_annotation: Any = Annotated[
            int | None, Field(ge=1, description=limit_description)
        ]
    else:
        limit_annotation = Annotated[
            int, Field(ge=1, le=MAX_PAGE_SIZE, description=limit_description)
        ]
    limit = inspect.Parameter(
        "limit",
        inspect.Parameter.KEYWORD_ONLY,
        default=page_size,
        annotation=limit_annotation,
    )
    return [offset, limit]


def page_result(
    rows: Sequence[Any], offset: int, limit: int | None
) -> list[Any] | CallToolResult:
    """Build a list tool's result for the requested page.

    Without paging in effect the upstream list is returned as is, so mcp
    serializes it exactly as before. Otherwise the result keeps the
    `{"result": [...]}` output schema and reports the paging state in `_meta`
    and in a trailing text block.
    """
    if limit is None and offset == 0:
        return list(rows)
    page, total, next_offset = paginate(rows, offset, limit)
    status = f"next_offset={next_offset}" if next_offset is not None else "last page"
    summary = f"Showing {len(page)} of {total} rows from offset {offset}; {status}"
    # Serialize rows the way mcp does for a returned list (one block per row)
    content: list[ContentBlock] = [
        TextContent(
            type="text",
            text=pydantic_core.to_json(row, fallback=str, indent=2).decode(),
        )
        for row in page
    ]
    content.append(TextContent(type="text", text=summary))
    return CallToolResult(
        content=content,
        structured_content={
            "result": _ROWS_ADAPTER.dump_python(page, mode="json", by_alias=True)
        },
        _meta={
            PAGINATION_META_KEY: {
                "total": total,
                "offset": offset,
                "limit": limit,
                "next_offset": next_offset,
            }
        },
    )


# Map service attribute names to their corresponding service classes
SERVICE_CLASSES = {
    "sites": site_management.SiteManagementService,
    "submission": submission.SubmissionService,
    "traffic": traffic_analysis.TrafficAnalysisService,
    "crawling": crawling.CrawlingService,
    "keywords": keyword_analysis.KeywordAnalysisService,
    "links": link_analysis.LinkAnalysisService,
    "content": content_management.ContentManagementService,
    "blocking": content_blocking.ContentBlockingService,
    "regional": regional_settings.RegionalSettingsService,
    "urls": url_management.UrlManagementService,
}


def wrap_service_method(
    mcp: MCPServer, service: BingWebmasterService, service_attr: str, method_name: str
) -> Callable[..., Any]:
    """Helper function to wrap a service method with mcp.tool() while preserving its signature and docstring.

    Args:
        mcp: The MCP server instance
        service: The BingWebmasterService instance
        service_attr: The service attribute name (e.g., 'sites', 'submission')
        method_name: The method name to wrap

    Returns:
        The wrapped method as an MCP tool
    """
    # Get the service class from our mapping
    service_class = SERVICE_CLASSES[service_attr]
    # Get the original method
    original_method = getattr(service_class, method_name)
    # Get the signature
    sig = inspect.signature(original_method)
    # Remove 'self' parameter from signature
    parameters = list(sig.parameters.values())[1:]  # Skip 'self'

    paged = returns_list(original_method)
    page_size = resolve_page_size() if paged else None
    cache = ResultCache(resolve_cache_ttl()) if paged else None
    # Shared by every tool of this service area, including ones registered later
    areas = _AREA_CACHES.setdefault(service, {})
    if cache is not None:
        areas.setdefault(service_attr, []).append(cache)
    clears_area = is_write_tool(method_name, paged)

    def clear_written_caches() -> None:
        for attr, caches in areas.items():
            if service_attr in (attr, GLOBAL_WRITE_AREA):
                for area_cache in caches:
                    area_cache.clear()

    doc = original_method.__doc__
    if paged:
        collisions = {"offset", "limit"} & {p.name for p in parameters}
        if collisions:
            raise ValueError(
                f"{method_name} already has parameter(s) {sorted(collisions)}, "
                "which clash with pagination"
            )
        parameters += pagination_parameters(page_size)
        cap = "" if page_size is None else f", max {MAX_PAGE_SIZE}"
        default = "all rows" if page_size is None else str(page_size)
        doc = (doc or "").rstrip() + PAGINATION_DOC.format(default=default, cap=cap)

    # Create new signature without 'self'
    new_sig = sig.replace(parameters=parameters)

    # Create wrapper function with same signature
    @wraps(original_method)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        offset: int = kwargs.pop("offset", 0) if paged else 0
        limit: int | None = kwargs.pop("limit", page_size) if paged else None
        key = cache_key(args, kwargs) if cache is not None else b""
        if cache is not None and (rows := cache.get(key)) is not None:
            return page_result(rows, offset, limit)
        generation = cache.generation if cache is not None else None
        async with service as s:
            service_obj = getattr(s, service_attr)
            # Get the method from the instance
            method = getattr(service_obj, method_name)
            # Call the method directly - it's already bound to the instance
            try:
                result = await method(*args, **kwargs)
            except (BingWebmasterError, ValueError) as exc:
                # mcp 2.x only forwards the message of a ToolError to the client;
                # ValueError includes pydantic.ValidationError
                raise ToolError(str(exc)) from exc
            finally:
                # A failed write may still have changed data upstream
                if clears_area:
                    clear_written_caches()
        if cache is None:
            return result
        cache.put(key, result, generation)
        return page_result(result, offset, limit)

    # Copy signature and docstring before registering, because mcp.tool()
    # builds the tool's input schema from them when it is applied (#10)
    wrapper.__signature__ = new_sig  # type: ignore
    wrapper.__doc__ = doc

    mcp.tool()(wrapper)

    return wrapper


def add_bing_webmaster_tools(mcp: MCPServer, service: BingWebmasterService) -> None:
    # Site Management Tools
    get_sites = wrap_service_method(mcp, service, "sites", "get_sites")  # noqa: F841
    add_site = wrap_service_method(mcp, service, "sites", "add_site")  # noqa: F841
    verify_site = wrap_service_method(mcp, service, "sites", "verify_site")  # noqa: F841
    remove_site = wrap_service_method(mcp, service, "sites", "remove_site")  # noqa: F841
    get_site_roles = wrap_service_method(mcp, service, "sites", "get_site_roles")  # noqa: F841
    add_site_roles = wrap_service_method(mcp, service, "sites", "add_site_roles")  # noqa: F841
    remove_site_role = wrap_service_method(mcp, service, "sites", "remove_site_role")  # noqa: F841
    get_site_moves = wrap_service_method(mcp, service, "sites", "get_site_moves")  # noqa: F841
    submit_site_move = wrap_service_method(mcp, service, "sites", "submit_site_move")  # noqa: F841

    # Submission Tools
    submit_url = wrap_service_method(mcp, service, "submission", "submit_url")  # noqa: F841
    submit_url_batch = wrap_service_method(  # noqa: F841
        mcp, service, "submission", "submit_url_batch"
    )
    submit_content = wrap_service_method(mcp, service, "submission", "submit_content")  # noqa: F841
    submit_feed = wrap_service_method(mcp, service, "submission", "submit_feed")  # noqa: F841
    get_feeds = wrap_service_method(mcp, service, "submission", "get_feeds")  # noqa: F841
    get_feed_details = wrap_service_method(  # noqa: F841
        mcp, service, "submission", "get_feed_details"
    )
    remove_feed = wrap_service_method(mcp, service, "submission", "remove_feed")  # noqa: F841
    get_url_submission_quota = wrap_service_method(  # noqa: F841
        mcp, service, "submission", "get_url_submission_quota"
    )
    get_content_submission_quota = wrap_service_method(  # noqa: F841
        mcp, service, "submission", "get_content_submission_quota"
    )
    fetch_url = wrap_service_method(mcp, service, "submission", "fetch_url")  # noqa: F841
    get_fetched_urls = wrap_service_method(  # noqa: F841
        mcp, service, "submission", "get_fetched_urls"
    )
    get_fetched_url_details = wrap_service_method(  # noqa: F841
        mcp, service, "submission", "get_fetched_url_details"
    )

    # Traffic Analysis Tools
    get_query_stats = wrap_service_method(mcp, service, "traffic", "get_query_stats")  # noqa: F841
    get_query_traffic_stats = wrap_service_method(  # noqa: F841
        mcp, service, "traffic", "get_query_traffic_stats"
    )
    get_query_page_stats = wrap_service_method(  # noqa: F841
        mcp, service, "traffic", "get_query_page_stats"
    )
    get_query_page_detail_stats = wrap_service_method(  # noqa: F841
        mcp, service, "traffic", "get_query_page_detail_stats"
    )
    get_page_stats = wrap_service_method(mcp, service, "traffic", "get_page_stats")  # noqa: F841
    get_page_query_stats = wrap_service_method(  # noqa: F841
        mcp, service, "traffic", "get_page_query_stats"
    )
    get_rank_and_traffic_stats = wrap_service_method(  # noqa: F841
        mcp, service, "traffic", "get_rank_and_traffic_stats"
    )

    # Crawling Tools
    get_crawl_stats = wrap_service_method(mcp, service, "crawling", "get_crawl_stats")  # noqa: F841
    get_crawl_settings = wrap_service_method(  # noqa: F841
        mcp, service, "crawling", "get_crawl_settings"
    )
    save_crawl_settings = wrap_service_method(  # noqa: F841
        mcp, service, "crawling", "save_crawl_settings"
    )
    get_crawl_issues = wrap_service_method(mcp, service, "crawling", "get_crawl_issues")  # noqa: F841

    # Keyword Analysis Tools
    get_keyword = wrap_service_method(mcp, service, "keywords", "get_keyword")  # noqa: F841
    get_keyword_stats = wrap_service_method(  # noqa: F841
        mcp, service, "keywords", "get_keyword_stats"
    )
    get_related_keywords = wrap_service_method(  # noqa: F841
        mcp, service, "keywords", "get_related_keywords"
    )

    # Link Analysis Tools
    get_link_counts = wrap_service_method(mcp, service, "links", "get_link_counts")  # noqa: F841
    get_url_links = wrap_service_method(mcp, service, "links", "get_url_links")  # noqa: F841
    get_deep_link = wrap_service_method(mcp, service, "links", "get_deep_link")  # noqa: F841
    get_deep_link_blocks = wrap_service_method(  # noqa: F841
        mcp, service, "links", "get_deep_link_blocks"
    )
    add_deep_link_block = wrap_service_method(  # noqa: F841
        mcp, service, "links", "add_deep_link_block"
    )
    remove_deep_link_block = wrap_service_method(  # noqa: F841
        mcp, service, "links", "remove_deep_link_block"
    )
    update_deep_link = wrap_service_method(mcp, service, "links", "update_deep_link")  # noqa: F841
    get_deep_link_algo_urls = wrap_service_method(  # noqa: F841
        mcp, service, "links", "get_deep_link_algo_urls"
    )
    get_connected_pages = wrap_service_method(  # noqa: F841
        mcp, service, "links", "get_connected_pages"
    )
    add_connected_page = wrap_service_method(  # noqa: F841
        mcp, service, "links", "add_connected_page"
    )

    # Content Management Tools
    get_url_info = wrap_service_method(mcp, service, "content", "get_url_info")  # noqa: F841
    get_url_traffic_info = wrap_service_method(  # noqa: F841
        mcp, service, "content", "get_url_traffic_info"
    )
    get_children_url_info = wrap_service_method(  # noqa: F841
        mcp, service, "content", "get_children_url_info"
    )
    get_children_url_traffic_info = wrap_service_method(  # noqa: F841
        mcp, service, "content", "get_children_url_traffic_info"
    )

    # Content Blocking Tools
    get_blocked_urls = wrap_service_method(mcp, service, "blocking", "get_blocked_urls")  # noqa: F841
    add_blocked_url = wrap_service_method(mcp, service, "blocking", "add_blocked_url")  # noqa: F841
    remove_blocked_url = wrap_service_method(  # noqa: F841
        mcp, service, "blocking", "remove_blocked_url"
    )
    get_active_page_preview_blocks = wrap_service_method(  # noqa: F841
        mcp, service, "blocking", "get_active_page_preview_blocks"
    )
    add_page_preview_block = wrap_service_method(  # noqa: F841
        mcp, service, "blocking", "add_page_preview_block"
    )
    remove_page_preview_block = wrap_service_method(  # noqa: F841
        mcp, service, "blocking", "remove_page_preview_block"
    )

    # Regional Settings Tools
    get_country_region_settings = wrap_service_method(  # noqa: F841
        mcp, service, "regional", "get_country_region_settings"
    )
    add_country_region_settings = wrap_service_method(  # noqa: F841
        mcp, service, "regional", "add_country_region_settings"
    )
    remove_country_region_settings = wrap_service_method(  # noqa: F841
        mcp, service, "regional", "remove_country_region_settings"
    )

    # URL Management Tools
    get_query_parameters = wrap_service_method(  # noqa: F841
        mcp, service, "urls", "get_query_parameters"
    )
    add_query_parameter = wrap_service_method(  # noqa: F841
        mcp, service, "urls", "add_query_parameter"
    )
    remove_query_parameter = wrap_service_method(  # noqa: F841
        mcp, service, "urls", "remove_query_parameter"
    )
    enable_disable_query_parameter = wrap_service_method(  # noqa: F841
        mcp, service, "urls", "enable_disable_query_parameter"
    )
