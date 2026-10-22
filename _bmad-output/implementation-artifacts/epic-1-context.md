# Epic 1 Context: Convert and verify PowerCenter mappings for reviewer use

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Deliver one cohesive basic converter: translate supported PowerCenter XML into runnable DuckDB dbt models, verify required targets/preparation, expose failures and provide explainable evidence. Three incremental stories build this outcome. Complete the basic gate before optional reusable coverage; five targets are a verification floor, not an allowlist.

## Stories

- Story 1.1: Generate and run a first XML-derived model
- Story 1.2: Convert and verify the complete basic mapping paths
- Story 1.3: Reproduce and explain the verified basic submission

## Requirements & Constraints

- Required target paths: staging `STG_CUSTOMERS`, `STG_ORDERS`, `STG_PRODUCTS`, `STG_SUPPLIES`; core `CUSTOMERS`. Inventory all three mappings/sixteen targets; selected paths include every upstream branch and bound generated producer. No fixed Jaffle Shop SQL.
- Generate runnable models, project/configuration, source declarations, sample explicit bindings and a local DuckDB profile. Supply controlled data separately. Verify generated customer cleanup on first/repeated dbt runs, including stale rows; conversion itself never executes imported commands.
- Basic completion includes actual dbt execution; independent expected column order, values and duplicate counts; relevant null/empty/unmatched/duplicate/numeric/date cases; XML mutations, rejection, sorting, determinism and preparation checks. Reference comparisons require matched inputs and rules. Compilation and correct rejection do not establish conversion correctness or coverage.
- Before bonuses, provide `reports/test-runs.csv`, `reports/validation.md`, clean-checkout commands and all README obligations: running, assumptions/omissions, wrong-output risks, genuine agent error/detection/correction, prompts/full export if supported, and actual process. Saar must understand the code. Record revision/dirty fingerprint, input, environment, stage and actual results; preserve failures and separate outcome/result/coverage counts.
- Preserve supplied hashes, native BMAD records and exact available prompts continuously; disclose unavailable history/redactions. Exclude credentials, installed packages/caches and confidential third-party context. No fabricated successes, universal accuracy or full source-runtime-equivalence claims.
- Aim near four hours from 16:34 Sofia on 22 October; 20:30 is flexible and finishing work in progress is permitted. Complete tested basic behavior and evidence before optional breadth. Submission/messaging are separate actions.

## Technical Decisions

- Python 3.13 CLI, ElementTree, dataclasses, argparse and explicit SQL rules; centrally uv-lock and smoke-check compatible pytest/DuckDB/dbt-duckdb. Product dependency compatibility remains unverified.
- Reader → shared mapping data → checked plan → translator → writer. Separate representation, XML, dependency, expression, SELECT, file/configuration and CLI responsibilities. Dependency analysis has a separate Python file. Set shared interfaces before parallel coding. Tests own expectations independently of translator helpers.
- Identity includes repository/folder/mapping, exact instance and exact port. Distinguish definitions from instances; retain expressions and separate source/intermediate/target type/default metadata. Never strip suffixes. One model per target, named intermediate CTEs, XML target column order, deterministic quoted names and collision rejection.
- Planner owns canonical ModelPlan names, alias/schema and exposed column/type contracts. Exact source-instance → target-instance configuration binds cross-mapping producers; recursively include them and use `ref`. Declare unbound external inputs with `source`. Reject absent/ambiguous/conflicting bindings and incompatible consumed columns/types; no invented renames, narrowing or fallback tables.
- Per-target outcomes are emitted/unsupported/blocked/error. Retain independent complete outputs, block transitive consumers of failed producers, return nonzero for selected failures and inventory unselected targets separately. Refuse nonempty destinations by default; publish current artifacts/inventory together. Emission is not verification.
- Parse supported expressions structurally; reject unknown semantics contextually. Qualifiers initially have empty overrides/filters and distinct disabled. Normal joins use ordinary equality; master outer preserves detail/grouped orders and leaves unmatched master customer fields null. Preserve duplicate multiplication and crossed product-price wiring.
- Implement researched three-argument IIF/null aggregates, source/target Oracle empty-string normalization separately from intermediate strings, double/decimal/target conversions and current-century YY dates. High precision is NO. Output defaults handle expression errors, not every null. Production dates are not fixed to 2026; tests control context. Verify precision, rounding, invalid dates/default interaction and supported character assumptions before support claims; unknown/error-routing variants remain explicit.
- Preparation classification yields target-bound typed intents, never raw executable XML SQL. Writer alone owns materialization/hooks; generator owns SELECT. Resolve original target relation metadata and render cleanup against dbt `this`; test existence, order and repeat-run lifecycle. Unsupported required preparation blocks its target; unrelated workflow commands remain reported. No arbitrary scheduler/workflow equivalence.
- Local conversion has no model API, live database connection or extraction. Local dbt verification uses controlled fixtures; no production writes. XML reading must not fetch DTDs or expand external entities. Generated files are deterministic; measured timestamps remain separate.

Required sources: the [SPEC and companions](../specs/spec-powercenter-to-dbt/SPEC.md), final architecture AD-1–AD-8 and [source-semantics evidence](../../research/06-core-semantics-check.md). Preserve their assignment, compatibility, reporting and related-version evidence limits; no source-runtime oracle is established.

## UX & Interaction Patterns

CLI only: inspect XML, select targets/bindings, write to a fresh destination, run documented local validation and inspect contextual diagnostics/inventory. No UI, cloud service, authentication or new scheduler.

## Cross-Story Dependencies

Sequential: 1.1 establishes real execution/preparation; 1.2 completes required paths; 1.3 reproduces the complete basic handoff. Evidence accumulates throughout. Optional outputs follow basic completion and never replace required targets.
