# Execution plan: run pytest in the lefthook pre-push hook

Source doc: .ai/specs/2026-09-24-lefthook-pytest-pre-push.md (spec PR #37)
Issue: #36

## Goal

Add a `pytest` job to the lefthook `pre-push` block. It runs the gate's pytest command with a fixed `BING_WEBMASTER_API_KEY=dummy` set through `env:`, in parallel with mypy, and only when the pushed commits change a `*.py` file. That way a broken test is caught before the push.

## Scope

`lefthook.yml` (one job) and the `AGENTS.md` Tooling row. There are no runtime code changes. The spec file merges through spec PR #37 and isn't committed here.

**Non-goals:** changing pre-commit, `validation.commands`, CI or `pyproject.toml`, and test selection by changed file.

## Risks

- `lefthook install` writes to the shared `.git/hooks`, so the evidence is produced only in a throwaway `/tmp` clone.

## Progress

> Convention: `- [ ]` pending, `- [x]` done. Append ` — <commit sha>` when a step lands. Do not rename step titles.

### Phase 1: pre-push pytest job

- [ ] 1.1 Re-measure the suite runtime
- [ ] 1.2 Add the pytest job to pre-push
- [ ] 1.3 Update the AGENTS.md Tooling row
- [ ] 1.4 Prove the hook in a throwaway clone
- [ ] 1.5 Run the full validation gate
