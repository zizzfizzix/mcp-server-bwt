# Execution plan: update dependencies

## Goal

Bring every dependency and toolchain pin up to its latest compatible release, where the bump is safe and meaningful.

## Scope

Inventory taken 2026-09-25 against PyPI, GitHub releases and endoflife.date:

| Item | Current | Latest | Action |
|---|---|---|---|
| `uv.lock`: ruff | 0.16.8 | 0.16.9 | Refresh with `uv lock --upgrade` |
| `uv.lock`: uvicorn (via mcp[cli]) | 0.53.0 | 0.54.0 | Refresh |
| `uv.lock`: opentelemetry-api (via mcp) | 1.44.0 | 1.45.0 | Refresh |
| `.python-version`, `.tool-versions` python | 3.13.2 | 3.13.15 | Bump patch (security and bug fixes; CI provisions this version) |
| `.tool-versions` uv | 0.6.12 | 0.12.19 | Bump to the current uv |
| `googleapis/release-please-action` | v4 | v5.0.0 | Bump; the only breaking change is the Node 24 runtime, which GitHub-hosted runners provide |
| mcp, bing-webmaster-tools, mypy, pytest, lefthook | latest | — | Already current |
| actions/checkout v7, upload-artifact v7, download-artifact v8, setup-uv v10.2.0, gh-action-pypi-publish v1.14.2 | latest | — | Already current |

**Non-goals:** moving to Python 3.14 (a supported-version decision, not a bump), changing `requires-python` or the `mcp[cli]>=2.2,<3` range, raising dependency floors in `pyproject.toml`, editing historical specs that mention the old pins.

## Risks

- The lockfile bumps are patch/minor releases of a linter and transitive runtime deps; the full gate covers them.
- release-please v5 can only be exercised on the next push to `main`. Its inputs and outputs are unchanged from v4 (the release notes list only the Node 24 runtime as breaking).
- The lockfile does not reach PyPI users (`uvx` resolves from `pyproject.toml`), so this ships as `chore(deps)` with no release.

## Implementation Plan

### Phase 1: Python dependencies

1.1 Refresh `uv.lock` with `uv lock --upgrade`, then run the gate.

### Phase 2: Toolchain pins

2.1 Bump the Python pin in `.python-version` and `.tool-versions` to 3.13.15.
2.2 Bump the uv pin in `.tool-versions` to 0.12.19.

### Phase 3: CI actions

3.1 Bump `googleapis/release-please-action` to v5 and update its output comment.

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles.

### Phase 1: Python dependencies

- [x] 1.1 Refresh uv.lock — 78b2a3c

### Phase 2: Toolchain pins

- [ ] 2.1 Bump Python pin to 3.13.15
- [ ] 2.2 Bump uv pin to 0.12.19

### Phase 3: CI actions

- [ ] 3.1 Bump release-please-action to v5
