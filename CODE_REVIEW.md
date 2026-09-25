# Code review rules

These rules apply to every PR in `mcp-server-bwt`, whether a human or `om-code-review` reviews it. They add to the built-in review checklist and don't replace it.

## Review priorities

1. **Correctness.** Tools must call the upstream `bing-webmaster-tools` method they claim to wrap, with the arguments the MCP client sent.
2. **Security.** The Bing Webmaster API key must never leak. Destructive operations must stay deliberate.
3. **Contracts.** Tool names, parameters, the console script and env vars are the public surface (see `BACKWARD_COMPATIBILITY.md`).
4. **Type safety and hygiene.** Code passes `mypy --strict` and ruff with no new blanket suppressions.

## Repo-specific checks

### Tool registration (`mcp_server_bwt/tools/bing_webmaster.py`)

- Every new tool is registered through `wrap_service_method`, not a hand-written `@mcp.tool()` function, unless the PR explains why the generic wrapper can't express it.
- `service_attr` must be a key of `SERVICE_CLASSES`, and `method_name` must exist on that class in the pinned upstream version. A typo only fails at server start (`AttributeError` or `KeyError` at import), so make sure the author started the server or the inspector (`make start` / `make mcp_inspector`).
- A new `SERVICE_CLASSES` entry has a matching attribute set in `BingWebmasterService.__aenter__` (`mcp_server_bwt/services/bing_webmaster.py`) under the same name.
- The wrapper must expose the upstream signature minus `self` (`__signature__`) and the upstream docstring, which MCP clients see as the tool schema and description. `wrap_service_method` sets `__signature__` and `__doc__` before calling `mcp.tool()`, because registration builds the schema right away. Don't approve changes that register the wrapper before both are assigned (#10). `test_tool_schemas_do_not_expose_self` guards this. Changes to this signature rewriting affect every tool at once, so treat them as `risk-high`.
- A tool that is added, removed or renamed is reflected in the README `## Available Tools` section in the same PR.

### Service and client lifecycle (`mcp_server_bwt/services/bing_webmaster.py`)

- Each tool call enters and exits `BingWebmasterService` via `async with`. Watch for client state leaking across calls and for `__aexit__` being skipped.
- Changes to `Settings` (timeouts, retries, rate limits, base URL) need a stated reason. Rate limits protect the user's Bing API quota.
- Flipping `disable_destructive_operations` changes which tools work for every user. It's a behavior change and needs to be called out in the PR body.

### Secrets and configuration

- `BING_WEBMASTER_API_KEY` stays wrapped in `SecretStr` and never appears in logs, exceptions, tool results or docs examples (use `YOUR_API_KEY_HERE`).
- New environment variables are documented in the README `### Environment Variables` section and have safe defaults, or fail fast with a clear error the way the API key does in `main.py`.

### Typing and style

- New code is fully annotated and passes `mypy --strict`. Each new `# type: ignore` needs a narrow reason. The existing one on `wrapper.__signature__` is the model.
- `# noqa: F841` is only acceptable on tool-registration assignments.
- Formatting is whatever `ruff format` produces. Don't hand-format against it.

### Dependencies and packaging

- Dependency changes go through `pyproject.toml` (and the uv lockfile when one is committed). An upgrade of `bing-webmaster-tools` or `mcp` can silently change tool signatures. Check the tool list against the new version before approving.
- Versions are owned by release-please (`SDLC.md`, *Releasing*). Only the bot's `chore(main): release X.Y.Z` PR edits `mcp_server_bwt/version.py`, `CHANGELOG.md` and `.release-please-manifest.json`. A hand edit in any other PR is a finding, and the fix is a Conventional Commit PR title that produces the intended bump.
- PyPI publishing (`build`/`publish` jobs in `.github/workflows/release-please.yml`): `id-token: write` stays scoped to the `publish` job, `publish` keeps `environment: pypi`, `pypa/gh-action-pypi-publish` stays pinned to a full commit SHA, and the build job keeps its tag-format and version-match checks. Adding a PyPI API token secret is a finding, because the upload uses Trusted Publishing. Renaming `release-please.yml` or the `pypi` environment breaks the PyPI Trusted Publisher and needs a matching change on PyPI.
- The sdist `include` list and the wheel `exclude` in `pyproject.toml` decide what reaches PyPI. Don't widen them to repo process files (`.ai/`, `SDLC.md`, workflows).

### Tests

- PRs that add behavior beyond straight registration (custom tools, argument transformation, error handling) should add pytest tests under `mcp_server_bwt/`. Mock the upstream client; tests must not hit the live Bing API.

## Validation gate

Before sign-off, the PR must pass the validation gate listed in `AGENTS.md` (Validation gate), which mirrors `validation.commands` in `.ai/agentic.config.json`: ruff check, ruff format check, `mypy --strict`, `uv build`, and the pytest suite with a dummy API key. CI runs the same gate as the required `validate` check, so a green `validate` run is the gate evidence. A failing or skipped step is a finding.

## Severity guidance

- **Blocker:** a leaked API key or secret; a tool that calls the wrong upstream method; a server that fails to start; a breaking contract change without the path in `BACKWARD_COMPATIBILITY.md`; destructive behavior enabled or widened without being called out.
- **Major:** a missing README update for a tool change; a `SERVICE_CLASSES` / `__aenter__` mismatch; new untyped code or broad `type: ignore`; client-lifecycle regressions; a gate failure.
- **Minor:** naming, comment and docstring nits; grouping or ordering of registrations; README wording.

Label discipline follows `SDLC.md`: reviewers move the pipeline label, and changes to the tool surface or the wrapper are at least `risk-medium`.
