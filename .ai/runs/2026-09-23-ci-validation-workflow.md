# Execution plan: CI workflow running the validation gate

Source doc: .ai/specs/2026-09-23-ci-validation-workflow.md (spec PR #26)
Issue: #11

## Goal

Add `.github/workflows/ci.yml` with one job, `validate`, that runs the four validation-gate commands plus an import smoke test on every PR and every push to `main`, so the gate is enforced rather than remembered.

## Scope

A new `.github/workflows/ci.yml`, plus the `AGENTS.md` CI row and the `SDLC.md` Validation gate section. No runtime code changes. The spec file itself merges through spec PR #26 and isn't committed here.

**Non-goals:** applying the ruleset change (spec Phase 2). The maintainer applied it on 2026-09-24: ruleset 12497565 now requires `validate` (integration 15368, non-strict). pytest in CI, a Python matrix, SHA pinning or Dependabot, and the Makefile `build` fix (already done in #24).

## Risks


- The job id `validate` becomes the required-check context once Phase 2 is applied, and renaming it later breaks merges.
- The workflow's steps are a hand copy of `validation.commands`, and the docs record that the two change together.

## Progress

PR: #27

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles.

### Phase 1: Workflow and docs

- [x] 1.1 Add the CI workflow with the validate job — 2e3e3d9
- [x] 1.2 Prove validate fails on a gate finding — b99c760 (red run 35986847346), reverted 4506cfa
- [x] 1.3 Replace the CI row in AGENTS.md — 4a8cc72
- [x] 1.4 Document the workflow in the SDLC.md validation gate — 6bc5f1e
