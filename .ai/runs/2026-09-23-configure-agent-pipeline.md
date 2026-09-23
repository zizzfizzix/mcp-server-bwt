# Execution plan: configure-agent-pipeline

## Goal

Land the agent-pipeline setup that `om-setup-agent-pipeline` produced on `cez/7de2ee3c` (commit `059cbad`) on `main`, so every `om-*` skill finds its config on the base branch.

## Scope

- `.ai/agentic.config.json`: GitHub tracker, agent-browser, validation gate (`ruff check`, `ruff format --check`, `mypy --strict`, `uv build`), full label taxonomy, QA gate off.
- `.ai/trackers/github.md`, `.ai/browsers/agent-browser.md`: the shipped descriptors, unmodified.
- `.ai/{runs,analysis,specs,scripts,qa}/.gitkeep`, plus `.gitignore` entries for per-run QA state.
- `SDLC.md`, `AGENTS.md`, `CODE_REVIEW.md`, `BACKWARD_COMPATIBILITY.md`, all generated from this repository.

## Non-goals

- Code or dependency fixes. The gate is red on `main` today, and that's tracked in #8 (mcp 2.x crash, also addressed by open PR #4) and #9 (ruff 0.16 findings).
- CI workflow and required checks (#11).
- The `self` schema bug (#10, also addressed by open PR #7).

## Implementation Plan

### Phase 1: Land the setup

1. Bring the setup commit `059cbad` onto this branch unchanged (cherry-pick).

### Phase 2: Verify

1. Check that the config parses, that every path it references exists, and that the generated docs contain no unresolved template placeholders. Run the validation gate and record its pre-existing failures.

## Risks

- This is a docs and config change only, with no runtime effect.
- The validation gate fails on `main` for reasons outside this PR (#8, #9). This run records those failures and doesn't fix them.
- The docs describe the process the skills enforce. If the team disagrees with a default (for example the QA gate being off), change it in `.ai/agentic.config.json` and `SDLC.md` together.

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles.

### Phase 1: Land the setup

- [x] 1.1 Cherry-pick the pipeline setup commit — d6ab654

### Phase 2: Verify

- [ ] 2.1 Verify config, paths, docs and run the validation gate
