# Execution plan: cache list tool results between pages

Source doc: .ai/specs/2026-09-25-list-result-cache.md (spec PR #45)
Issue: #44

## Goal

List tools keep their upstream result in memory for `BING_WEBMASTER_CACHE_TTL` seconds (default 300, `0` disables). Later pages of the same query are sliced from memory instead of being downloaded again.

## Scope

- `mcp_server_bwt/tools/bing_webmaster.py`: TTL resolver, `ResultCache`, cache key, and the wrapper lookup/store.
- `mcp_server_bwt/test_pagination.py`: cache tests.
- Docs: `README.md` (env var, staleness), `BACKWARD_COMPATIBILITY.md` §4, and the `AGENTS.md` tool row.

**Non-goals:** caching single-object or write tools, persistent or shared caches, a per-call bypass parameter, request coalescing.

## Risks

- Staleness is up to one TTL for Bing-computed stats. Write tools clear their area's cached lists, so the server's own changes show up right away.
- The cache is created per registered tool, so tests that build fresh servers stay isolated.

## Progress

PR: #46

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles.

### Phase 1: TTL cache for list tools

- [x] 1.1 Cache TTL setting — 4d867fe
- [x] 1.2 ResultCache and cache key — 4d867fe
- [x] 1.3 Wire the cache into list tool wrappers — 4d867fe (test_startup.py disables cache hits because its tests share main.mcp)
- [x] 1.4 Docs: README, BACKWARD_COMPATIBILITY.md, AGENTS.md — c068152
- [x] Post-review fix: non-string cache key test, §4 exception note, README cache wording — df69635

### Phase 2: Clear cached lists on writes

- [x] 2.1 Write tools clear their area's list caches, with a generation guard against a racing read — 4c11736
