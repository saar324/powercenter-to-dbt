# Development process

## Current state

The repository, source materials, and BMAD development environment are prepared. No product specification, approved support matrix, converter implementation, or product acceptance result exists yet.

## Selected method

Use BMAD Method 6.12.4, with its core and BMM modules, integrated with Codex. The exact npm version is pinned. The installed skill sources are committed so reviewers can inspect the workflow instructions used.

Official stable documentation: https://github.com/bmad-code-org/BMAD-METHOD/tree/V6.12/docs

The npm setup overrides BMAD's transitive `csv-parse` dependency to version 7.0.2, which fixes advisory [GHSA-8cw4-87c7-c6xx](https://github.com/advisories/GHSA-8cw4-87c7-c6xx). BMAD itself remains pinned to 6.12.4. Installer compatibility is checked during setup; this override does not alter the committed workflow instructions.

Only the method has been selected. The following sequence is a proposed starting process; it is not evidence that those workflows have run.

1. Use `bmad-spec` to turn the assignment and sample findings into a short specification. Resolve supported transformations, output behaviour, error handling, and observable acceptance criteria.
2. Record the small technical design needed by the converter. Use `bmad-architecture` if its workflow is useful. Keep the effort within the exercise's time budget.
3. Ask `bmad-spec` for Story Breakdown if the agreed scope needs several implementation units. Review the story order and checkpoints.
4. Use `bmad-build` for each agreed unit. Keep implementation, meaningful tests, review findings, and corrections traceable.
5. Run the complete local command-line flow and semantic SQL checks. Review supported and unsupported cases together.
6. Use `bmad-retrospective` for the combined result when appropriate. Complete the README and evidence before submission.

No UI, hosted service, production deployment, paid service, or cloud database is required by the brief. Python, pytest, Ruff, and dbt with local DuckDB are the prepared development tools; product dependencies can be added after the design is settled.

## Evidence rules

- Preserve actual prompts and material decisions as work happens.
- Keep BMAD specifications, memory logs, story records, reviews, and retrospectives under `_bmad-output/`.
- Keep an observed agent-error record in `docs/agent/mistakes.md`. Do not invent a mistake or relabel an open question as a proven error.
- Record commands, outcomes, failures, and remaining uncertainty. Tool availability is not product verification.
- Use independently defined expected behaviour. Passing tests based on the same incorrect assumption as the implementation are insufficient.
- Prefer small commits that show planning, implementation, tests, and correction in their actual sequence.

## Handoff to a new coding session

Open this directory as the project root. Read `AGENTS.md`, `docs/assignment.md`, `docs/sample-findings.md`, and `docs/open-decisions.md`. Then invoke the installed `bmad-spec` skill with `docs/agent/starting-prompt.md` as its input. The prepared prompt is intentionally not executed during repository setup.
