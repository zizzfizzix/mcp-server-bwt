# Run pytest in the lefthook pre-push hook

Tracking issue: #36 (follow-up from #34, Q3)

## 📝 TLDR

Contributors and the agent pipeline learn about a broken test only when CI's `validate` job fails, after the push. This spec proposes that `lefthook.yml` will run the gate's pytest command as a **pre-push** job, in parallel with mypy, whenever the pushed commits change a `*.py` file. At about 2 s, the suite is too slow for pre-commit, where the rule is under about 1 s, but cheap enough for pre-push.

## 📝 Problem Statement

- #35 added `BING_WEBMASTER_API_KEY=dummy uv run pytest mcp_server_bwt --doctest-modules` to `validation.commands` and to the `validate` CI job. The pytest-gate spec (`.ai/specs/2026-09-24-pytest-validation-gate.md`, Q3) deliberately left `lefthook.yml` unchanged.
- Today `pre-push` runs only `mypy --strict` and, for dependency files, `uv lock --check` (`lefthook.yml`, #18). A push that breaks a test reaches the remote and fails CI 1–2 minutes later.

Measured at `2d14ae0` (2026-09-24, warm uv cache, 2 vCPU, 9 tests, 3 runs):

| Command | Wall time |
|---|---|
| `BING_WEBMASTER_API_KEY=dummy uv run pytest mcp_server_bwt --doctest-modules` | 2.00–2.10 s (pytest reports 1.2–1.3 s) |
| `uv run mypy --strict mcp_server_bwt/` (already in pre-push) | 0.39 s |
| `uv run ruff check mcp_server_bwt/` (pre-commit) | 0.04 s |

These times confirm the numbers in the issue: 2 s is over the 1 s pre-commit rule, so the job goes in **pre-push**.

## 📝 Proposed Solution

Add one job to the existing parallel `pre-push` block:

```yaml
    - name: pytest
      glob: "*.py"
      env:
        BING_WEBMASTER_API_KEY: dummy
      run: uv run pytest mcp_server_bwt --doctest-modules
```

- **Same command as the gate.** With the `env:` key applied, the job runs the 5th entry of `validation.commands` exactly. The key goes in lefthook `env:`, just as the CI `Tests` step sets it, not as an inline shell prefix. The value is fixed at `dummy` and overrides a developer's real key, for the reason given in the gate spec's Q2: a real credential never reaches a test run.
- **`glob: "*.py"`.** On pre-push, lefthook matches the glob against the files changed in the pushed commits (see the existing comment in `lefthook.yml`). A docs-only or workflow-only push skips the job. This is the same `*.py` pattern the pre-commit ruff job already uses to match `mcp_server_bwt/**`.
- **Parallel with mypy.** The block is already `parallel: true`, and both jobs are read-only, so the hook's wall time is set by pytest (about 2 s), not by the sum of the jobs.
- **No `{push_files}` argument.** The whole suite runs, so a change to a module is tested by tests in other files.

**Alternatives considered**

- *pre-commit.* The suite takes about 2 s, which breaks the 1 s rule for per-commit checks. It would also run on every WIP commit. Revisit if the suite drops well under 1 s.
- *`make test`.* It writes `reports/`, and it honors a real key from the environment. The hook uses the gate command verbatim instead, which is the same reasoning the gate spec gives.
- *Run only the tests next to the pushed files.* That would miss tests elsewhere that exercise the changed code. The full suite is fast enough to run in full.

## 📝 Architecture

This is repository tooling only. Nothing under `mcp_server_bwt/` changes, and neither does the built wheel.

- Changed: `lefthook.yml` (one `pre-push` job), and the `AGENTS.md` Tooling row, which says pre-push also runs pytest when `*.py` files are pushed.
- Unchanged: `validation.commands`, `.github/workflows/ci.yml`, `SDLC.md`. The hooks still don't replace the gate or CI, which remains the backstop that `--no-verify` can't bypass.
- Installation: no change. `make install` already runs `lefthook install`. Existing clones pick up the new job without reinstalling, because the `.git/hooks` shim reads `lefthook.yml` on every run.

## 📝 Edge Cases & Failure Scenarios

- **Broken test.** pytest exits non-zero, lefthook prints the pytest output and aborts the push. Nothing reaches the remote.
- **Bypass.** `git push --no-verify` and `LEFTHOOK=0` skip every hook, including this one. They stay documented as the escape hatch, and CI still catches the failure.
- **A real key in the environment.** It's overridden by `dummy` inside the job. The tests don't call the Bing API.
- **A branch's first push.** lefthook diffs against the local default branch, so the job runs if the branch changes any `*.py` file.
- **Tag pushes and branch deletions.** No changed files, so the job is skipped.
- **Deps-only push** (`pyproject.toml`/`uv.lock` without `.py` changes). The job is skipped, and CI runs the tests. See Q2.
- **A future slow suite.** The hook's cost grows with the suite. The stage rule is recorded in the Resolved assumptions, so the decision can be re-measured later instead of re-argued.

## 📝 Risks & Impact Review

- Local developer-experience change only. It adds about 2 s to a push that changes Python files. Rollback: delete the job from `lefthook.yml`, which takes effect on the next push without reinstalling.
- No protected surface changes (`BACKWARD_COMPATIBILITY.md`: tool names, schemas and the launch contract are untouched).
- **Shared hooks hazard.** `lefthook install` and hook runs in a linked worktree use the shared `.git/hooks` of the common git dir. Implementation evidence must be produced in a throwaway clone under `/tmp`, never by installing hooks in the main checkout.

## 📝 Resolved assumptions (autonomous defaults)

| # | Question | Default applied | Rationale |
|---|---|---|---|
| Q1 | pre-commit or pre-push? | **pre-push.** | The measured time is 2.0–2.1 s, above the issue's 1 s pre-commit rule. The issue names pre-push at this runtime. |
| Q2 | Should the glob also match `pyproject.toml` / `uv.lock`, since a dependency bump can break tests? | **No, only `*.py`,** as the issue specifies. | This is the smallest scope. Dependency changes arrive through PRs, where CI runs the tests. Widening the glob later is a one-line change. |
| Q3 | Pass `{push_files}` so only affected tests run? | **No, run the whole suite.** | At about 2 s, selecting tests saves nothing, and selecting by file misses cross-file coverage. |

None of these weakens security or a compatibility contract, so none is marked `⚠ NEEDS HUMAN CONFIRMATION`.

## 📋 Implementation Plan

### Phase 1: pre-push pytest job (one PR, `Closes #36`)

1. Re-measure the suite: run `BING_WEBMASTER_API_KEY=dummy uv run pytest mcp_server_bwt --doctest-modules` and `uv run mypy --strict mcp_server_bwt/` 3 times each, and record the wall times on the PR. If pytest takes under 0.5 s wall, stop and revisit Q1. Otherwise continue with pre-push. Check: the numbers are in the PR body.
2. Add the `pytest` job (`glob: "*.py"`, `env: BING_WEBMASTER_API_KEY: dummy`, `run: uv run pytest mcp_server_bwt --doctest-modules`) to the `pre-push` block in `lefthook.yml`, after mypy. Check: `uv run lefthook validate` passes, and `uv run lefthook dump` shows the job under `pre-push`.
3. Update the `AGENTS.md` Tooling row: pre-push also runs the gate's pytest command when `*.py` files are pushed, in parallel with mypy, and `--no-verify` / `LEFTHOOK=0` still skip it. Check: the row's wording matches `lefthook.yml`.
4. Evidence, in a throwaway clone under `/tmp` with a local bare remote (never in the shared checkout): after `uv sync && uv run lefthook install`,
   - pushing a `.py` change with a passing suite succeeds, and the `pytest` job runs.
   - pushing a deliberately broken assertion is blocked by the `pytest` job.
   - pushing a docs-only change skips the `pytest` job.
   - `git push --no-verify` with the broken test goes through.

   Check: the hook output excerpts are on the PR.
5. Run the full validation gate. Check: all 5 commands pass. `git diff origin/main...HEAD --stat` touches only `lefthook.yml`, `AGENTS.md` and this spec's references.

**Non-goals:** changing the pre-commit hook, changing `validation.commands` or CI, pytest configuration in `pyproject.toml`, and test selection by changed file.
