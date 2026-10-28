---
id: SPEC-fivetran-source-report
companions:
  - source-report-contract.md
  - ../spec-powercenter-to-dbt/validation-and-reporting.md
sources: []
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# Fivetran source coverage for migration

## Why

Migration from PowerCenter to Fivetran and dbt needs both input data and translated processing rules. The converter currently reports conversion outcomes but does not show which connector types can supply its external inputs. Saar approved a source report to identify connector matches, intermediate inputs and unresolved information.

## Capabilities

- **CAP-1**
  - **intent:** Inventory all source definitions and their uses for migration planning.
  - **success:** The supplied XML produces 12 distinct source definitions with all 28 source uses. Unused definitions, failed or unselected paths and missing metadata remain visible.
- **CAP-2**
  - **intent:** Distinguish external inputs from inputs explicitly assigned to generated producers.
  - **success:** Exact bindings identify producers per source use. Mixed bound/unbound uses remain separate; missing or unsuccessful producers never imply that input data is available.
- **CAP-3**
  - **intent:** Identify potential Fivetran connector types and information still needed for migration.
  - **success:** A documented catalogue supplies evidence for recognized source types. Unknown, missing or conflicting metadata is explicit; connector availability is separate from unverified client compatibility and live configuration.
- **CAP-4**
  - **intent:** Produce a useful report while preserving existing conversion behavior.
  - **success:** Report-only execution covers the whole export without SQL generation. Opt-in conversion output includes the report in the existing atomic publication. Existing conversion SQL, selection and exit statuses remain unchanged.

## Constraints

- Preserve source definition, source use, exported database identifier and session/workflow connection evidence as different facts; exact rules are in `source-report-contract.md`.
- Use explicit bindings. Never infer an intermediate input or physical database identity from names alone.
- Preserve the existing XML security guards, supplied fixtures, output-directory protection and translation semantics.
- Keep conversion offline. No credentials, live Fivetran account, database connection, extraction, imported SQL execution, deployment, push or submission is authorized.
- Use the project-local BMAD Spec and Build workflows, specialist agents and actual evidence. Keep prompts, decisions, implementation and reviews in their existing authoritative records.
- Prioritize a functional MVP. New tests cover core report behavior and an actual CLI flow; existing targeted conversion tests check regressions. Additional support and unverified conditions remain explicit.

## Non-goals

- Configure or verify live connections, establish client compatibility, resolve all PowerCenter runtime overrides, estimate physical connection counts or support every Fivetran connector.
- Change generated SQL, expand transformation support, reproduce production ingestion or replace the existing test history.

## Success signal

Saar can run the CLI on the supplied XML and inspect every source, its uses, explicit producer assignments, potential connector matches and unresolved metadata. The report is available despite unsupported transformations, and existing conversion behavior remains verified within the stated test scope.
