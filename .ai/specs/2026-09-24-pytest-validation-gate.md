# Run pytest in the validation gate and the validate CI job

Tracking issue: #30 (follow-up from #26, Q1)

## 📝 TLDR

Maintainers and the agent pipeline rely on the validation gate and the required `validate` check to keep `main` green. Today neither runs the test suite, so a PR that breaks one of the 9 tests in `mcp_server_bwt/test_*.py` can pass `validate` and merge. This spec proposes adding one pytest command to `validation.commands` and, as its own step, to the existing `validate` job, with the gate docs in `AGENTS.md` and `SDLC.md` updated in the same change.

## 📝 Problem Statement

- `.ai/agentic.config.json` → `validation.commands` and `.github/workflows/ci.yml` (job `validate`, #27) run ruff, ruff format, mypy, `uv build` and an import smoke test, but not pytest. Tests run only through `make test`, locally, when someone remembers to.
- The CI spec (`.ai/specs/2026-09-23-ci-validation-workflow.md`, Q1) deferred this on purpose so that the gate contract would change in one reviewable step. This spec is that step.
- The `AGENTS.md` Tests row still carries `TODO: add pytest to the validation gate.`

Evidence the command is ready: at `bef094d`, `BING_WEBMASTER_API_KEY=dummy uv run pytest mcp_server_bwt --doctest-modules` passes (9 passed, about 1.3 s).

## 📝 Proposed Solution

Add one gate command, the fifth, after `uv build`:

```
BING_WEBMASTER_API_KEY=dummy uv run pytest mcp_server_bwt --doctest-modules
```

- **`--doctest-modules`** matches `make test` and the `AGENTS.md` Tests row, so CI collects exactly what developers run locally. It also imports every module, including `main.py`, which reads the API key at import time. That's why the gate needs the dummy key: without it, collection fails with `ValueError: BING_WEBMASTER_API_KEY environment variable is required`. Without `--doctest-modules` the tests happen to pass keyless today, because they monkeypatch the key. The gate keeps the key anyway so it doesn't depend on that.
- **The key has a fixed value.** `make test` uses `${BING_WEBMASTER_API_KEY:-dummy}`, which would pick up a developer's real key. The gate and CI always use `dummy`, so no real credential can reach a test run and results don't depend on the environment.
- **No `--junitxml`.** The report file `make test` writes is a local artifact that nothing in CI consumes.
- **Placement:** in the gate, after `uv build`. The cheap static checks fail first, and the gate lists stay append-only. In CI, the new step goes after `uv build` and before the import smoke test, keeping the gate order. The smoke test stays: it's a separate import check that isn't part of `validation.commands`.

CI step, in the existing `validate` job (the job id stays, because it's the required check on `main`):

```yaml
      - name: Tests
        env:
          BING_WEBMASTER_API_KEY: dummy
        run: uv run pytest mcp_server_bwt --doctest-modules
```

The key goes in `env:`, as the smoke test already does it, rather than an inline shell prefix. The effective command is identical to the gate entry.

**Alternatives considered**

- *Run `make test` in CI and the gate.* It writes `reports/`, and it honors a real key from the environment. Running the command verbatim keeps CI identical to `validation.commands`, the same reasoning as the CI spec.
- *Move `--doctest-modules` (or the env) into `[tool.pytest.ini_options]`.* It's a tidier command line, but it changes `pyproject.toml` and `make test` behavior. That's out of scope for a gate change and can be done later.
- *A separate `test` job.* That would mean a second required check to register on the ruleset. A step in `validate` is enforced by the existing required check with no settings change.

## 📝 Architecture

This is repository infrastructure only. Nothing under `mcp_server_bwt/` changes, and neither does the built wheel.

- Changed: `.ai/agentic.config.json` (`validation.commands` gains one entry), `.github/workflows/ci.yml` (one new step in `validate`), `AGENTS.md` (the Validation gate list gains item 5, the Tests-row TODO is removed, and the CI row mentions the test step), `SDLC.md` (the Validation gate list gains the command).
- The repo settings don't change: `validate` is already required on the `main` ruleset, so the new step is enforced as soon as the workflow change merges.
- Consumers: every `om-*` skill that runs `validation.commands` (om-fix, om-auto-create-pr, om-check-and-commit, om-code-review) picks up the new command automatically. `lefthook.yml` is unchanged: its hooks don't replace the gate, and adding tests to pre-push is a separate decision.

## 📝 Edge Cases & Failure Scenarios

- **A real key in the environment.** It's overridden by `dummy` in both the gate and CI, so no network call is authenticated with a real credential. The tests don't call the Bing API.
- **Tests that need the network in future.** They would fail in CI. That's intended, and they should be mocked. It's out of scope here.
- **Test collection error (import-time failure).** pytest exits non-zero, so the `Tests` step fails red and the log names it. This overlaps the smoke test, which stays as a cheaper and more explicit signal.
- **Open PRs branched before this merges.** Their `validate` runs use the workflow from the PR's merge ref, so they gain the test step once they merge or update from `main`. No PR gets stuck, because the check name is unchanged.
- **Runtime.** It adds about 2 s to a 1–2 minute job.

## 📝 Risks & Impact Review

- **Gate contract change.** Every future PR must now keep the suite green. That's the point. Rollback: remove the one command and the one step, which takes effect on the next run.
- **Drift between the three lists.** This is handled as the CI spec handled it: `validation.commands`, the `ci.yml` steps, and the `AGENTS.md`/`SDLC.md` lists change together in this PR, and the check in Step 4 diffs them.
- **No protected surface changes** (`BACKWARD_COMPATIBILITY.md`: tool names, schemas and the launch contract are untouched).

## 📝 Resolved assumptions (autonomous defaults)

| # | Question | Default applied | Rationale |
|---|---|---|---|
| Q1 | Should the gate command include `--doctest-modules`, which the issue's example omits? | **Yes.** | It matches `make test` and the `AGENTS.md` Tests row, so CI collects what developers run. There are no doctests today, so the only effect is importing all modules, which the dummy key already covers. It's reversible by dropping the flag. |
| Q2 | Fixed `dummy` key or `${BING_WEBMASTER_API_KEY:-dummy}` as in `make test`? | **Fixed `dummy`.** | A real credential can never reach a gate run, and results don't depend on the environment. |
| Q3 | Add the tests to the lefthook pre-push hook too? | **No, defer.** | The issue scopes the change to the gate and CI. The hooks explicitly don't replace the gate. |
| Q4 | Keep the import smoke test now that pytest collection imports `main.py`? | **Keep it.** | It's out of scope to remove, it's cheap, and it gives a clearer failure than a collection error. |

None of these weakens security or a compatibility contract, so none is marked `⚠ NEEDS HUMAN CONFIRMATION`.

## 📋 Implementation Plan

### Phase 1: Gate, CI step and docs (one PR, `Closes #30`)

1. Append `BING_WEBMASTER_API_KEY=dummy uv run pytest mcp_server_bwt --doctest-modules` to `validation.commands` in `.ai/agentic.config.json`. Check: `python -m json.tool .ai/agentic.config.json` succeeds and the command passes locally.
2. Add the `Tests` step (with `env: BING_WEBMASTER_API_KEY: dummy`) to `.github/workflows/ci.yml` after `uv build` and before the import smoke test, without renaming the `validate` job. Check: `uv run --with check-jsonschema check-jsonschema --builtin-schema vendor.github-workflows .github/workflows/ci.yml` passes, and the PR's `validate` run is green and shows the `Tests` step.
3. Update `AGENTS.md`: add item 5 to the Validation gate list, remove the Tests-row TODO (the row should say the suite runs in the gate and in CI), and mention the test step in the CI row. Also add the command to `SDLC.md` → Validation gate and update its sentence about what CI runs. Check: Step 4.
4. Consistency check: the command lists in `validation.commands`, the `ci.yml` `run:` steps (with the env key applied), `AGENTS.md` and `SDLC.md` match exactly and in the same order. Check: grep or diff the four lists. The full gate passes locally.
5. Negative evidence: on a throwaway commit pushed to the PR branch (reverted before merge), break an assertion in one test and confirm that `validate` fails at the `Tests` step. Check: the red run URL and the green run URL are both linked in the PR, and `git diff origin/main...HEAD --stat` shows no file under `mcp_server_bwt/`, so the break was reverted.

**Non-goals:** a pytest config refactor in `pyproject.toml`, lefthook changes (Q3), removing the smoke test (Q4), coverage reporting, and a Python matrix.
