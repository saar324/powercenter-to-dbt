---
title: PowerCenter-to-dbt converter
status: final
created: 2026-10-22
updated: 2026-10-22
---

# PRD: PowerCenter-to-dbt converter

**Approved by Saar in U64.** The converter stack, five-target verification minimum without an output cap, DuckDB SQL, row-comparison rules, supported preparation-step conversion and separate dependency-analysis file are approved. No converter implementation or result measurements exist yet. Continue through the installed BMAD planning and implementation stages.

## 0. Document purpose

This PRD consolidates the supplied assignment, recruiter logistics, original XML and public references with Saar's recorded directions. It defines the result to build and how to assess it. [Technical details and source inventory](addendum.md) support this document; they do not add hidden scope. The native SPEC now reflects the individually approved decisions and adopts this PRD and addendum. Final PRD approval is recorded in U64; native architecture, stories, readiness and implementation preparation remain next. These are not independent plans.

Saar's review starts with the original mandatory requirements, then evaluates research-based proposals and their reasons. Added features or research recommendations must not replace the assignment's required conversion logic, tests and submission evidence. The brief permits reasonable coverage limits; those limits must be explicit rather than used to bypass its requirements.

## 1. Vision

Build a small tool that translates supported Informatica PowerCenter mapping logic from XML into equivalent dbt SQL models. The value is preserving the transformation rules—field lineage, expressions, joins and aggregation—rather than reproducing a fixed Jaffle Shop query.

The exercise rewards reasoning, honest limits, tests and code Saar understands. A complete tested subset is more valuable than broad output that silently omits logic. Saar reports a wider company ambition for conversion across products and versions; this submission will explain a practical extension path without claiming universal conversion.

## 2. Target user and task

Saar is the builder and CLI operator. Infinite Lambda's evaluator must be able to reproduce the conversion, inspect the generated models and understand its limits.

Jobs to be done:

- Convert a supported mapping without manually rewriting its data logic.
- Identify the exact reason a target cannot be converted safely.
- Run generated models against controlled data and inspect measured evidence.
- Explain the implementation and agent-assisted process during the interview.

The operator scenario is deliberately small: Saar selects an XML input and target set, generates models, runs documented verification and reviews results and diagnostics. A new web interface or invented customer journey is unnecessary for this CLI exercise.

## 3. Glossary

- **Mapping:** a PowerCenter graph connecting sources, transformations and targets.
- **Target path:** the complete incoming dependency graph for one target, including every branch; it need not be a single linear sequence.
- **Instance / definition:** a named use of an object versus the object it references. Their names can differ.
- **Port / connector:** a transformation field versus a link between specific instance ports.
- **dbt SQL model:** a SQL query saved as a model file, which dbt uses to build a table or view.
- **Source Qualifier:** the PowerCenter transformation that defines how relational source rows enter a mapping.
- **Expression / Joiner / Aggregator / Sorter:** transformations for row calculations, combining rows, grouped calculations and sorting respectively.
- **Master / detail:** PowerCenter Joiner input roles; these determine outer-join preservation rules.
- **Supported:** the complete target path is within the converter's declared translation rules. **Unsupported** means a known boundary prevents conversion; **unverified** means evidence is missing.
- **Result check:** comparison of generated-query output with independently specified expected columns, values and duplicate counts.
- **Core / bonus:** required delivery scope if this PRD is approved versus optional work allowed only after the core passes.

## 4. Approved core and proposed bonuses

### 4.1 Complete core — target set approved

[DECISION A1 — approved by Saar in U46] The following five complete target paths form the minimum. Their names identify acceptance fixtures, not hard-coded conversion rules. The decisions below define the agreed boundaries; this target-set approval alone does not finalize the whole PRD.

The five targets are a required verification minimum, not a target-name allowlist or output limit. Conversion rules must apply to other targets using supported constructs. After the core passes, verify additional reusable paths before claiming them as supported; do not add artificial exclusions to keep the output count at five. New transformation semantics and complete-path verification still require separate work.

| Mapping | Target | Required behavior |
|---|---|---|
| Staging | `STG_CUSTOMERS` | Source fields and target renames |
| Staging | `STG_ORDERS` | Date/currency expressions and its non-distinct Sorter |
| Staging | `STG_PRODUCTS` | Arithmetic, nested string functions and conditions |
| Staging | `STG_SUPPLIES` | Product/supply normal join, arithmetic and conditions |
| Core marts | `CUSTOMERS` | Order grouping, master-outer join and customer metrics |

