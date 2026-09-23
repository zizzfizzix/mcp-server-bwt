# Execution plan: release-please automated releases

Source doc: .ai/specs/2026-09-23-release-please.md (lands via spec PR #20)
Issue: #16

## Goal

Merging a release-please release PR bumps `mcp_server_bwt/version.py`, updates `CHANGELOG.md`, tags `vX.Y.Z`, and publishes a GitHub release.

## Scope

- New: `release-please-config.json`, `.release-please-manifest.json`, `.github/workflows/release-please.yml`.
- `mcp_server_bwt/version.py`: `# x-release-please-version` annotation.
- Docs: `AGENTS.md`, `SDLC.md`, `BACKWARD_COMPATIBILITY.md`.

**Non-goals:** PyPI publishing; changelog backfill before `v0.1.0`; changing repo settings (the Actions PR-creation toggle and merge-commit policy stay maintainer actions); a validation CI workflow (#11).

## Implementation Plan

### Phase 1: Release automation

1. Add the release-please config and manifest (spec step 1).
2. Annotate the version line and check that hatch still parses it (spec step 2).
3. Add the workflow (spec step 3).

### Phase 2: Docs

1. AGENTS.md: add a Releases row and update the CI row.
2. SDLC.md: add a Releasing note.
3. BACKWARD_COMPATIBILITY.md: replace the manual version-bump instructions.

## Risks

- The repo setting "Allow GitHub Actions to create and approve pull requests" is off, so the first workflow run fails until the maintainer enables it (spec A3).
- A release PR opened with `GITHUB_TOKEN` won't trigger other workflows. This matters once #11 lands, and it is mitigated by the `RELEASE_PLEASE_TOKEN` fallback (spec A1).

## Progress

PR: #22

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles.

### Phase 1: Release automation

- [x] 1.1 Add release-please config and manifest — aff2b5d
- [x] 1.2 Annotate version line — 4a7438e
- [x] 1.3 Add release-please workflow — 0ec8355

### Phase 2: Docs

- [x] 2.1 AGENTS.md release and CI rows — 23ba6c7
- [x] 2.2 SDLC.md releasing note — b8e471e
- [x] 2.3 BACKWARD_COMPATIBILITY.md version-bump path — 2a3a931
