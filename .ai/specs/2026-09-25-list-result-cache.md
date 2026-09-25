# Cache list tool results between pages

Tracking issue: #44 (follow-up to #39 / #41)

## 📝 TLDR

Assistants that page through a large list tool result re-download the whole list from the Bing API on every page. This spec proposes that the server keeps each list tool's upstream result in memory for a short time (default 300 s, set with the new optional `BING_WEBMASTER_CACHE_TTL`, `0` disables it). Later pages of the same query are then sliced from memory. That saves latency and API quota. It also means that pages fetched within one TTL come from the same snapshot.

## 📝 Problem Statement

- In `wrap_service_method` (`mcp_server_bwt/tools/bing_webmaster.py`), `wrapper` awaits the upstream method on every call, and only then does `page_result` slice the list. The Bing API has no server-side paging (see the #39 spec), so every `offset` costs a full download.
- Walking 1,200 `get_query_stats` rows at the default 50 per page makes 24 identical full downloads. That is slow, spends the account's API quota, and pages can disagree when the data changes between fetches.

## Resolved assumptions (autonomous defaults; Q1 decided by the maintainer)

| # | Question | Applied default | Why |
|---|----------|-----------------|-----|
| Q1 | Default TTL? | **300 s** (the maintainer confirmed this on this run). | Bing stats update about once a day, so 5 minutes of staleness is conservative. It is long enough for an assistant to walk a list page by page. |
| Q2 | Do refresh-style callers need a per-call bypass parameter? | **No.** `BING_WEBMASTER_CACHE_TTL=0` turns caching off. | A new tool parameter would be a new public input on 27 tools (§2). The env var already covers operators who need fresh data. It can be added later without breaking anything. |
| Q3 | Where does the cache live? | **One bounded cache per registered list tool**, created inside `wrap_service_method` (up to 16 entries per tool). The issue sketched one module-level cache. | A module-level cache outlives the server that filled it. Tests build a fresh server per case, so a global cache would leak rows between them. A per-tool cache is isolated by construction, needs no tool name in the key, and leaves the 62 registration call sites unchanged. The worst case is 27 × 16 cached lists, each alive for at most one TTL. |
| Q4 | Upper bound on the TTL? | **86,400 s (one day).** | This matches Bing's update cadence. A longer value is almost certainly a typo, so it fails at startup like an out-of-range page size. |

## 📝 Proposed Solution

**Setting.** `resolve_cache_ttl(environ=os.environ) -> int` sits next to `resolve_page_size`, uses the same parsing, and fails the same way. Unset or blank means 300. The value must be an integer from 0 to 86,400. Anything else raises `ValueError("BING_WEBMASTER_CACHE_TTL must be an integer between 0 and 86400")`. `wrap_service_method` resolves the value when it registers a list tool. An invalid value therefore stops the server at import, just as `BING_WEBMASTER_PAGE_SIZE` does.

**Cache.** Add a small stdlib class `ResultCache(ttl: int, max_entries: int = 16)`:

- `get(key) -> list | None` returns the stored rows while `time.monotonic() < expires_at`. An expired entry is dropped and reported as a miss.
- `put(key, rows)` stores `(time.monotonic() + ttl, rows)`. Before storing, it removes expired entries. While the cache is full, it evicts the oldest entry (insertion order of a `dict`).
- With `ttl == 0`, `get` always misses and `put` is a no-op, so behavior matches today's.

**Key.** `pydantic_core.to_json([args, sorted(kwargs.items())], fallback=str)` is computed after `offset` and `limit` are popped. It returns `bytes`, so it is hashable. It covers every upstream argument type: strings, ints, enums, `datetime`, and pydantic models such as `FilterProperties`, without special-casing any of them. Different arguments, for example another `site_url`, give a different key.

**Wrapper flow (paged tools only).** Look up the key before `async with service`. On a hit, skip the upstream call and the client session. On a miss, call upstream as today, then `put` the rows only after the call returns successfully. The `ToolError` mapping is unchanged, and an exception never reaches `put`, so errors are not cached. `page_result` slices the returned rows, whether they came from the cache or from upstream. Single-object and mutating tools never touch the cache.

**Alternatives rejected.** `functools.lru_cache` has no TTL and needs hashable arguments. A third-party TTL cache would add a dependency (a non-goal). Invalidating after write tools needs a map from each write to the reads it affects. With a short TTL, `0` as an opt-out, and no invalidation (a non-goal), a write tool's effect shows up in list tools within one TTL.

## 📝 Edge Cases & Failure Scenarios

- **Concurrent identical calls** both miss and both fetch. The later `put` wins. The result is correct, just not deduplicated, which is acceptable at this scale.
- **Upstream error or validation failure** propagates as a `ToolError` and leaves no cache entry, so the next call retries upstream.
- **Unpaged calls** (`BING_WEBMASTER_PAGE_SIZE=0`, no `limit`) are still cached. Paging and caching are independent.
- **A walk that outlives its entry.** When a walk takes longer than the TTL, or another query evicts its entry (the tool already holds 16 entries), the next page comes from a fresh download. Its `total` may differ from the earlier pages. The client sees this in `_meta` and in the summary line, just as it does on every page today, so the result is no worse than current behavior. A sliding TTL (refreshing on each hit) was rejected: it would let an actively paged list stay stale indefinitely.
- **Shared rows.** Cached rows are handed to `page_result`, which copies each slice into a new list and never mutates the rows.

## 📝 Risks & Impact Review

- `BACKWARD_COMPATIBILITY.md` §4: the new optional variable's default changes freshness, not the result shape. It is non-breaking. Add it to the §4 description.
- §2: results can be up to TTL seconds stale. That includes rows a write tool just changed, such as `add_blocked_url` followed by `get_blocked_urls`. The README must say so and point to `0`. Rollback is `BING_WEBMASTER_CACHE_TTL=0` or a revert. No state persists across restarts.
- Memory is bounded per tool (16 entries) and by time (TTL). No secrets are stored: the key holds only tool arguments, and the API key never enters it.

## 📋 Implementation Plan

### Phase 1: TTL cache for list tools (single PR, `feat:`)

1. **Setting.** Add `DEFAULT_CACHE_TTL = 300`, `MAX_CACHE_TTL = 86400`, `CACHE_TTL_ENV = "BING_WEBMASTER_CACHE_TTL"`, and `resolve_cache_ttl()` with doctests. Add tests beside `test_resolve_page_size` for the defaults and for rejected values (`-1`, `86401`, `ten`, `1.5`).
2. **Cache class.** Add `ResultCache` and a `cache_key(args, kwargs)` helper to `tools/bing_webmaster.py`. Test hit, expiry (with `time.monotonic` monkeypatched), eviction of the oldest entry at the bound, and TTL 0.
3. **Wire into `wrapper`.** Create one `ResultCache(resolve_cache_ttl())` per paged tool in `wrap_service_method`, and look it up and store into it as described above. Add tests to `test_pagination.py` with a counting stub `BingWebmasterClient.request`:
   - two calls with different `offset` make one upstream request;
   - after the TTL (patched clock), a second request is made;
   - another `site_url` misses;
   - `TTL=0` requests every time;
   - an upstream error (stub raises `BingWebmasterError`) is retried on the next call;
   - an invalid env value fails registration with a message naming the variable.
   Existing tests must keep passing unchanged.
4. **Docs.** In the README, document `BING_WEBMASTER_CACHE_TTL` under optional env vars, with the staleness window, the write-tool caveat and `0`. Add a sentence to the paging section. In `BACKWARD_COMPATIBILITY.md` §4, add the variable. In `AGENTS.md`, extend the tool-routing row by one clause about the cache. Run the validation gate.
