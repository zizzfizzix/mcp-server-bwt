# Paginate large list tool results

Tracking issue: #39 (user report: #2)

## 📝 TLDR

Users on MCP clients with small context windows, such as Cursor, can't use the list tools on a real site. `get_query_stats` and the other list tools return every row the Bing API has, so a request for the top 3 pages fails with "Your conversation is too long" (#2). This spec proposes that each of the 27 list-returning tools gets two optional parameters, `offset` and `limit`. The server fetches the full upstream list, returns only the requested slice, and reports `total` and `next_offset` in a trailing text block and in the result's `_meta`. Results are bounded by default: omitting `limit` returns the first 50 rows, and `limit` is capped at 500. Operators who need the old unbounded behavior can set `BING_WEBMASTER_PAGE_SIZE=0`. Output schemas don't change, but the default row count does, so this is a breaking release (`feat!:`).

## 📝 Problem Statement

- `wrap_service_method` (`mcp_server_bwt/tools/bing_webmaster.py`) returns `await method(...)` unchanged. On `main` (mcp 2.2.0), a `List[Model]` return is published as `{"result": [...]}` structured output. It is also serialized as one pretty-printed (`indent=2`) text block per row. Both carry every row.
- Upstream `bing-webmaster-tools` 1.2.0 has no paging on 25 of the 27 list getters, including all 7 traffic getters, whose rows are query × day for months of history. Only `get_children_url_info` and `get_children_url_traffic_info` take an upstream `page` index. The API itself returns everything in one response, so paging can't be pushed upstream.
- The reporter diagnosed this on #2 ("downloads all stats at once … too much data"). The owner agreed that the thin wrapper is the cause. This spec covers the smallest fix inside the current architecture. The task-oriented redesign the owner mentioned on #2 is a separate effort.

## Resolved assumptions (autonomous defaults; Q1 decided by the owner)

