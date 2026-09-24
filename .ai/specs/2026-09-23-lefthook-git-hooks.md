# Git hooks via lefthook running the validation gate locally

Tracking issue: #18

## 📝 TLDR

Contributors (humans and the agent pipeline) run the validation gate in `AGENTS.md` only when they remember to, so lint and format drift (#9) reaches commits. This spec proposes that a committed `lefthook.yml` will run the fast gate commands as git hooks: `pre-commit` will auto-fix and restage ruff findings on staged Python files, and `pre-push` will run `mypy --strict` plus `uv lock --check` when dependency files changed. `make install` will install the hooks.

## 📝 Problem Statement

- The gate (`AGENTS.md` → Validation gate) is manual. There is no CI yet (#11), so nothing enforces it before review.
- #9 was a ruff drift that landed because nobody ran `ruff check` before committing. A pre-commit fix would have caught it.
- The pipeline's own agents commit through `git commit`, so hooks cover them too, without any skill needing a change.

## 📝 Proposed Solution

Add [lefthook](https://lefthook.dev) as a dev dependency (`[dependency-groups].dev`). The PyPI package ships the prebuilt binary, so contributors need no Go or npm. A root `lefthook.yml` reuses the exact gate commands through `uv run`.

| Hook | Job | Command | Filter |
|---|---|---|---|
| `pre-commit` | ruff (fix, then format) | `uv run ruff check --fix {staged_files}` then `uv run ruff format {staged_files}` | `glob: "*.py"` (matches nested paths), `stage_fixed: true` on each sub-job |
| `pre-push` | mypy | `uv run mypy --strict mcp_server_bwt/` | always |
| `pre-push` | lockfile | `uv lock --check` | `glob: ["pyproject.toml", "uv.lock"]` over the pushed files |

`ruff check --fix` and `ruff format` run **sequentially** in one piped group, so the two never write the same file at the same time. `stage_fixed: true` has to go on each sub-job. Set on the parent group, it does nothing: in a lefthook 2.1.14 check the fix stayed in the working tree and the unfixed content was committed. On pre-push, lefthook matches `glob` against the files in the pushed commits, so the lockfile check needs no `files:` command. The pre-push jobs are read-only, so they can run in parallel.

`make install` becomes `uv sync && uv run lefthook install`.

**Alternatives considered**

- The `pre-commit` framework (maintainer rejected it, see #18). It builds a separate environment per hook, so ruff and mypy versions would drift from `uv.lock`. It also needs a Python bootstrap of its own.
- Hand-written `.git/hooks` scripts. They aren't versioned and they aren't installed on clone, so every contributor maintains a copy.
- Check-only pre-commit, with no auto-fix (maintainer rejected it). It turns fixable drift into a failed commit and a manual re-run.

## 📝 Architecture

This is dev tooling only. No file under `mcp_server_bwt/` changes, and neither does the built wheel.

- New: `lefthook.yml` at the repo root.
- Changed: `pyproject.toml` (the dev group), `uv.lock`, `Makefile` (`install`), `AGENTS.md` (the Tooling and Dependencies rows), `README.md` (a short Development note).
- `lefthook install` writes `.git/hooks/pre-commit` and `.git/hooks/pre-push` shims that call the lefthook binary. In a linked worktree it writes into the shared `.git/hooks` of the common git dir, so one install covers every worktree.

## 📝 Edge Cases & Failure Scenarios

- **An unfixable ruff finding** fails the commit. The output names the file and the rule, and nothing is committed.
- **A partially staged `.py` file**: lefthook hides unstaged hunks while `stage_fixed` jobs run. The staged hunks are fixed and committed, and the unstaged hunks stay unstaged (checked against lefthook 2.1.14). Step 5 re-checks this.
- **Non-Python commits** (docs, Makefile) skip the ruff job because of the glob.
- **Bypass**: `git commit --no-verify`, `git push --no-verify`, and `LEFTHOOK=0` skip every hook, and are documented as the escape hatch.
- **Hooks not installed** (a contributor ran `uv sync` directly): nothing runs, same as today. The README and `AGENTS.md` point at `make install`.
- **mypy failure** blocks the push with mypy's own output.
- **Stale lockfile**: `uv lock --check` fails the push with uv's message. The fix is `uv lock` plus a commit.

## 📝 Risks & Impact Review

- No protected surface in `BACKWARD_COMPATIBILITY.md` is touched. Server users and the published package are unaffected.
- Contributors get one new dev dependency, and their commits and pushes get slower by the time ruff and mypy take (seconds on this codebase).
- Rollback: delete `lefthook.yml`, revert the `Makefile`, and run `uv run lefthook uninstall` (or delete the two hook shims).

## 📋 Implementation Plan

### Phase 1: Hooks, installation, and docs (one PR)

1. Add `lefthook` to `[dependency-groups].dev` in `pyproject.toml`, run `uv lock`, and commit both files. Check: `uv run lefthook version` works.
2. Create `lefthook.yml` with the `pre-commit` and `pre-push` jobs from the table above. Check: `uv run lefthook validate` passes.
3. Change the `Makefile` `install:` target to `uv sync && uv run lefthook install`. Check: after `make install`, `.git/hooks/pre-commit` and `.git/hooks/pre-push` exist and invoke lefthook.
4. Docs: add the hooks and how to skip them to the `AGENTS.md` Tooling row (and lefthook to the Dependencies row), and add a short "Development" note to `README.md`.
5. Verify the done-when list from #18 in a scratch clone: fixable drift is fixed and committed; an unfixable finding fails the commit and names the file; non-Python commits skip ruff; a mypy error fails the push; `--no-verify` and `LEFTHOOK=0` bypass; a partially staged file keeps its unstaged hunks. Then run `uv run lefthook run pre-commit --all-files` and the four gate commands.

**Non-goals:** `uv build` or pytest in hooks, changes to the gate commands, CI (#11), and commit-message linting.
