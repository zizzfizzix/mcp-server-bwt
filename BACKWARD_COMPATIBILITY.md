# Backward compatibility

`mcp-server-bwt` is consumed by MCP clients (Claude Desktop, Zed, Cursor, …) that users configure by hand and that AI assistants drive by tool name. The surfaces below are protected contracts. Review skills check every change against this file, and implementation skills warn when a change breaks one.

The project is pre-1.0, but users run it via `uvx mcp-server-bwt`, which picks up new releases without any action on their side. Breaking changes therefore still need the paths below. Versions are cut by release-please (see `SDLC.md`, *Releasing*). Where a path below asks for a minor version bump, mark the PR title breaking (`feat!:` / `fix!:`, or a `BREAKING CHANGE:` footer), which makes release-please bump the minor version while pre-1.0. Never edit `mcp_server_bwt/version.py` by hand.

## Protected surfaces

### 1. MCP tool names

The 62 tools registered in `mcp_server_bwt/tools/bing_webmaster.py` (listed in the README `## Available Tools` section). A tool's name is its upstream method name (`get_sites`, `submit_url`, …).

- **Breaking:** removing or renaming a tool; registering it under a different upstream method that changes its behavior.
- **Non-breaking:** adding a new tool.
- **Required path:** note the removal or rename in the PR body and README. For a rename, keep the old name registered alongside the new one for at least one minor release, and mention the deprecation in its description. Mark the PR title breaking so release-please bumps the minor version.

### 2. Tool input schemas and results

Parameter names, types, required-ness and defaults for each tool. These come from the upstream `bing-webmaster-tools` method signature, minus `self`. Result shapes are whatever the upstream method returns.

- **Breaking:** removing or renaming a parameter; making an optional parameter required; changing a type incompatibly; changing a result shape. This includes changes that arrive via an upstream `bing-webmaster-tools` upgrade.
- **Non-breaking:** new optional parameters; docstring and description improvements.
- **Required path:** for dependency upgrades, diff the tool list and signatures before and after the upgrade and record any breaking changes in the PR body. For intentional changes, follow the tool-name path above.

### 3. Console script and launch contract

`[project.scripts] mcp-server-bwt = "mcp_server_bwt.main:app"`, the stdio transport, and the `python mcp_server_bwt/main.py` path documented in the README for venv setups.

- **Breaking:** renaming the script or the `mcp_server_bwt.main:app` target; changing the default transport away from stdio; moving `main.py`; raising `requires-python` (currently `>=3.13`).
- **Required path:** a README migration note with before and after client config, plus a minor version bump. Keep the old entry point working for one minor release where possible.

### 4. Environment configuration

`BING_WEBMASTER_API_KEY` (required; the server refuses to start without it).

- **Breaking:** renaming or removing it; adding a new *required* variable.
- **Non-breaking:** new optional variables with defaults that keep current behavior.
- **Required path:** accept the old variable name alongside the new one for at least one minor release, and document both in the README.

### 5. Client behavior settings

The API client settings in `BingWebmasterService.__init__`: `disable_destructive_operations=False`, the base URL, timeout, retries and rate limits.

- **Breaking:** changing `disable_destructive_operations` (it changes which tools work); changes that make previously working calls fail (for example, a tighter timeout or a different base URL).
- **Required path:** call it out in the PR body and README. When a change reduces capability, make it opt-in through a new optional environment variable instead.

### 6. Package identity

The distribution name `mcp-server-bwt` and the import package `mcp_server_bwt`.

- **Breaking:** renaming either one.
- **Required path:** avoid. If it's unavoidable, publish under both names for a transition period and document the change in the README.

## Not protected

Internal helpers (`wrap_service_method`, `SERVICE_CLASSES`, `SiteInfo`, and the attribute names on `BingWebmasterService`), the Makefile targets, and the dev tooling can change freely, as long as the surfaces above behave the same.
