# Research and source checks

Research snapshot: **22 October 2026**. Saar requested the first five notes to understand the supplied mapping before PRD approval. Note 06 adds a bounded source check during architecture preparation after approval. Files are kept directly in `research/`. This is focused primary-source research for the exercise, not an exhaustive survey or a ranking of people/tools.

## Read in this order

| Note | Question it answers |
|---|---|
| [01 — PowerCenter XML structure](01-powercenter-xml-structure.md) | What are definitions, instances, ports, transformations, connectors, sessions and workflows? How do actual fields move through our XML? |
| [04 — Jaffle Shop DuckDB](04-jaffle-shop-duckdb.md) | What does the linked example project contain, how do its CSVs/models/database fit together, and how can it help? |
| [02 — Conversion design](02-conversion-design.md) | What can we learn from mature compiler/transpiler tools about parsing, typed graphs, expressions and explicit support boundaries? |
| [03 — SQL semantics and testing](03-sql-semantics-and-testing.md) | Which join, number, null, date and ordering differences need verification? What evidence can establish a result for a tested case? |
| [05 — Input handling and reproducibility](05-input-handling-and-reproducibility.md) | How should XML bytes, external declarations, runtime commands, generated files and locked environments be handled? |
| [06 — Core semantics check](06-core-semantics-check.md) | What exact functions, defaults, numeric metadata and session precision settings do the approved paths reach, and which rules still need executable checks? |
| [07 — Reference version correlation](07-reference-version-correlation.md) | Which historical Jaffle Shop revisions correspond to the XML/export publication dates, and do their rules permit a one-to-one comparison? |

## Sources and evidence rules

Each note links original documentation or maintainer material, gives its reading scope and distinguishes source facts, project-specific observations and recommendations. Authorities include Informatica, Python, dbt Labs, DuckDB, Oracle, Apache Calcite and SQLGlot maintainers. Mature project examples inform the design; they are not proof that our converter works or that a dependency must be adopted.

Some exact PowerCenter documentation pages returned HTTP 403. Notes identify available indexed excerpts and related-version evidence rather than claiming full manuals or exact-runtime confirmation. Source product/version must remain visible. Mutable repository links need a pinned revision before being used as reproducible comparison oracles.

## Findings that affect the review

- Follow connector endpoints, not suggestive column names. The supplied product price ports are cross-wired relative to their names; faithful conversion must preserve the actual mapping.
- Separate XML parsing, reference resolution, supported semantic rules and SQL emission. A small typed graph can apply these boundaries without a large compiler framework.
- XML syntax is shared; ETL schemas and transformation semantics are product/version specific. Configuration alone cannot translate arbitrary scripts or stateful logic.
- Distinguish Oracle source/storage null rules from PowerCenter intermediate expressions. Decimal division, IIF defaults and two-digit-year date parsing need explicit, tested rules.
- Mapping-query conversion does not automatically reproduce target pre-SQL, workflow command tasks or session side effects. The supplied file contains such commands; none were executed.
- Use independently expected complete results and explicit rejected cases. Keep test outcomes, result checks and coverage separate; passing a small sample is not universal accuracy.

The approved stack remains unchanged. The [PRD](../_bmad-output/planning-artifacts/prds/prd-powercenter-to-dbt-2026-10-22/prd.md) was approved in U64; later source checks support its engineering gates without changing approved scope. Native BMAD memory/contracts remain the decision records. These notes are reference evidence, not another work log, implementation plan or measured test report.

No converter code, dependency installation, reference-project execution or result testing took place during this research. Original supplied files remain unchanged.
