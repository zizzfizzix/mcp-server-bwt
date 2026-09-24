# Skip the validation gate on release-please PRs

Tracking issue: #31

## 📝 TLDR

#27 made `validate` a required check on every PR, including release-please's `chore(main): release X.Y.Z` PRs. Those PRs only rewrite generated files (`.release-please-manifest.json`, `CHANGELOG.md`, the `__VERSION__` line in `mcp_server_bwt/version.py`), and every commit they describe already passed `validate` on `main`. This spec proposes a job-level `if:` on `validate` that skips the job for same-repo PRs whose head branch starts with `release-please--branches--`. The check then reports *skipped*, which satisfies the required check. Every other PR, and every push to `main`, keeps running the full gate.

## 📝 Problem Statement

- `ci.yml` runs `validate` on every `pull_request`. Release PR #29 (head `release-please--branches--main--components--mcp-server-bwt`, files: the manifest, `CHANGELOG.md`, `mcp_server_bwt/version.py`) spends a runner on a re-validation that adds nothing, and the release has to wait for it.
- The maintainer asked for this on #27: "skip the validations on release please prs".
- This is an efficiency gain, not a fix. #29 is green today in about 23s (`priority-low`).

## 📝 Proposed Solution

Add one condition to the existing job and change nothing else:

```yaml
jobs:
  # The job id is the required-check name on the main ruleset. Never rename it.
  validate:
    # Release-please PRs only touch generated release files built from commits that
    # already passed validate on main, so skip the gate for them. A skipped job still
    # reports the `validate` check, which satisfies the required check. The same-repo
    # guard means a fork can't get a free pass by naming its branch the same way.
    if: >-
      github.event_name != 'pull_request'
      || github.event.pull_request.head.repo.full_name != github.repository
      || !startsWith(github.event.pull_request.head.ref, 'release-please--branches--')
    runs-on: ubuntu-latest
    ...
```

