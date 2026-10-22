# Infinite Lambda take-home exercise

This repository contains the supplied assignment materials, BMAD tooling and current requirements records. Converter implementation has not started.

- [Assignment instructions](docs/assignment.md)
- [Original supplied XML](fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml)
- [Original upstream README](fixtures/powercenter/UPSTREAM_README.md)
- [Source provenance and checksums](fixtures/powercenter/provenance.json)

The task has entered native Build preparation after PRD,architecture,stories and sprint-readiness checks. Saar approved the Python 3.13 command-line stack with uv and pytest/DuckDB/dbt-duckdb validation; the [native stack record](./_bmad-output/specs/spec-powercenter-to-dbt/source-compatibility.md#converter-implementation-stack) contains the choices and rationale. The five-target core, DuckDB output, row-comparison rule and conversion of supported preparation commands are approved in the PRD; engineering verification and the native implementation contract remain pending; Saar approved the consolidated PRD in U64 and the overall architecture in U75. Reusable rules are not limited to five target names. The user has requested measured CSV reporting and a concise validation/next-work summary; their contract is captured below. Removed setup proposals are not approved inputs.

- [Consolidated PRD for review](./_bmad-output/planning-artifacts/prds/prd-powercenter-to-dbt-2026-10-22/prd.md) — approved by Saar in U64; remaining engineering checks are explicit.
- [Pre-approval research and learning notes](research/README.md) — XML walkthrough, Jaffle Shop primer, conversion design, semantic tests and input handling, with primary sources.
- [Reviewed architecture](./_bmad-output/planning-artifacts/architecture/architecture-powercenter-to-dbt-2026-10-22/ARCHITECTURE-SPINE.md) — shared graph, conversion boundaries, output ownership and verification contract.
- [Current native specification](./_bmad-output/specs/spec-powercenter-to-dbt/SPEC.md) — individually approved PRD decisions are reconciled; final PRD signoff is recorded; semantic verification and native implementation preparation remain pending.
- [Source compatibility and reference boundaries](./_bmad-output/specs/spec-powercenter-to-dbt/source-compatibility.md)
- [Validation and reporting contract](./_bmad-output/specs/spec-powercenter-to-dbt/validation-and-reporting.md)
- [Available actual prompts](docs/agent-prompts.md) — curated record with stated omissions, not a full conversation export.

The effort target is about four hours from 16:34 Europe/Sofia on 22 October 2026, including understanding, planning, agent coordination, testing and documentation. Saar clarified in U43 that 20:30 is a target, not a hard cutoff: 20:40 is acceptable, and work in progress can be finished when needed. Keep the effort near four hours and prioritize a complete tested minimum over optional coverage. No converter tests or accuracy measurements have been produced yet. The final submission will add actual converter run instructions, verified limitations and results as they exist; setup commands below are not converter run instructions.

## Tools and agent process

- Coding tool: Codex desktop app.
- Access: Saar's personal Codex 20× plan, as reported by Saar.
- Development workflow: project-local BMAD Method 6.12.4.

The subscription label is recorded separately from the model. Saar described GPT 5.6, high thinking and fast execution in the [prompt record](docs/agent-prompts.md) (U23); these are user-provided settings, not independently captured runtime metadata. Record actual model/settings per run when available.

## BMAD setup

BMAD Method 6.12.4 is installed for Codex in `.agents/skills/` and `_bmad/`.
Native requirements and append-only memory are in `_bmad-output/specs/spec-powercenter-to-dbt/`. Native Build has been entered; product implementation and implementation review have not run yet.

To restore the pinned installer dependencies:

```sh
npm ci --ignore-scripts
```

To reinstall BMAD if needed:

```sh
npm run setup:bmad
```

Open this repository as the coding tool's project root. BMAD's own help is available through the installed `bmad-help` skill.

Assignment documentation is governed by [AGENTS.md](AGENTS.md). Project overrides in `_bmad/custom/` remind Build and the retrospective to maintain the required submission evidence. Existing BMAD records are reused rather than duplicated.

The submission will include the relevant development record: BMAD tooling and shared configuration, requirements and native history, research, prompts, implementation and reviews, tests and measured reports, CI, and dependency manifests and lockfiles. Installed packages, virtual environments, tool caches, credentials and machine-only settings are excluded. Any private third-party context in the conversation is redacted and identified as such.

The repository setup check verifies tooling configuration and unchanged supplied files only.

## Agent error caught during setup

During setup, the coding agent added analysis and proposed implementation choices when I had asked only for repository preparation. I caught this by reviewing the repository files and questioning what had already been added. I asked the agent to remove those additions and the converter-specific scaffolding, keeping the supplied materials and BMAD setup. The cleanup is recorded in commit `270a3d8`. This occurred before converter implementation.

See [third-party notices](THIRD_PARTY_NOTICES.md).