The core is complete only when all five generate, run and pass their defined result checks, required negative/mutation and preparation checks pass, reporting is measured and the README is reproducible. All six employer README/evidence obligations in FR-8, including actual prompts/export handling and the agent-assisted process, belong to this basic-stage gate; they are not bonuses. Capture evidence during work. Saar must be able to explain the submitted code. If a required semantic rule cannot be established, report the blocker and agree a scope change; do not silently lower this gate.

[DECISION A2 — approved by Saar in U51] Generate DuckDB SQL for this exercise, using DuckDB/dbt-duckdb for local verification and the supplied reference where applicable. Other output dialects are future work.

[DECISION A3 — approved by Saar in U53–U54] Preserve target column order from the XML. Compare result rows without requiring the same display order, while checking all values and duplicate counts. Do not add alphabetical or other display sorting without a requirement. Preserve and separately test sorting where the mapping requires it or it affects calculations. A Sorter can be translated only where its distinctness and downstream effects are understood. Stateful order-dependent calculations remain outside this core. Date and Joiner interpretation risks in §11 are acceptance gates, not permission to guess.

[DECISION A5 — approved by Saar in U57] In addition to row transformations, generate equivalent dbt preparation steps for supported imported setup commands, including the supplied customer-table cleanup before loading. Derive these steps from XML and resolve their target names to generated relations; do not blindly copy vendor SQL. Test the preparation and repeated-load behavior in a local database. Commands that cannot be converted must be clearly reported; arbitrary command support is not promised. XML conversion itself does not execute imported commands.

### 4.2 Bonuses — only after the core passes

1. Short additional paths: staging `STG_ORDER_ITEMS`, then core `PRODUCTS` and `SUPPLIES`.
2. Core `ORDER_ITEMS`: additional joins and aggregation after its semantics are checked.
3. Enriched `ORDER_ITEM_ENRICHED` or `PRODUCT_DAILY_PERFORMANCE` if dependencies are provided and the result can be verified completely.

Defer staging locations, core orders and the larger enriched paths that involve routers, custom union templates, stateful variables or runtime parameters. A recognized union template is not equivalent to arbitrary custom-code support. These exclusions and their practical implementation/tests belong in the final report.

## 5. Remaining stages and BMAD handoff

[DECISION A4 — U43] Keep total effort around four hours from the original 16:34 Europe/Sofia start on 22 October. Aim to finish around 20:30; 20:40 is acceptable, and finish work in progress when needed. The earlier 18:30/18:55/19:40 checkpoint proposals are superseded, not missed delivery promises. At the 19:08 review there are about 80 minutes to the original finish target; no implementation throughput has been measured.

| Stage | Required result |
|---|---|
| Final PRD approval | Saar approves the consolidated decisions; no product code starts before this. |
| Native preparation and first result | Use `bmad-help`, reconcile this PRD through `bmad-spec`, complete the required architecture, stories and sprint-readiness stages, then enter `bmad-build` for its implementation contract. Verify semantic rules, lock the environment and execute the first generated model. |
| Core verification and basic handoff | Complete the five required target paths and preparation behavior; pass independent result, mutation, rejection and repeat-run checks. Complete measured reports, reproducible run instructions, all six employer README items and current prompt/decision/error evidence before bonuses. |
| Reusable additional outputs | Include and verify further outputs using the supported rules; do not impose a five-output cap or silently replace the required core with easier outputs. |
| Final evidence refresh and handoff | Repeat relevant clean-checkout checks after any additional outputs; refresh the already required reports, README and prompt/process evidence, then complete final review and prepare the repository/ZIP for reviewer access. Keep the finish near 20:30 with the agreed flexibility. |

Reduce optional expansion first if progress threatens core verification and documentation. Report a concrete blocker or material effort change rather than silently lowering the core gate. These are work stages, not a claim that the scope has already been delivered. Submission and recruiter messaging remain later explicit actions.

## 6. Review decisions and remaining engineering checks

- **Resolved:** five required targets without an output cap (U46–U48); DuckDB SQL (U51); target column order and row comparison (U53–U54); supported preparation-step conversion (U57); separate dependency-analysis file (U59).
- **Engineering checks, not owner questions:** verify join preservation, date rules, numeric precision, null/empty-string handling and error/default behavior against the recorded sources and focused tests. Establish the rule before implementing its translation. Unknown rules must block affected support or lead to a concrete proposed boundary for Saar; do not guess. Related-version documentation and independent examples do not prove full PowerCenter runtime equivalence.
- **Date-test correction:** the proposed required run-year setting was withdrawn after U61. Controlled test clocks/context are an engineering detail; no production year is fixed to 2026 and no user-facing date setting is approved by default.
- **Repository access resolved:** Saar requested public visibility in U42. The existing repository is public and anonymous access was verified; current local drafts still need publication. Reviewer handles are not required for public access.
- **Final approval resolved — U64:** Saar approved this consolidated PRD and requested continuation. No other product question is currently identified; a newly discovered semantic blocker must be raised with concrete evidence.