The condition says: run the job unless all three hold (it's a PR event, the head is in this repo, and the head branch has the release-please prefix).

- **Why a job-level `if:`.** When a conditional skips a job, GitHub still creates its check run (conclusion `skipped`), and a skipped check satisfies a required status check. The check keeps its name, `validate`, so ruleset 12497565 (`context: validate`, `integration_id: 15368`) needs no change.
- **Why both guards.** Release PRs are opened with `RELEASE_PLEASE_TOKEN`, which belongs to the maintainer account, so the PR author doesn't distinguish them. The branch prefix alone could be spoofed by a fork. The same-repo check closes that: pushing a branch into this repo already needs write access, and a fork's `head.repo.full_name` never equals `github.repository`.
- **`push` to `main` is unaffected.** `github.event_name != 'pull_request'` is true, so the full gate runs on the merge commit of every release PR too. That run is the backstop.

**Alternatives considered**

- *`paths-ignore` or removing the workflow for release branches.* A filtered-out required check stays "Expected — waiting for status" forever and blocks the merge (AGENTS.md, CI row). Rejected.
- *Step-level `if:` on each gate step.* The job would still run checkout and report *success*. That's six conditions to keep in sync instead of one, plus a runner spin-up. It buys nothing over *skipped*.
- *Skip only when the diff touches just the three release files.* This is stronger, but it needs the job to run and diff the PR, which is most of the cost being removed. It also adds logic for a case (a hand-edited release PR) the maintainer already controls. Deferred (Q2).
- *Match on PR author or label.* The author is the maintainer account (see above), and anyone with triage access can add a label. Both are weaker than branch plus same repo.

## 📝 Architecture

This is repository infrastructure only. Nothing under `mcp_server_bwt/` changes, and neither does the built wheel.

- Changed: `.github/workflows/ci.yml` (one `if:` plus a comment on the `validate` job).
- Changed docs: `AGENTS.md` (CI row) and `SDLC.md` (Validation gate). Both state the exemption and its condition, and both still say never to rename the job.
- Unchanged: `release-please.yml`, `release-please-config.json`, the `main` ruleset, `.ai/agentic.config.json` → `validation.commands` (the gate's command list doesn't change, only when CI runs it).

## 📝 Edge Cases & Failure Scenarios

- **Fork PR with a head branch named `release-please--branches--main`.** `head.repo.full_name` is the fork, so the job runs the full gate. This is the spoofing guard (acceptance criterion 3).
- **A human pushes a commit onto the release branch.** The job still skips, because the condition can't tell who wrote the commit. That's acceptable: pushing needs write access, and the post-merge `push` run on `main` validates the result. `AGENTS.md` already forbids hand-editing the release files. If this becomes a problem, Q2's diff check is the upgrade path.
- **Non-default release branches.** release-please names every branch `release-please--branches--<target>[--components--<name>]`, so the prefix covers any future target branch too.
- **release-please changes its branch naming.** The condition stops matching and release PRs fall back to running the full gate. That fails safe: slower, never an unvalidated merge.
- **Concurrency group.** It's unchanged. A skipped run still joins `ci-${{ github.ref }}`, which is harmless.
- **Ruleset treats skipped as passing.** This is GitHub's documented behavior for conditionally skipped jobs. If it ever changed, release PRs would show `validate` as blocking. You'd see that right away on the release PR, and reverting the `if:` fixes it.

## 📝 Risks & Impact Review

- **Merge gate loosened for one branch family.** The blast radius is branches in this repo named `release-please--branches--*`, which only writers can create, and `main` re-validates after merge. Rollback: delete the `if:` line.
- **Doc drift.** The condition is spelled out in three places (workflow comment, AGENTS.md, SDLC.md). The review checklist catches a diff that changes one without the others.
- **No compatibility surface.** `BACKWARD_COMPATIBILITY.md` covers the MCP tool surface and package metadata, and neither is touched.

## 📝 Resolved assumptions (autonomous defaults)

| # | Question | Default applied | Rationale |
|---|---|---|---|
| Q1 | Job-level `if:` (reports *skipped*) or step-level `if:`s (reports *success*)? | **Job-level.** | It's one condition, no runner, and skipped satisfies the required check. It's also the change the issue specifies. |
| Q2 | Should the skip also require the diff to touch only the three release files? | **No, defer.** | It needs a running job and diff logic, which cancels most of the saving. Same-repo plus branch prefix already needs write access, and `main` re-validates after merge. |
| Q3 | Should the implementation PR prove the skip with a throwaway same-repo `release-please--branches--*` PR before merge? | **No.** Verify on the real release PR (#29) after merge. | Merging the implementation PR pushes to `main`, and release-please then updates #29, which runs the new `ci.yml`. A throwaway PR would be extra outward-facing noise. |

None of these defaults weaken security or a compatibility contract, so none is marked `⚠ NEEDS HUMAN CONFIRMATION`.

## 📋 Implementation Plan

### Phase 1: Workflow condition and docs (one PR)

1. Add the job-level `if:` and its comment to `validate` in `.github/workflows/ci.yml`, exactly as in Proposed Solution. Don't touch the job id, the steps or the triggers. Check: `uv run --with check-jsonschema check-jsonschema --builtin-schema vendor.github-workflows .github/workflows/ci.yml` passes (or `actionlint` when available), and the implementation PR itself (a normal branch) shows `validate` running all its steps green. That's acceptance criterion 2.
2. Update `AGENTS.md`, CI row: `validate` is skipped (it reports *skipped*, which satisfies the required check) on same-repo PRs whose head branch starts with `release-please--branches--`. Fork PRs and pushes to `main` always run the full gate. Keep "never rename the job". Check: the condition wording matches `ci.yml` (grep `release-please--branches--` in all three files).
3. Update `SDLC.md` → Validation gate with the same exemption and condition. Keep the sentence that the workflow steps, `validation.commands` and the section change together. Check: the same grep, and the four gate commands still pass locally.

### Phase 2: Confirm on the real release PR (post-merge)

4. After the implementation PR merges, release-please updates #29 (or opens the next release PR). Check: `gh pr checks <release PR>` shows `validate` as skipped, and `gh pr view <release PR> --json mergeStateStatus` shows `CLEAN` (acceptance criterion 1). Record the evidence on #31.

Acceptance criterion 3 (fork PR named `release-please--branches--main` still runs the full gate) follows from `head.repo.full_name != github.repository` evaluating to true for every fork. It's verified by review of the expression, not by opening a fork PR.

**Non-goals:** diff-based release validation (Q2), changes to the ruleset, release-please configuration, or the gate command list.
