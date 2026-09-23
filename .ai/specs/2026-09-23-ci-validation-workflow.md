# CI workflow running the validation gate, required on main

Tracking issue: #11

## 📝 TLDR

Maintainers and the agent pipeline need something that enforces the validation gate on every PR. Today it runs only when someone remembers to run it locally, and the `main` ruleset requires no status checks. This spec proposes a GitHub Actions workflow, `.github/workflows/ci.yml`, whose single job `validate` will run the four gate commands plus an import smoke test on every PR and every push to `main`. The `main` ruleset will then list `validate` as a required check, so a red PR can't merge.

## 📝 Problem Statement

- There is no `.github/workflows/` on `main`. `AGENTS.md` lists `CI | none`, and the gate in `AGENTS.md` / `SDLC.md` / `.ai/agentic.config.json` is manual.
- The `main` ruleset (ID 12497565) has `deletion`, `non_fast_forward`, `pull_request` and `required_linear_history` rules, but no `required_status_checks`. Nothing stops a red PR from merging.
- `SDLC.md` → "Reporting is decoupled from CI" assumes that "required checks still gate every merge". That's false today.
- #8 (a fresh install resolved mcp 2.x and the server failed on import) would have been caught by a CI import check.

The prerequisites have landed. #8 and #14 committed `uv.lock` and moved to mcp 2.x, and #9 fixed the ruff findings. At `f8180e6` all four gate commands and the import smoke test pass locally. The issue's Makefile item (`make build` → `uv build`) was already fixed by #24 and is out of scope here.

## 📝 Proposed Solution

A single workflow file with one job:

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  validate:            # the job id is the required-check context: never rename it
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v10
        with:
          enable-cache: true
      - run: uv sync --locked          # uv installs the Python from .python-version (3.13.2)
      - run: uv run ruff check mcp_server_bwt/
      - run: uv run ruff format --check mcp_server_bwt/
      - run: uv run mypy --strict mcp_server_bwt/
      - run: uv build
      - name: Import smoke test
        env:
          BING_WEBMASTER_API_KEY: dummy
        run: uv run python -c "import mcp_server_bwt.main"
