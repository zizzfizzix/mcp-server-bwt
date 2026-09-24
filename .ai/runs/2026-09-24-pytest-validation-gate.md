# Execution plan: run pytest in the validation gate and the validate CI job

Source doc: .ai/specs/2026-09-24-pytest-validation-gate.md (spec PR #34)
Issue: #30

## Goal

Add `BING_WEBMASTER_API_KEY=dummy uv run pytest mcp_server_bwt --doctest-modules` to `validation.commands` and, as a `Tests` step, to the existing `validate` job, so a PR that breaks a test can't merge.

## Scope

`.ai/agentic.config.json`, `.github/workflows/ci.yml`, `AGENTS.md` (the Validation gate list, the Tests row and the CI row) and `SDLC.md` (the Validation gate section). There are no runtime code changes. The spec file merges through spec PR #34 and isn't committed here.

**Non-goals:** a pytest config refactor in `pyproject.toml`, lefthook changes, removing the import smoke test, coverage, and a Python matrix.

## Risks

- The `validate` job id is the required check on `main`, so it must not be renamed.
- Four hand-kept copies of the gate list could drift. Step 1.4 diffs them.

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles.

### Phase 1: Gate, CI step and docs

- [ ] 1.1 Add pytest to validation.commands
- [ ] 1.2 Add the Tests step to the validate job
- [ ] 1.3 Update the gate docs in AGENTS.md and SDLC.md
- [ ] 1.4 Check the four gate lists match
- [ ] 1.5 Prove validate fails at the Tests step on a broken test
