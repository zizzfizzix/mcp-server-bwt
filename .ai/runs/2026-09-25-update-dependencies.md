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

**Non-goals:** raising `requires-python` above `>=3.13` (breaking per `BACKWARD_COMPATIBILITY.md`; 3.13 keeps security support until 2029-10), a CI Python matrix (it would rename the required `validate` check) or the `mcp[cli]>=2.2,<3` range, raising dependency floors in `pyproject.toml`, editing historical specs that mention the old pins.

## Scope addendum (maintainer request, 2026-09-25)

Python 3.13 bugfix support ends 2026-10-01, so development and CI move to Python 3.14.7 (bugfix support until 2027-10). `requires-python` stays `>=3.13`; mypy `python_version` stays 3.13 so type checks target the floor; a 3.14 classifier is added.

## Risks

- CI only runs 3.14 after this. The 3.13 floor is covered by mypy/ruff targeting 3.13 and a one-off local pytest run on 3.13.15 (112 passed).

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

### Phase 4: Python 3.14

4.1 Pin Python 3.14.7 for development and CI, add the 3.14 classifier.
4.2 Update AGENTS.md for the supported-vs-pinned Python split.

## Progress

PR: #47

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles.

### Phase 1: Python dependencies

- [x] 1.1 Refresh uv.lock — 78b2a3c

### Phase 2: Toolchain pins

- [x] 2.1 Bump Python pin to 3.13.15 — 5464bfc
- [x] 2.2 Bump uv pin to 0.12.19 — 17c6592

### Phase 3: CI actions

- [x] 3.1 Bump release-please-action to v5 — 39998ac

### Phase 4: Python 3.14

- [x] 4.1 Pin Python 3.14.7 — c6e870c
- [x] 4.2 Update AGENTS.md Python notes — dd4ed11
