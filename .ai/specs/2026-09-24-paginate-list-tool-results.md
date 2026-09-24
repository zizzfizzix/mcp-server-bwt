# Paginate large list tool results

Tracking issue: #39 (user report: #2)

## 📝 TLDR

Users on MCP clients with small context windows, such as Cursor, can't use the list tools on a real site. `get_query_stats` and the other list tools return every row the Bing API has, so a request for the top 3 pages fails with "Your conversation is too long" (#2). This spec proposes that each of the 27 list-returning tools gets two optional parameters, `offset` and `limit`. The server fetches the full upstream list, returns only the requested slice, and reports `total` and `next_offset` in a trailing text block and in the result's `_meta`. Output schemas don't change. When `limit` is omitted, a call behaves exactly as it does today.

## 📝 Problem Statement

- `wrap_service_method` (`mcp_server_bwt/tools/bing_webmaster.py`) returns `await method(...)` unchanged. On `main` (mcp 2.2.0), a `List[Model]` return is published as `{"result": [...]}` structured output. It is also serialized as one pretty-printed (`indent=2`) text block per row. Both carry every row.
- Upstream `bing-webmaster-tools` 1.2.0 has no paging on 25 of the 27 list getters, including all 7 traffic getters, whose rows are query × day for months of history. Only `get_children_url_info` and `get_children_url_traffic_info` take an upstream `page` index. The API itself returns everything in one response, so paging can't be pushed upstream.
- The reporter diagnosed this on #2 ("downloads all stats at once … too much data"). The owner agreed that the thin wrapper is the cause. This spec covers the smallest fix inside the current architecture. The task-oriented redesign the owner mentioned on #2 is a separate effort.

## Resolved assumptions (autonomous defaults)

| # | Question | Applied default | Why |
|---|----------|-----------------|-----|
| Q1 | Opt-in pagination, or a default `limit` that bounds every call? | **Opt-in.** With `limit` omitted, the tool returns all rows as it does today. The tool description tells the assistant to pass `limit`. ⚠ NEEDS HUMAN CONFIRMATION | A default limit changes the results of every existing call (`BACKWARD_COMPATIBILITY.md` §2) and needs a `feat!:` release. Opt-in is additive and reversible, but it only fixes #2 when the assistant chooses to pass `limit`. The owner should decide whether to take the breaking default instead. |
| Q2 | Sorting or filtering (`sort_by`, date range) in this scope? | **Deferred** to a follow-up. | Keeps one capability per spec. Paging alone ends the context overflow. "Top N by clicks" needs sorting and is the natural next ticket. |
| Q3 | Offset/limit or an opaque cursor? | **Offset/limit** (integers). | Every call re-fetches the full upstream list anyway, so a cursor would carry no state an offset lacks. It's also easier for an LLM to fill in. |
| Q4 | Which tools? | **Every registered tool whose upstream return annotation is `list[...]`** (27 today), detected in `wrap_service_method`. Tools returning a single model (`get_url_links`, `get_link_counts`, …) are unchanged. | One uniform rule, no hand-maintained list, and new upstream list tools are covered automatically. |
| Q5 | Maximum `limit`? | **None.** `limit` must be ≥ 1. `offset` must be ≥ 0 and defaults to 0. | A cap would be a new restriction to maintain. It can be added later without breaking anyone. |
| Q6 | Split into several specs? | **No.** | One capability: bounded list results. |

## 📝 Proposed Solution

**Inputs.** Each list tool gains two keyword-only optional parameters, appended to the upstream signature:

- `offset: int = 0` (≥ 0)
- `limit: int | None = None` (≥ 1)

The names avoid `page`. `get_page_query_stats` and `get_query_page_detail_stats` already use `page` for a page URL, and `get_children_url_*` use it for the upstream page index. Where the upstream also pages (`get_children_url_*`), `offset`/`limit` slice within the upstream page the caller asked for. Registration fails loudly (it raises) if an upstream method ever gains a parameter named `offset` or `limit`.

**Structured output — schema unchanged.** `output_schema` stays `{result: list[T]}`, and `structured_content.result` holds the returned slice. `BACKWARD_COMPATIBILITY.md` §2 lists "changing a result shape" as breaking, with no carve-out for added keys. So pagination metadata stays out of the schema. It goes in the `CallToolResult`'s `_meta` under `mcp-server-bwt/pagination`: `{total, offset, limit, next_offset}`. `total` is the upstream row count. `next_offset` is `offset + len(result)` when rows remain, otherwise `null`. Structured-only consumers can also detect the end when `len(result) < limit`.

**Unstructured output.** The wrapper returns a `CallToolResult` itself: one text block per returned row, serialized as mcp 2.2's `_convert_to_content` does today (`pydantic_core.to_json(row, fallback=str, indent=2)`, not `model_dump`). When `limit` is passed, one trailing text block is added: `Showing rows {offset}–{end} of {total}; next_offset={n}` (or `…; last page`). With `limit` omitted, the text content is byte-identical to today's. mcp 2.2 validates a returned `CallToolResult`'s `structured_content` against the declared output model (`FuncMetadata.convert_result`), so the schema stays authoritative.

