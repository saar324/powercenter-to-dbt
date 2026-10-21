# Agent mistakes and corrections

Converter implementation has not started. One setup-stage agent mistake is recorded below. This is a real command failure, not a converter-logic defect.

The assignment requires an actual example. Add it when an error is observed. Do not invent one to fill this file.

For each entry, record:

- What the agent proposed or implemented.
- What was incorrect, with a file, diff, or concrete behaviour.
- How the error was detected: test, data comparison, source inspection, or human review.
- The correction and the check that verified it.
- Relevant prompt, BMAD record, and commit links.

An unresolved assumption or a reference mismatch is not automatically an agent mistake.

## SETUP-001 — Wrong uv lock mode for a BMAD helper

- **Agent action:** the first verification command and draft CI step used `uv run --locked --all-groups _bmad/scripts/resolve_config.py`.
- **Error:** this BMAD helper has inline Python-script metadata. uv treated it as a separate script environment and required a script-specific lockfile. The project's `uv.lock` did not satisfy that mode.
- **Detection:** the local command exited with `Unable to find lockfile for Python script, but --locked was provided`.
- **Correction:** the CI step now uses `uv run --locked --all-groups python _bmad/scripts/resolve_config.py`, so the helper runs inside the locked project environment. BMAD's own documented command, without `--locked`, is checked separately.
- **Verification:** see `docs/evidence/setup-verification.md` for the actual readback results. No converter behaviour was involved.
