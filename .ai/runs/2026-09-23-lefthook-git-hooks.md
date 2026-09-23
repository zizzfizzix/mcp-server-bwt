# Execution plan: git hooks via lefthook

Source doc: .ai/specs/2026-09-23-lefthook-git-hooks.md (spec PR #21)
Issue: #18

## Goal

Run the fast validation-gate commands automatically as git hooks. `pre-commit` should ruff-fix and restage staged `*.py` files. `pre-push` should run `mypy --strict`, plus `uv lock --check` when dependency files are pushed. `make install` should install the hooks.

## Scope

`pyproject.toml` (dev group), `uv.lock`, a new `lefthook.yml`, `Makefile` (`install`), `AGENTS.md`, and `README.md`. No runtime code changes.

**Non-goals:** `uv build` or pytest in hooks, changes to the gate commands, CI (#11), and commit-message linting.

## Risks

- `stage_fixed` has to be set on each sub-job of the piped group. Set on the group, it silently commits unfixed content (see the spec).
- Hooks install into the shared `.git/hooks`, so linked worktrees get them too. That's intended.

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles.

### Phase 1: Hooks, installation, and docs

- [ ] 1.1 Add lefthook to the dev dependency group and relock
- [ ] 1.2 Add lefthook.yml with pre-commit and pre-push jobs
- [ ] 1.3 Install hooks from make install
- [ ] 1.4 Document hooks in AGENTS.md and README.md
- [ ] 1.5 Verify the done-when list and run the gate
