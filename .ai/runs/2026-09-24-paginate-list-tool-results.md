# Execution plan: paginate large list tool results

Source doc: .ai/specs/2026-09-24-paginate-list-tool-results.md (spec PR #40)
Issue: #39 (user report: #2)

## Goal

The 27 list-returning tools return at most 50 rows by default. They take `offset` and `limit` (max 500) and report `total`/`next_offset` in a trailing text block and in `_meta`. `BING_WEBMASTER_PAGE_SIZE` tunes the default, and `0` restores unbounded results.

## Scope

`mcp_server_bwt/tools/bing_webmaster.py` (wrapper, slicing, page-size resolver), a new `mcp_server_bwt/test_pagination.py`, `README.md` (tool note, env var, migration note), `AGENTS.md` (tool-registration row), and `BACKWARD_COMPATIBILITY.md` (§2 note, §4 env var). Output schemas stay unchanged.

**Non-goals:** sorting/filtering (spec Q2), caching across calls, changing single-object tools, moving the metadata into output schemas.

## Risks

- Breaking default (§2): the PR title must be `feat!:`.
- Text content must stay byte-identical when paging is disabled. Pinned by a test that compares against mcp's own conversion.

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles.

### Phase 1: Paging in wrap_service_method

- [x] 1.1 Slicing helper and page-size resolver — 9f725aa
- [x] 1.2 Signature and schema for list tools — f89c8ef
- [x] 1.3 Result building with CallToolResult and _meta — f89c8ef (also: the #6 date parser accepts RFC 3339 date-times so mcp can re-validate paged rows)
- [x] 1.4 Docs: README, AGENTS.md, BACKWARD_COMPATIBILITY.md — 87e67fd