**Description.** The wrapper appends one paragraph to the upstream docstring: "Returns all rows unless `limit` is set; large sites can return thousands of rows. Pass `limit` (and `offset` from `next_offset`) to page through them."

**Alternatives considered**

- *Truncate every result to N rows by default.* This would fix #2 for every client, but it's breaking and silently drops data. See Q1.
- *Hand-written paginated variants (`get_query_stats_page`).* That doubles the tool count and breaks the rule that tool names mirror upstream methods (`AGENTS.md`).
- *MCP resources or streaming.* Clients that hit #2 don't browse resources, and responses still land in context.

## 📝 Architecture

This change touches one module, `mcp_server_bwt/tools/bing_webmaster.py`. No service, env, or entry-point changes.

- `wrap_service_method` reads the upstream return annotation (`typing.get_type_hints`). When its origin is `list`, it sets `wrapper.__signature__` to the upstream parameters plus `offset`/`limit`, keeps the upstream return annotation (so mcp still derives the same `{result: list[T]}` output schema), and appends the description paragraph.
- The wrapper pops `offset`/`limit` from `kwargs` before calling the upstream method, slices the list, and returns `CallToolResult(content=…, structured_content={"result": [row.model_dump(mode="json", by_alias=True) …]}, _meta=…)`. That is the same dump mcp uses for structured content, so field aliases (`Clicks`, `Date`, …) and the UTC date fix (#6) are preserved. mcp validates the returned `structured_content` against the unchanged output model (`FuncMetadata.convert_result`).
- Error handling (`BingWebmasterError`/`ValueError` → `ToolError`) is unchanged. Invalid `offset`/`limit` are rejected by the argument schema (`Annotated[int, Ge(...)]`) before the upstream call.

## 📝 Edge Cases & Failure Scenarios

- **Upstream returns an empty list:** `result: []`; `_meta` pagination `total: 0`, `next_offset: null`.
- **`offset ≥ total`:** empty `result`, `next_offset: null`. This is not an error, so an assistant can stop paging naturally.
- **Data changes between calls:** every page re-fetches, so rows can shift. Stateless paging accepts this, and the description does not promise snapshot consistency.
- **Cost:** each page costs one full upstream call. That's the same API usage per call as today, and rate limits are unchanged (`BingWebmasterService.__init__`).
- **Upstream parameter named `offset`/`limit` after an upgrade:** registration raises at import, so the server fails at startup and CI catches it instead of silently shadowing the parameter.

## 📝 Risks & Impact Review

- `BACKWARD_COMPATIBILITY.md` §2: new optional parameters are non-breaking, and output schemas and the no-`limit` results are unchanged, so this ships as `feat:`. The PR body records the input-schema diff (27 tools gain `offset`/`limit`) and confirms the output schemas are identical before and after.
- Relying on `_meta` and a trailing text block is less discoverable than schema fields. Moving the metadata into the schema later would be a §2 breaking change, bundled with any Q1 override.
- If the owner overrides Q1 with a default limit, it becomes `feat!:` with a README migration note.
- Rollback is a plain revert. No stored state, config, or env is involved.

## 📋 Phasing

Phase 1 (one PR): paging in `wrap_service_method`, tests, README. It's independently shippable. A sorting follow-up (Q2) adds parameters on the same wrapper.

## 📋 Implementation Plan

1. **Slicing helper.** In `mcp_server_bwt/tools/bing_webmaster.py`, add a helper that takes the upstream list, `offset` and `limit` and returns `(rows, total, next_offset)`. Unit-test the first page, a middle page, the last page, `offset` past the end, `limit=None`, and an empty list.
2. **Signature and schema.** Detect list-returning methods in `wrap_service_method`, append `offset`/`limit` to `__signature__`, keep the upstream return annotation, append the description paragraph, and raise on a name collision. Test with `mcp.list_tools()`: `get_query_stats` has `offset`/`limit` in its input schema, every tool's `output_schema` equals the pre-change snapshot, `get_url_links` is unchanged, and the tool count is still 62. Test the collision guard by wrapping a stub service method that already has a `limit` parameter and expecting the raise.
3. **Result building.** Return a `CallToolResult` with per-row text blocks, the trailing summary block only when `limit` is set, and matching `structured_content`. Test through `mcp.call_tool("get_query_stats", …)` with the upstream method monkeypatched to return 5 `QueryStats` (no network). With `limit=2, offset=0`, expect 2 rows in `structured_content.result`, `_meta` pagination `total: 5` and `next_offset: 2`, and the trailing summary block. With no `limit`, the text content must equal the pre-change output; capture that with the same stub before step 3 lands. Also check that invalid `limit=0` is rejected.
4. **Docs.** Add a README note under `## Available Tools` on `offset`/`limit` and the `next_offset` loop, and add a pagination rule to the tool-registration row in `AGENTS.md`. Run the validation gate.
