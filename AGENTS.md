# AGENTS.md

## Project overview

`mcp-server-bwt` is a Python 3.13 MCP (Model Context Protocol) server that connects AI assistants to the Bing Webmaster Tools API. It runs over stdio (`MCPServer` from `mcp[cli]` 2.x) and exposes the service methods of the [`bing-webmaster-tools`](https://github.com/merj/bing-webmaster-tools) client library as MCP tools. There are 62 today, covering site management, submission, traffic, crawling, keywords, links, content, blocking, regional settings and URL parameters. It is packaged with hatchling, managed with uv, and published as the `mcp-server-bwt` console script, which is meant to be launched through `uvx`.

## Task routing

| When the task involves… | Read first | Key rules |
|---|---|---|
| Server startup, env config, entry point | `mcp_server_bwt/main.py`, `pyproject.toml` (`[project.scripts]`) | `BING_WEBMASTER_API_KEY` is read at import time and a missing value raises `ValueError`. `app()` is the console-script target and must keep `transport="stdio"`. Never log or echo the API key. |
| Adding, removing or renaming an MCP tool | `mcp_server_bwt/tools/bing_webmaster.py`, `README.md` (`## Available Tools`) | Register tools only through `wrap_service_method(mcp, service, "<service_attr>", "<method>")` and assign the result to a variable named after the method with `# noqa: F841`. Keep tools grouped under the `# <Area> Tools` comments. Tool names, signatures and docstrings come from the upstream library method, so don't hand-write them. Update the README tool list in the same PR. Renaming or removing a tool is a breaking change (see `BACKWARD_COMPATIBILITY.md`). |
| A new upstream service area | `mcp_server_bwt/tools/bing_webmaster.py` (`SERVICE_CLASSES`), `mcp_server_bwt/services/bing_webmaster.py` (`__aenter__`) | Add the service class to `SERVICE_CLASSES` and instantiate it on the same attribute name in `BingWebmasterService.__aenter__`. The two maps must stay in sync. |
| API client settings (timeouts, retries, rate limits, base URL) | `mcp_server_bwt/services/bing_webmaster.py` | Settings are built in `BingWebmasterService.__init__`. The key is wrapped in `pydantic.SecretStr`. Each tool call opens and closes the client through `async with service`. `disable_destructive_operations=False` is deliberate, so destructive tools (remove site, remove feed, …) are exposed. |
| Dependencies and packaging | `pyproject.toml`, `mcp_server_bwt/version.py` | `uv.lock` is committed, so installs are reproducible. Change dependencies in `pyproject.toml`, then run `uv lock` and commit both files. `mcp[cli]` is pinned to `>=2.2,<3`. The server uses `mcp.server.mcpserver.MCPServer`, because mcp 2.x removed `mcp.server.fastmcp` (#8, #14). The next major needs the same schema diff as this one did. The version is sourced from `mcp_server_bwt/version.py` (`__VERSION__`) via `[tool.hatch.version]`. Add dev tools to `[dependency-groups].dev` (this includes `lefthook`, whose PyPI package ships the hook binary). `requires-python` is `>=3.13`. |
| Tests | `pyproject.toml` (`[tool.pytest.ini_options]`), `Makefile` (`test`) | Tests live next to the code as `mcp_server_bwt/test_*.py` (for example `test_startup.py`). pytest runs over `mcp_server_bwt` with `--doctest-modules`, and `pythonpath = "mcp_server_bwt"`. mypy excludes files matching `.+test_`. Collection imports `main.py`, which reads the API key at import time, so run the tests with a dummy key: `BING_WEBMASTER_API_KEY=dummy make test`. TODO: add pytest to the validation gate. |
| Tooling, lint, types, git hooks | `Makefile`, `pyproject.toml` (`[tool.mypy]`), `lefthook.yml` | Code must pass `mypy --strict` and ruff (lint and format, default config). Every function carries full type annotations. Use `# type: ignore` only where the dynamic wrapping genuinely requires it. `make install` installs lefthook git hooks. pre-commit runs `ruff check --fix` and `ruff format` on staged `*.py` files and restages the fixes. pre-push runs `mypy --strict`, plus `uv lock --check` when `pyproject.toml` or `uv.lock` is pushed. Skip them with `--no-verify` or `LEFTHOOK=0`. The hooks don't replace the validation gate below. In a hook sub-job that fixes files, set `stage_fixed: true` on the sub-job itself, not on its group. |
| Releases | `release-please-config.json`, `.release-please-manifest.json`, `.github/workflows/release-please.yml` | release-please owns the version: it keeps a `chore(main): release X.Y.Z` PR open, and merging that PR bumps `mcp_server_bwt/version.py`, updates `CHANGELOG.md`, tags `vX.Y.Z`, and publishes a GitHub release. Never hand-edit `__VERSION__` (its line carries `# x-release-please-version`), `CHANGELOG.md`, or the manifest. The squash-merged PR title decides the bump: `fix:` → patch, `feat:` → minor, and a breaking change (`feat!:` or a `BREAKING CHANGE:` footer) → minor while pre-1.0. `chore:`/`docs:`/`refactor:` don't release. |
| CI | `.github/workflows/ci.yml`, `.github/workflows/release-please.yml` | `ci.yml` has one job, `validate`, which runs on every PR and on every push to `main`. It runs `uv sync --locked`, the validation-gate commands below as separate steps in the same order, and an import smoke test (`BING_WEBMASTER_API_KEY=dummy uv run python -c "import mcp_server_bwt.main"`). `validate` is a required status check on the `main` ruleset (bound to the GitHub Actions app), so a PR can't merge until it passes. Never rename the job, because the required check matches it by name. Release-please PRs are the one exemption. A job-level `if:` skips `validate` when the PR's head is in this repository and its head branch starts with `release-please--branches--`. The skipped job still reports `validate`, which satisfies the required check. Those PRs only touch generated release files, and `main` re-validates after they merge. Fork PRs, other PRs, and pushes to `main` always run the full gate. The workflow steps mirror `validation.commands` in `.ai/agentic.config.json`, so change them together. There are no `paths:` filters, because a required check has to report on every PR. `release-please.yml` runs on push to `main` and opens release PRs with the `RELEASE_PLEASE_TOKEN` repo secret. That secret has to stay set: PRs opened with the default token don't trigger `validate`, and a release PR without it can't merge. |
| Docs | `README.md` | The README documents client setup (Claude Desktop, Zed, via uvx or a local venv) and the full tool list. Keep both accurate when behavior changes. |

## Validation gate

Run in order. Any non-zero exit fails the gate:

1. `uv run ruff check mcp_server_bwt/`
2. `uv run ruff format --check mcp_server_bwt/`
3. `uv run mypy --strict mcp_server_bwt/`
4. `uv build`

Use `make format` or `uv run ruff check --fix` to fix drift locally. `make lint` runs `ruff --fix` and changes files, so it isn't used as the gate.

## Pointers

- Delivery process, labels, claim protocol: `SDLC.md`
- Review rules: `CODE_REVIEW.md`
- Protected contract surfaces: `BACKWARD_COMPATIBILITY.md`
- Pipeline config: `.ai/agentic.config.json` (tracker descriptor in `.ai/trackers/github.md`)