## 7. Features and functional requirements

### 7.1 Read and understand the export

#### FR-1: Discover mapping structure

The operator can read the supplied export and identify mappings, target paths, source definitions, transformations and connectors.

**Testable consequences:** the inventory identifies all three mappings and sixteen target instances; instance-to-definition references and connector port identities are retained. XML document order does not determine execution order. Malformed XML, missing references or dependency cycles produce explicit diagnostics for affected paths.

#### FR-2: Select complete conversion scope

The operator can choose one or more targets using the documented CLI. The converter examines every upstream dependency of each selected target.

**Testable consequences:** unrelated unsupported branches do not become silently selected; a selected target with unsupported logic is reported as unsupported. Shared dependencies are resolved consistently. The original input remains unchanged.

### 7.2 Derive runnable dbt SQL

#### FR-3: Translate supported relational operations

The converter derives SQL from XML fields, connections and rules for the approved target paths. The approved core requires projections/renames; the expressions reached by those paths; normal and master-outer joins; grouped COUNT, MIN, MAX and SUM; and the non-distinct Sorter reached by staging orders. Exact semantic boundaries remain to be settled.

**Testable consequences:** joins follow input roles and the XML condition; duplicates are preserved or multiplied according to the operation. Aggregation follows group ports and null-sensitive aggregate behavior. Expressions preserve supported arithmetic, conditions, string handling and dates within the declared boundary. Unknown semantics cause a diagnostic, not guessed SQL.

The core Source Qualifier profile has empty SQL overrides/source filters and distinct disabled. Other profiles require explicit support or rejection. Document and test numeric precision/scale, source/storage null behavior, PowerCenter intermediate empty-string/null behavior, target conversion and output-default/error boundaries separately before a path counts as verified; per-row recovery remains outside scope.

Changing a supported expression, field name or source reference in XML changes the generated behavior as independently expected. Conversion rules cannot branch on Jaffle Shop model names to return fixed queries. The supplied product price fields are connected to targets whose names suggest opposite units; preserve and test that exact wiring rather than silently correct it.

#### FR-4: Produce executable models and dependencies

Generated SQL models can run in a documented local dbt validation project with the required source data and source/model references.

**Testable consequences:** the proposed raw-customers/raw-orders → staging → core-customers slice runs in dependency order through dbt. Product and supply paths also run. Source references are derived from XML and declared configuration; the converter is not responsible for extracting a client's live data. Identical XML and configuration produce identical SQL/model metadata.

Classify imported runtime SQL and commands. Generate equivalent dbt preparation steps for supported commands, including the supplied customer-table cleanup, and report commands that cannot be converted. The converter writes artifacts without executing imported SQL. Verify generated preparation steps in the local dbt test database, including a repeat run with stale pre-existing rows; table lifecycle and command order must be compatible with dbt materialization. Row-result checks alone do not prove setup behavior or arbitrary workflow equivalence.

#### FR-5: Make unsupported behavior explicit

Diagnostics identify the affected mapping, target and transformation or expression, with a reason.

**Testable consequences:** unsupported logic is never silently removed and the affected target is never presented as converted. A failed selected conversion returns a failing CLI status. Unaffected successful targets may be retained only with an explicit partial-result inventory; the documented behavior must prevent stale output from being mistaken for current success.

### 7.3 Verify behavior and report evidence

#### FR-6: Check conversion results independently

Tests exercise complete core target paths using small, controlled datasets and expected results calculated independently of the converter.

**Testable consequences:** checks compare columns, values and duplicate counts, including applicable nulls, empty strings, unmatched/duplicate join keys, empty inputs, numeric division/precision and date boundaries. At least one XML mutation exercises each core operation category. Sorter mutations check generated keys/directions and supported settings separately; unordered result equality cannot prove sort behavior. A distinct-enabled mutation is rejected until explicitly supported. Negative cases check malformed or unsupported input. Repeated conversion checks deterministic SQL generation. Actual dbt execution is required; compilation alone is insufficient.

Use a Jaffle Shop reference only when schema, input rows and transformation rules match. Tests based on independent examples must not be described as a complete PowerCenter runtime equivalence proof.

#### FR-7: Record measured runs and a concise report

