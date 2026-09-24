# Execution plan: skip the validation gate on release-please PRs

Source doc: .ai/specs/2026-09-24-skip-validate-on-release-prs.md (on spec PR #32)
Issue: #31

## Goal

Skip `validate` on release-please PRs from this repository while the required `validate` check still reports and passes as *skipped*. Every other PR and every push to `main` keeps running the full gate.

## Scope

- `.github/workflows/ci.yml`: add a job-level `if:` and a comment on `validate`.
- `AGENTS.md` (CI row) and `SDLC.md` (Validation gate): document the exemption and its condition.

## Non-goals

- Diff-based release validation (spec Q2).
- Any change to the ruleset, the release-please config, or `validation.commands`.
- Committing the spec itself, which merges through #32.

## Risks

- The skip could match more than release PRs. It's guarded by the same-repo check plus the branch prefix, and `main` re-validates after merge.
- The acceptance check on a real release PR can only happen after merge (spec Phase 2). It's tracked on #31, not as a step here.

## Implementation Plan

### Phase 1: Workflow condition and docs

1. Add the job-level `if:` to `validate` in `ci.yml`, then schema-check the workflow.
2. Document the exemption in the `AGENTS.md` CI row.
3. Document the exemption in the `SDLC.md` Validation gate section.

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles.

### Phase 1: Workflow condition and docs

- [x] 1.1 Add the job-level `if:` to `validate` in `ci.yml` — 1f8e43a
- [x] 1.2 Document the exemption in the `AGENTS.md` CI row — 14a1079
- [x] 1.3 Document the exemption in the `SDLC.md` Validation gate section — dcddad3
