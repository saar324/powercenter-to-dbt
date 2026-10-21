# Project instructions

## Scope and source of truth

- This is the Infinite Lambda PowerCenter-to-dbt take-home exercise. Read `docs/assignment.md` and `docs/sample-findings.md` before planning or implementation.
- Keep the effort proportionate to the approximately four-hour exercise. Prefer a small, correct supported subset with explicit limitations.
- Derive output from XML definitions, instances, connectors, fields, and expressions. Do not hard-code Jaffle Shop table names or expected SQL.
- Preserve the original fixture bytes. Use separate, synthetic fixtures for changed-name, changed-expression, and failure-case tests.
- The linked DuckDB reference and supplied XML have different schemas. Do not change XML meaning to match the reference.

## BMAD workflow

- Use the committed BMAD 6.12.4 skills. Do not upgrade or migrate without a project decision.
- Setup is complete; requirements, implementation scope, and story order remain to be established. Start with `bmad-spec` using `docs/agent/starting-prompt.md` as input. Do not run Build merely because setup is ready.
- Let `bmad-spec` own its generated `SPEC.md` and memory log. Use the skill to update them.
- Keep specifications, story records, review findings, and actual check results in `_bmad-output/`. Do not edit vendor skills to add project policy; use project instructions or `_bmad/custom/` overrides.
- Explain decisions in short, clear English. Define unfamiliar Informatica and dbt terms.

## Verification and evidence

- Use the project Python environment through `uv run`. Python dependencies are locked in `uv.lock`; BMAD tooling is locked in `package-lock.json`.
- Run local dbt commands with `DBT_SEND_ANONYMOUS_USAGE_STATS=false` and `--profiles-dir dbt`. The profile is local DuckDB only. Do not use global warehouse profiles.
- Test generated behaviour against independently defined expected results. Include XML name/expression mutations and relevant unsupported-input cases. Do not rely only on SQL snapshots or test expectations copied from generated SQL.
- Record actual commands, results, failures, and unresolved limitations. Do not claim checks that were not run. No tests collected means the test gate is incomplete.
- Append project user prompts to `docs/agent/prompts.md`. Record observed agent mistakes and how they were detected in `docs/agent/mistakes.md`. Never invent an error to satisfy the brief.
- Keep commits small enough to inspect. Use `codex/` for development branches. Preserve the sequence of planning, implementation, tests, and correction.

## Publication boundary

- Keep private correspondence, the private submission URL, secrets, local paths, and unrelated chat context out of commits and exports.
- Repository preparation does not authorize assignment submission, recruiter messages, visibility changes, or collaborator access changes.