```

- **One step per gate command, in gate order.** A failure names the command, so the log answers "which gate?" without scrolling. Steps stop at the first failure, the same as the local gate.
- **Python comes from `.python-version`.** `uv sync` reads it and provisions a managed interpreter, so there's no `actions/setup-python` step and no second source of truth for the version.
- **`uv sync --locked`** fails when `uv.lock` is out of date with `pyproject.toml`. That enforces the lockfile rule in `AGENTS.md` (Dependencies row).
- **Actions are pinned to their current major tags** (`actions/checkout@v7`, `astral-sh/setup-uv@v10`, the latest releases at spec time), matching the `@v4` tag style of the release-please workflow in #22. Before committing, the implementer checks that those majors are still current.
- **Required check.** After the workflow has merged and run once on `main`, the `main` ruleset gets a `required_status_checks` rule with context `validate`, bound to the GitHub Actions app (integration id `15368`) so another app can't post a status with the same name. `strict_required_status_checks_policy` stays `false`: requiring the branch to be up to date would force a rebase on every merge, and linear history plus squash merges already keep `main` coherent.

**Alternatives considered**

- *Run `make` targets in CI.* `make lint` runs `ruff --fix` and changes files (AGENTS.md), and the Makefile has no gate target. Running the gate commands verbatim keeps CI identical to `.ai/agentic.config.json`.
- *A Python version matrix.* `requires-python` is `>=3.13` and `.python-version` pins 3.13.2, so a matrix adds CI minutes without a supported-version question behind it. We can add one when a second version is supported.
- *Separate jobs per gate command.* Each job repeats checkout, setup and sync, and the result is several required checks to keep in sync. One job with named steps gives the same diagnosability.
- *SHA-pinned actions.* That's stronger supply-chain hygiene, but without Dependabot/Renovate the pins go stale, and the repo convention (#22) is major tags. Deferred (see Resolved assumptions).

## 📝 Architecture

This is repository infrastructure only. No file under `mcp_server_bwt/` changes, and neither does the built wheel.

- New: `.github/workflows/ci.yml`.
- Changed: `AGENTS.md` (the CI row), `SDLC.md` (the Validation gate section).
- Repo settings (not a file): the `main` ruleset gains `required_status_checks`. It ships in the same spec rather than a separate one because it can't work without the workflow. It's staged as a separate post-merge phase because it's a different actor and a different kind of change.
- Neighbours: `lefthook.yml` (local hooks, #18) runs a subset of the gate before commit and push, and CI is the backstop that can't be bypassed with `--no-verify`. `release-please.yml` (#22, open) shares the `.github/workflows/` directory and interacts with the required check (see Edge Cases).

`.ai/agentic.config.json` → `validation.commands` stays the source of truth for the gate. The workflow duplicates the list by hand, and `SDLC.md` gets a sentence that the two change together.

## 📝 Edge Cases & Failure Scenarios

- **Ruleset applied before the workflow is on `main`.** Every open PR whose merge ref lacks `ci.yml` (#5, #7, #20, #22) would wait forever on a `validate` check that never reports. Apply the ruleset only after this PR merges. Those PRs then pick up the check on their next push or merge-base update.
- **Release-please PRs (#22).** PRs opened with the default `GITHUB_TOKEN` don't trigger other workflows, so a release PR would never get `validate` and couldn't merge. #22 already plans a `RELEASE_PLEASE_TOKEN` secret for this. Setting it is a maintainer task, tracked on #22, and doesn't block this spec.
- **Fork PRs.** `pull_request` runs with a read-only token and no secrets. The job needs neither, because the smoke test uses a dummy key.
- **Cache poisoning / stale cache.** The setup-uv cache is keyed on `uv.lock`, and a cache miss only costs time. No secret ever enters the cache.
- **Flaky network during `uv sync`.** The step fails red and a re-run fixes it. There's no retry logic, because a hidden retry would mask a real resolution failure.
- **Docs-only PRs.** The required check must always report, so there are deliberately no `paths:` filters. A filtered-out required check stays "expected" and blocks the merge.
- **Renaming the job.** Changing `validate` silently breaks the required check (the PR waits on the old name). The comment in the workflow and the AGENTS.md row call this out.
- **Admin bypass.** The ruleset has no bypass actors today, so the check binds maintainers too. That's intended. Emergency merges go through a temporary ruleset edit, which is audited.

## 📝 Risks & Impact Review

- **Merge-gate change (hard to notice when wrong).** A mis-scoped context or integration id makes every PR unmergeable. Rollback: delete the `required_status_checks` rule from the ruleset, which takes effect immediately.
- **Outward-facing admin action.** Editing the ruleset changes repository settings, not code. It's done after merge, by the maintainer or by an agent with explicit maintainer approval, never as an unattended step of the implementation run.
- **Cost:** one ubuntu job of roughly 1–2 minutes per PR push and per `main` push. Public-repo Actions minutes are free.
- **Drift:** the workflow's command list is a hand copy of `validation.commands`. `SDLC.md` documents that they change together, and the review checklist catches a diff that touches one without the other.

## 📝 Resolved assumptions (autonomous defaults)

| # | Question | Default applied | Rationale |
|---|---|---|---|
| Q1 | Tests now exist (`mcp_server_bwt/test_*.py`, 9 passing). Should pytest join CI in this change? | **No, defer.** CI runs the four gate commands plus the import smoke test only. | The issue says to add pytest to the workflow and `validation.commands` together, and changing the gate contract is a separate, reviewable decision. A follow-up issue can add `BING_WEBMASTER_API_KEY=dummy uv run pytest mcp_server_bwt` to both. |
| Q2 | Who applies the ruleset change, and when? | **After merge, by the maintainer or by an agent with explicit approval**, via Settings → Rules or `gh api -X PUT repos/{owner}/{repo}/rulesets/12497565`. | It's a repository-settings change outside the diff. Applying it before merge would block every open PR. |
| Q3 | Pin actions by SHA or by major tag? | **Major tag** (`@v7`, `@v10`). | Matches the #22 convention and needs no update bot. SHA pinning plus Dependabot can follow separately. |
| Q4 | Require branches to be up to date before merging (strict policy)? | **No.** | Squash merges with linear history keep `main` coherent. Strict mode forces a re-run and rebase for every merge. It can be turned on later with a single toggle. |
| Q5 | Python version matrix? | **No**, single 3.13 from `.python-version`. | There's only one supported version today. |

None of these defaults weaken security or a compatibility contract, so none is marked `⚠ NEEDS HUMAN CONFIRMATION`.

## 📋 Implementation Plan

### Phase 1: Workflow and docs (one PR)

1. Create `.github/workflows/ci.yml` as in Proposed Solution. First confirm that `actions/checkout` and `astral-sh/setup-uv` are still on the major versions listed. Check: `uv run --with check-jsonschema check-jsonschema --builtin-schema vendor.github-workflows .github/workflows/ci.yml` passes (or `actionlint` when available), and the PR shows a green `validate` check whose log lists all eight steps (checkout, setup-uv, sync, the four gate commands, the smoke test).
2. Negative check (on a throwaway branch or commit, reverted before merge, or recorded as CI evidence on the PR): introduce a ruff finding and confirm that `validate` fails at the `ruff check` step. Check: a red run URL is linked in the PR.
3. Update `AGENTS.md`: replace the `CI | none` row with the workflow path, the job name `validate` (required on `main`, so never rename it), the trigger events, and a note that the step list mirrors `validation.commands`. Check: every path, job name and trigger the row names matches `ci.yml` (grep them), and the four gate commands still pass locally.
4. Update `SDLC.md` → Validation gate: say that `.github/workflows/ci.yml` (job `validate`) runs the gate plus the import smoke test on every PR and push to `main`, that `validate` is a required check on `main`, and that the workflow steps, `validation.commands` and this section change together. Check: the command list in the section matches `validation.commands` and the `run:` steps in `ci.yml` exactly (diff the three lists).

### Phase 2: Require the check on main (post-merge, maintainer-approved)

5. After Phase 1 merges and `validate` has run green on `main`, confirm the reporting app: `gh api repos/{owner}/{repo}/commits/main/check-runs -q '.check_runs[] | select(.name=="validate") | .app.id'` must print `15368` (use whatever it prints). Then add to ruleset 12497565 a `required_status_checks` rule with `required_status_checks: [{context: "validate", integration_id: 15368}]` and `strict_required_status_checks_policy: false`, keeping every existing rule. Check: `gh api repos/{owner}/{repo}/rulesets/12497565` lists the rule, and a PR with a failing `validate` shows "Merging is blocked".
6. Comment on #11 with the ruleset evidence and close it.

**Non-goals:** pytest in CI (Q1), a Python matrix (Q5), SHA pinning or Dependabot (Q3), release automation (#16 / #22), and the Makefile `build` fix (already done in #24).
