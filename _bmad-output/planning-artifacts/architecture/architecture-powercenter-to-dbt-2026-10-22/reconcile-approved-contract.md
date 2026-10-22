# Approved-contract input reconciliation

Compared `ARCHITECTURE-SPINE.md` with the one canonical package: `_bmad-output/specs/spec-powercenter-to-dbt/SPEC.md` and its adopted assignment, source-compatibility, validation/reporting, PRD and addendum companions. Also read exact prompts U65–U72 and the corresponding recorded agent questions A15–A20. This is source preservation before the separate architecture-review gate; it does not establish implementation readiness, executable compatibility or delivered conversion.

## Preserved load-bearing inputs

| Canonical input or latest user decision | Architecture landing |
|---|---|
| XML-derived equivalent dbt output; no fixed Jaffle Shop queries; exact connector/port identity and target column order. | AD-1, AD-3, AD-4 and AD-6. Connected values and original expressions remain traceable; transformations remain XML-derived. |
| Approved Python/uv/ElementTree/dataclass/argparse/emitter and pytest/DuckDB/dbt-duckdb stack; separate dependency-analysis file. | Shared Python objects, component boundaries, structural seed, Stack and Deferred. Package pins remain centralized future lockfile work, not a verified environment claim. The adopted package still owns the exact selected libraries. |
| U65: work through the design with Saar; U72: discuss at the proper system level. | One draft spine presents the whole pipeline, boundaries, outputs, failure policy and verification together. No small implementation approval questions are embedded. The owner discussion should use this coherent system view; this audit does not approve it for Saar. |
| U66: separate read, connection checking and SQL generation. | Design Paradigm, AD-1 and AD-2. Generator consumes a checked plan rather than bypassing validation. |
| U67: explicitly record separation of concerns. | AD-2 assigns representation, reading, planning, expression/relational rules, writing, CLI and independent tests separate responsibilities. |
| U68: one SQL model per target, intermediate operations inside it. | AD-3 specifies one target model with named CTEs. |
| U69: SQL plus runnable configuration, source data supplied separately. | AD-4 includes project/source/profile files and declares external inputs; validation supplies controlled data. |
| U70: keep complete independent outputs, report failures, block dependent outputs. | AD-5 defines per-target outcomes, failure propagation, nonzero selected-failure status and current-run ownership. SQL emission is not semantic success. |
| U71: explicit sample configuration for absent cross-mapping links; transformation rules still XML-derived. | AD-4 and identity conventions map exact source/target instance keys, include sample bindings and choose ref/source explicitly; unknown/conflicting links are validated. |
| Five required targets are a verification floor, not a name/output cap; optional work follows completed basic. | AD-8 preserves the floor; Deferred does not impose a five-name allowlist. The adopted PRD defines the exact five paths and basic-before-bonus gate. |
| Preserve meaningful sorting, null/type/date/error rules; no production run-year setting or silently fixed 2026. | AD-3, AD-6 and AD-8. Unknown semantics are diagnosed, controlled test context stays distinct from production date semantics. Exact semantic evidence is still subject to preparation/review, not supplied by this reconciliation. |
| Convert supported preparation commands, including cleanup; no execution while converting; local first/repeat-run verification. | AD-7 covers separate preparation translation, relation resolution, lifecycle/order/stale rows, required-target blocking and unconverted unrelated commands. |
| Tests, actual dbt execution, independent expected data, mutations/negatives and explicit unsupported results. | AD-2, AD-5, AD-6 and AD-8; expected rows do not reuse translator logic. |
| All six employer README obligations and real prompt/error/process evidence belong to basic completion, not bonuses. | AD-8 expressly includes all six items, current prompts and actual detection/correction evidence; CAP-4 maps handoff records. The adopted source package retains the exact export-if-supported, clean-checkout, explainability and publication rules. |
| Minimal real CSV plus summary, separate test/result/coverage measures, final revision and environment, practical next work. | AD-8 establishes single actual run history and summary with revision/environment; per-target conversion and measured-test status are distinct. Detailed denominators and evidence → change → acceptance-test rules remain in the adopted validation companion. |
| Original fixture integrity, no private third-party reuse/disclosure, no live extraction/service/API or unauthorized submission. | Publication/environment/configuration conventions and Deferred preserve integrity and operational exclusions. Original code/public-source boundaries remain in the adopted addendum and repository rules; no private identifiers or code appear in the spine. |

## Carry-through clarifications

No approved scope decision was contradicted, and U66–U71 all landed. Two constraints remain inherited through the canonical source package but would benefit from one explicit architecture-level sentence rather than being easy to miss in the single system review:

1. **Effort and core priority:** the spine does not state the approximately four-hour effort constraint, flexible 20:30 finish under U43, or explicitly connect deferred design/breadth to completing the basic evidence gate first. Add a short constraint pointing to the approved PRD stages and requiring optional architecture/breadth to yield to core verification/documentation. Do not revive expired checkpoint promises, a hard cutoff or another planning workflow.
2. **External entities:** the environment convention states that XML reads do not fetch external DTDs, but omits the adopted PRD's separate prohibition on expanding external entities. Carry both restrictions into the XML-reader invariant. This is preservation of an existing input boundary, not a claim that ElementTree has been tested or that arbitrary hostile uploads are supported.

These are explicit carry-through gaps in this review artifact, not missing requirements from the canonical package or requests for new owner-level implementation decisions. Report schema details and exact library imports need not be duplicated into the spine. The separate architecture reviewer should assess the chosen contracts and interface adequacy; this audit has not done that gate or changed the sources.