Produce one machine-readable run history and one short human report, segmented by actual case/type, input, condition, environment and development stage.

**Testable consequences:** every reported result links to a real run, tested revision, input identity and environment. Test outcomes, result checks and fixture coverage remain separate. Unsupported and unverified cases remain visible. Correct rejection can pass a negative test without increasing conversion coverage. Prior failures remain history; final measurements identify the final tested revision.

The human report states verified strengths, observed failures, deliberate exclusions, untested risks and practical next steps. Each material next step follows **evidence → concrete change → acceptance test**. Keep reporting minimal. Do not fabricate passing rows or claim universal accuracy.

### 7.4 Reproducible and transparent handoff

#### FR-8: Deliver a short, complete README

The submission README covers all six requested areas: run instructions; assumptions/omissions; likely wrong-output cases; a genuine agent mistake and how Saar caught it; prompts from the initial prompt onward, plus a full shareable task conversation export if the tool supports it; and the actual agent-assisted process. A complete export can serve as the single prompt source only when it preserves the required prompts; a curated prompt list does not waive a supported full-export requirement.

**Testable consequences:** documented commands work from a clean checkout with declared prerequisites. Links resolve to actual evidence. Saar can explain any part of the submitted code and trace a generated column back through XML and code.

**Later submission checklist:** use the existing public repository, or a ZIP if needed. The brief also permits a private repository with confirmed reviewer access. Publish the relevant development evidence, check anonymous access, use the supplied submission channel by the recruiter's stated 23 October 2026 deadline and notify the recruiter after submission as requested. Public visibility was authorized in U42; actual submission and sending still require Saar's separate instruction.

#### FR-9: Preserve development evidence as work occurs

Use official project-local BMAD workflows and the actual prompt record throughout development.

**Testable consequences:** requirements, choices, implementation checks and reviews use their native records; generated run data has one authoritative source. Preserve original fixture hashes, exact available prompts, approval provenance and genuine error/correction evidence. Label missing conversation history and redactions honestly. Tools documentation includes Codex desktop, Saar's user-reported personal Codex 20× plan and BMAD; subscription and runtime model metadata stay separate.

## 8. Non-goals

- Arbitrary XML or universal cross-vendor/version conversion.
- Full coverage of all sixteen supplied targets within this time box.
- Silent replacement of XML behavior with a more familiar Jaffle Shop implementation.
- Live PowerCenter execution, database extraction, continuous synchronization, UI or hosted service.
- Reproducing arbitrary PowerCenter commands, session scheduling, recovery or per-row error handling. Supported preparation commands are included under A5 and FR-4; unconverted commands remain explicitly reported.
- Production deployment, submission or recruiter notification in this preparation stage. Repository public visibility was separately authorized and completed in U42.

## 9. Success measures

No measurements have been produced. These are proposed delivery gates, not current scores.

- **SM-1 — Core completion:** all five approved core paths emitted, executed through dbt and independently result-checked; all required checks pass on the final revision. Validates FR-2–FR-6. Show path and case counts, including failed/error/skipped cases.
- **SM-2 — General conversion evidence:** XML mutation cases cover every core operation category and change results, ordering rules or supported-status diagnostics as independently expected. Validates FR-3 and FR-6.
- **SM-3 — Reproducibility and transparency:** a clean-checkout verification and all six README obligations pass review. Validates FR-7–FR-9.
- **SM-C1 — Coverage honesty:** show supported, emitted, executable and result-checked counts against the full sixteen-target fixture; passing rejection tests never raise supported coverage. Counterbalances inflated test pass rates.
- **SM-C2 — Time and breadth:** aim for about four hours total; 20:30 is a flexible finish target, and finish work in progress when needed. Preserve core verification/documentation time instead of maximizing model count. Counterbalances bonus expansion. No finite test set establishes universal accuracy.

## 10. Quality and working constraints

- Use the approved Python CLI stack; exact package versions will be locked and compatibility verified during setup. Technical choices are in the addendum.
- Conversion uses explicit rules and requires no live database, PowerCenter service or model API. After dependencies are installed, controlled validation runs locally.
- Preserve original source files. XML reading must not fetch external DTDs or expand external entities; the supplied export's declaration must not be mistaken for a requirement to fetch a remote file.
- Fail visibly when meaning is unknown. Prioritize correct port lineage, types, nulls and complete dependencies over broad SQL emission.
- Aim for **about four hours from 16:34 Europe/Sofia on 22 October**, inclusive of learning, PRD review, coordination, code, tests and documents. Under U43, 20:30 is a target, not a hard cutoff; 20:40 is acceptable, and finish work in progress when needed. Use five to ten useful specialist agents in successive groups; the environment permits four active agents including the coordinator. Do not infer execution speed from user-described model settings.
- Keep prose simple and reports minimal. Use native BMAD records rather than parallel decision or work logs. Do not expose private correspondence, submission URLs, credentials or unrelated chat content.

