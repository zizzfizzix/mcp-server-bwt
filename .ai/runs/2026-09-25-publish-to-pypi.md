# Execution plan: publish mcp-server-bwt to PyPI

Source doc: .ai/specs/2026-09-24-publish-to-pypi.md (spec PR #42)

## Goal

Upload every release that release-please creates to PyPI as `mcp-server-bwt` through Trusted Publishing, and make `uvx mcp-server-bwt` the only documented way for users to install.

## Scope

`pyproject.toml` (metadata, sdist/wheel targets), `.github/workflows/release-please.yml` (job-level permissions, outputs, `build` and `publish` jobs, `workflow_dispatch`), `README.md`, `mcp_server_bwt/test_packaging.py`, `AGENTS.md`, `SDLC.md`, `BACKWARD_COMPATIBILITY.md` and `CODE_REVIEW.md`. The server's runtime code doesn't change.

**Non-goals:** a TestPyPI job, the MCP Registry, attaching dists to GitHub releases, changing `version.py` or the release-please config, and changing repo or PyPI settings (those are maintainer actions and are already done).

## Risks

- The workflow only runs on a real release or a dispatch, so the upload itself can't be tested in this PR. The guard script is tested locally, and the YAML is checked with actionlint.
- The first upload claims the name permanently. It happens only after this PR merges and a release goes out.

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles.

### Phase 1: Packaging and publish pipeline

- [x] 1.1 Metadata — 0a0fe67
- [x] 1.2 Build targets — 3410c36
- [x] 1.3 Workflow — 41a3deb

### Phase 2: Docs

- [ ] 2.1 README and packaging test
- [ ] 2.2 AGENTS.md, SDLC.md, BACKWARD_COMPATIBILITY.md, CODE_REVIEW.md
