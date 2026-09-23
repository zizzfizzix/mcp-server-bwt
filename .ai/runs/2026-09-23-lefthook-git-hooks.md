# Execution plan: git hooks via lefthook

Source doc: .ai/specs/2026-09-23-lefthook-git-hooks.md (spec PR #21)
Issue: #18

## Goal

Run the fast validation-gate commands automatically as git hooks. `pre-commit` should ruff-fix and restage staged `*.py` files. `pre-push` should run `mypy --strict`, plus `uv lock --check` when dependency files are pushed. `make install` should install the hooks.

## Scope

`pyproject.toml` (dev group), `uv.lock`, a new `lefthook.yml`, `Makefile` (`install`), `AGENTS.md`, and `README.md`. No runtime code changes.

**Non-goals:** `uv build` or pytest in hooks, changes to the gate commands, CI (#11), and commit-message linting.

## Verification

I checked everything in a fresh clone with lefthook 2.1.14:
- Fixable drift is fixed and committed.
- An unfixable finding fails the commit and names the file.
- Non-Python commits skip ruff.
- A partially staged file keeps its unstaged hunks.
- A mypy error fails the push, on the first push and on later pushes.
- A stale lockfile fails the push.
- `--no-verify` and `LEFTHOOK=0` bypass the hooks.

`lefthook run pre-commit --all-files` passes, and the four gate commands are green.

## Risks

- `stage_fixed` has to be set on each sub-job of the piped group. Set on the group, it silently commits unfixed content (see the spec).
- pre-push file detection uses `@{push}`, or on a branch's first push the local default branch. When lefthook finds no changed files, it skips the pre-push jobs. That's harmless, but the hooks are a convenience and CI (#11) stays the enforcing gate.
- Hooks install into the shared `.git/hooks`, so linked worktrees get them too. That's intended.

## Progress

PR: #23

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles.

### Phase 1: Hooks, installation, and docs

- [x] 1.1 Add lefthook to the dev dependency group and relock — 1f79d8f
- [x] 1.2 Add lefthook.yml with pre-commit and pre-push jobs — 6f13b56
- [x] 1.3 Install hooks from make install — 2ad5a68
- [x] 1.4 Document hooks in AGENTS.md and README.md — 4d115f8
- [x] 1.5 Verify the done-when list and run the gate — 822c341