## 11. Main risks and practical responses

| Risk visible in the sources | Required response / test |
|---|---|
| XML has `Master Outer Join` with customer ports marked master; familiar dbt customer logic may preserve the wrong side. | Establish the applicable PowerCenter input-role rule, then test unmatched rows on both sides, duplicate keys and null keys. Related official Informatica documentation states that a master outer join preserves detail rows; exact-version evidence limits are recorded in the addendum. |
| Orders use `TO_DATE(TO_CHAR(..., 'DD-MM-YY'), 'DD-MM-YY')`. | Formatting removes the original century. Specify the evaluation century and test date boundaries before claiming equivalence; related PowerCenter YY documentation uses the current century. Do not reduce the rule to a date cast without evidence; document or reject unsupported ranges. |
| Product price connectors cross names and the target contains pre-SQL TRUNCATE. | Follow and independently test the actual connector wiring; report surprising source behavior separately. Generate equivalent supported preparation steps, resolve the correct dbt relation and test table lifecycle, order and repeat-run cleanup locally. Never execute imported commands during conversion; report unconverted commands. |
| Supplied XML and classic DuckDB Jaffle Shop use different schemas/rules. | Match inputs/rules before comparison; otherwise use independent expected datasets. |
| Instance aliases, port collisions, nulls, decimal division or duplicates change results. | Resolve connectors by exact identity; add focused edge cases and complete-result checks. |
| Selected paths expose unknown defaults, SQL overrides or error semantics. | Record the boundary and reject affected cases rather than invent fallbacks. |
| More targets or format support consumes the remaining time. | Finish and verify the agreed core first; use the final report for evidence-backed next work. |

## 12. Assumptions index

- **A1 (§4.1), resolved U46:** Saar approved the five named target paths as the required core, with their tests, reporting and README obligations. Remaining engineering checks still gate their affected implementation.
- **A2 (§4.1), resolved U51:** generated SQL targets DuckDB for this exercise; broader dialects are deferred.
- **A3 (§4.1), resolved U53–U54:** preserve target column order; compare all row values and duplicate counts without requiring incidental display order. Preserve and test meaningful mapping order; do not add unnecessary sorting or an unverified stateful rewrite.
- **A4 (§5), resolved U43:** use the remaining work stages rather than expired intermediate clock times; aim for about four hours, with a flexible 20:30 finish and permission to finish work in progress. The current stage plan is part of final PRD review.
- **A5 (§4.1), resolved U57:** also generate supported preparation steps and verify their local behavior; report commands that cannot be converted. The earlier report-only proposal is superseded.

Approval of this document establishes the agreed product scope; it does not establish that any capability is implemented or that the submission is complete.

## 13. Sources and provenance

Source authority is explicit: the assignment defines the exercise; Saar's later decisions define the working constraints and added reporting; XML defines the mapping being converted; official references explain semantics. Saar confirmed there are no additional company instructions beyond the existing sources (U30 in the prompt record). The consolidated PRD was approved in U64. Historical extracts/reviews describe the decisions available when written; later memory entries and the current PRD supersede earlier report-only runtime scope and fixed-stop proposals.

- [Original assignment and recruiter excerpt](../../../../docs/assignment.md). The recruiter message was re-read on 22 October: the external deadline is **23 October 2026**, with no exact submission hour established. Private submission details remain outside this repository.
- [Unchanged XML](../../../../fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml), [upstream README](../../../../fixtures/powercenter/UPSTREAM_README.md) and [provenance](../../../../fixtures/powercenter/provenance.json). Fresh inspection found **three mappings, sixteen targets, ninety-eight transformations and 1,066 connectors**.
- [Recorded prompts and user decisions](../../../../docs/agent-prompts.md), [documentation rules](../../../../AGENTS.md) and [existing native SPEC](../../../specs/spec-powercenter-to-dbt/SPEC.md).
- Official PowerCenter/dbt reading and the two Jaffle Shop variants are linked with access limits in [source reconciliation](reconcile-official-references.md). They are reference evidence, not proof that generated output already works.
- [Pre-approval research](../../../../research/README.md) adds an actual XML walkthrough, Jaffle Shop primer and primary-source design/semantic/input-handling notes. Recommendations inform review; they do not silently change the approved stack or approve scope.