| # | Question | Applied default | Why |
|---|----------|-----------------|-----|
| Q1 | Opt-in pagination, or a default `limit` that bounds every call? | **Default limit** (decided by the owner on #40). Omitting `limit` returns 50 rows. | Opt-in would only fix #2 when the assistant chose to pass `limit`. A default bounds every call for every client. It's a breaking change under `BACKWARD_COMPATIBILITY.md` §2, shipped as `feat!:` with a README migration note and an env-var escape hatch (Q7). |
| Q2 | Sorting or filtering (`sort_by`, date range) in this scope? | **Deferred** to a follow-up. | Keeps one capability per spec. Paging alone ends the context overflow. "Top N by clicks" needs sorting and is the natural next ticket. |
| Q3 | Offset/limit or an opaque cursor? | **Offset/limit** (integers). | Every call re-fetches the full upstream list anyway, so a cursor would carry no state an offset lacks. It's also easier for an LLM to fill in. |
| Q4 | Which tools? | **Every registered tool whose upstream return annotation is `list[...]`** (27 today), detected in `wrap_service_method`. Tools returning a single model (`get_url_links`, `get_link_counts`, …) are unchanged. | One uniform rule, no hand-maintained list, and new upstream list tools are covered automatically. |
| Q5 | Default and maximum `limit`? | **Default 50, maximum 500.** `limit` must be between 1 and 500. `offset` must be ≥ 0 and defaults to 0. | At ~300 characters per pretty-printed row, sent as both text and structured content, 50 rows is roughly 8k tokens and fits comfortably in small client windows. The 500 cap stops an assistant from re-creating #2 by asking for everything; larger sets are paged. Both are constants, easy to tune. |
| Q6 | Split into several specs? | **No.** | One capability: bounded list results. |
| Q7 | How do existing users get the old behavior back? | **Optional env var `BING_WEBMASTER_PAGE_SIZE`.** It sets the default `limit` (1–500). `0` disables the default and the cap, returning all rows when `limit` is omitted, as today. Unset means 50. | `BACKWARD_COMPATIBILITY.md` §4 allows new optional env vars. §5 asks that a capability reduction come with a way to restore the old behavior. |

## 📝 Proposed Solution

**Inputs.** Each list tool gains two keyword-only optional parameters, appended to the upstream signature:

- `offset: int = 0` (≥ 0)
- `limit: int` (1–500), defaulting to the configured page size (50 unless `BING_WEBMASTER_PAGE_SIZE` says otherwise). With `BING_WEBMASTER_PAGE_SIZE=0`, the published default is `null` (all rows) and the 500 cap is lifted.

The names avoid `page`. `get_page_query_stats` and `get_query_page_detail_stats` already use `page` for a page URL, and `get_children_url_*` use it for the upstream page index. Where the upstream also pages (`get_children_url_*`), `offset`/`limit` slice within the upstream page the caller asked for. Registration fails loudly (it raises) if an upstream method ever gains a parameter named `offset` or `limit`.

**Structured output — schema unchanged.** `output_schema` stays `{result: list[T]}`, and `structured_content.result` holds the returned slice. `BACKWARD_COMPATIBILITY.md` §2 lists "changing a result shape" as breaking, with no carve-out for added keys. So pagination metadata stays out of the schema. It goes in the `CallToolResult`'s `_meta` under `mcp-server-bwt/pagination`: `{total, offset, limit, next_offset}`. `total` is the upstream row count. `next_offset` is `offset + len(result)` when rows remain, otherwise `null`. Structured-only consumers can also detect the end when `len(result) < limit`.

**Unstructured output.** The wrapper returns a `CallToolResult` itself: one text block per returned row, serialized as mcp 2.2's `_convert_to_content` does today (`pydantic_core.to_json(row, fallback=str, indent=2)`, not `model_dump`). Whenever paging is in effect (always, unless `BING_WEBMASTER_PAGE_SIZE=0` and no `limit`), one trailing text block is added: `Showing rows {offset}–{end} of {total}; next_offset={n}` (or `…; last page`). That block tells the assistant that more rows exist. With paging disabled, the text content is byte-identical to today's. mcp 2.2 validates a returned `CallToolResult`'s `structured_content` against the declared output model (`FuncMetadata.convert_result`), so the schema stays authoritative.

**Description.** The wrapper appends one paragraph to the upstream docstring: "Returns at most `limit` rows (default 50, max 500). When `next_offset` is set, call again with `offset=next_offset` to get more rows." The numbers are rendered from the effective configuration.

**Alternatives considered**

- *Opt-in paging (no default limit).* Non-breaking, but it only fixes #2 when the assistant thinks to pass `limit`. The owner rejected it (Q1). The chosen default doesn't drop data silently: the trailing block and `next_offset` always say more rows exist.
- *Hand-written paginated variants (`get_query_stats_page`).* That doubles the tool count and breaks the rule that tool names mirror upstream methods (`AGENTS.md`).
- *MCP resources or streaming.* Clients that hit #2 don't browse resources, and responses still land in context.

## 📝 Architecture

Code changes are confined to `mcp_server_bwt/tools/bing_webmaster.py`. It reads the optional `BING_WEBMASTER_PAGE_SIZE` there, at registration time, which `main.py` already triggers via `add_bing_webmaster_tools`. No service or entry-point changes.

- `wrap_service_method` reads the upstream return annotation (`typing.get_type_hints`). When its origin is `list`, it sets `wrapper.__signature__` to the upstream parameters plus `offset`/`limit`, keeps the upstream return annotation (so mcp still derives the same `{result: list[T]}` output schema), and appends the description paragraph.
- The wrapper pops `offset`/`limit` from `kwargs` before calling the upstream method, slices the list, and returns `CallToolResult(content=…, structured_content={"result": [row.model_dump(mode="json", by_alias=True) …]}, _meta=…)`. That is the same dump mcp uses for structured content, so field aliases (`Clicks`, `Date`, …) and the UTC date fix (#6) are preserved. mcp validates the returned `structured_content` against the unchanged output model (`FuncMetadata.convert_result`).
- Error handling (`BingWebmasterError`/`ValueError` → `ToolError`) is unchanged. Invalid `offset`/`limit` are rejected by the argument schema (`Annotated[int, Ge(...)]`) before the upstream call.

## 📝 Edge Cases & Failure Scenarios

- **Upstream returns an empty list:** `result: []`; `_meta` pagination `total: 0`, `next_offset: null`.
- **`offset ≥ total`:** empty `result`, `next_offset: null`. This is not an error, so an assistant can stop paging naturally.
- **Data changes between calls:** every page re-fetches, so rows can shift. Stateless paging accepts this, and the description does not promise snapshot consistency.
- **Cost:** each page costs one full upstream call. That's the same API usage per call as today, and rate limits are unchanged (`BingWebmasterService.__init__`).
- **`BING_WEBMASTER_PAGE_SIZE` invalid** (not an integer, or outside 0–500): startup fails with a `ValueError` that names the variable, like the missing-key check in `main.py`. The value is never echoed alongside the API key.
- **A caller relied on getting every row in one call** (for example, a script counting queries): it now gets 50 rows plus `next_offset`. The README migration note and the `_meta.total` field make that visible, and `BING_WEBMASTER_PAGE_SIZE=0` restores the old behavior.
- **Upstream parameter named `offset`/`limit` after an upgrade:** registration raises at import, so the server fails at startup and CI catches it instead of silently shadowing the parameter.

## 📝 Risks & Impact Review

- 💥 **Breaking under `BACKWARD_COMPATIBILITY.md` §2.** Omitting `limit` now returns at most 50 rows instead of all of them. The implementation PR is titled `feat!:`, so release-please bumps the minor version pre-1.0. Its body records the input-schema diff (27 tools gain `offset`/`limit`) and confirms the output schemas are identical before and after.
- §4: `BING_WEBMASTER_PAGE_SIZE` is a new optional env var whose unset default changes behavior. The README documents it under client configuration, together with a before/after migration note (`BING_WEBMASTER_PAGE_SIZE=0` restores today's behavior).
- Relying on `_meta` and a trailing text block is less discoverable than schema fields. Moving the metadata into the output schema would be a further §2 change and is out of scope.
- Rollback is a plain revert. No stored state is involved; users who set the env var just see it ignored.

## 📋 Phasing

Phase 1 (one PR): paging in `wrap_service_method`, tests, README. It's independently shippable. A sorting follow-up (Q2) adds parameters on the same wrapper.

## 📋 Implementation Plan

1. **Slicing helper.** In `mcp_server_bwt/tools/bing_webmaster.py`, add a helper that takes the upstream list, `offset` and `limit` and returns `(rows, total, next_offset)`. Add a page-size resolver that reads `BING_WEBMASTER_PAGE_SIZE` once at registration (unset → 50, `0` → unbounded, invalid → `ValueError`). Unit-test the first page, a middle page, the last page, `offset` past the end, the unbounded mode, an empty list, and each env-var case.
2. **Signature and schema.** Detect list-returning methods in `wrap_service_method`, append `offset`/`limit` to `__signature__` (`limit` defaulting to the resolved page size, `le=500` unless unbounded), keep the upstream return annotation, append the description paragraph, and raise on a name collision. Test with `mcp.list_tools()`: `get_query_stats` has `offset`/`limit` in its input schema with default 50 and maximum 500, every tool's `output_schema` equals the pre-change snapshot, `get_url_links` is unchanged, and the tool count is still 62. Test the collision guard by wrapping a stub service method that already has a `limit` parameter and expecting the raise.
3. **Result building.** Return a `CallToolResult` with per-row text blocks, the trailing summary block whenever paging is in effect, and matching `structured_content`. Test through `mcp.call_tool("get_query_stats", …)` with the upstream method monkeypatched to return 5 `QueryStats` (no network). With `limit=2, offset=0`, expect 2 rows in `structured_content.result`, `_meta` pagination `total: 5` and `next_offset: 2`, and the trailing summary block. With 60 stubbed rows and no `limit`, expect 50 rows and `next_offset: 50`. With `BING_WEBMASTER_PAGE_SIZE=0` and no `limit`, the text content must equal the pre-change output; capture that with the same stub before step 3 lands. Also check that `limit=0` and `limit=501` are rejected.
4. **Docs.** In the README: add a note under `## Available Tools` on `offset`/`limit` and the `next_offset` loop, document `BING_WEBMASTER_PAGE_SIZE` in the client config examples, and add a migration note (before: all rows; after: 50 by default; `=0` to restore). Add a pagination rule to the tool-registration row in `AGENTS.md`, and add the env var to `BACKWARD_COMPATIBILITY.md` §4 as a protected optional variable. Run the validation gate. The implementation PR title is `feat!:`.
