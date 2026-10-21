# Initial sample findings

These are observations from the supplied file and linked repositories. They are research inputs, not promises about converter coverage.

The exact source commits and checksums are recorded in `fixtures/powercenter/provenance.json`. The XML inventory is in `docs/evidence/sample-inventory.json`.

## File and pipeline

The sample is an Oracle-oriented PowerCenter repository export. Its XML declaration specifies Windows-1252 and references `powrmart.dtd`. Preserve its encoding and do not fetch an external DTD when parsing it.

It contains 12 source definitions, 16 target definitions, and three mappings:

| Mapping | Target instances | Transformation types observed |
| --- | --- | --- |
| `m_FL_JS_STAGING_FULL` | 6 | Source Qualifier, Expression, Sorter, Router, Custom Transformation, Joiner |
| `m_FL_JS_MARTS_CORE` | 5 | Source Qualifier, Joiner, Sorter, Aggregator, Expression |
| `m_FL_JS_MARTS_ENRICHED` | 5 | Source Qualifier, Joiner, Sorter, Aggregator, Expression, Router, Custom Transformation, Filter |

The upstream README describes the processing order as raw sources, staging, core marts, then enriched marts. XML document order differs: the enriched mapping appears before the core mapping. Do not infer execution order from document position.

## Semantic cases to investigate

- Connectors link named fields between instances. Instances and definitions must be distinguished.
- Expressions include renaming, division by 100, nested `IIF`, null handling, trimming, uppercasing, and date conversion.
- The two observed Custom Transformation definitions identify the built-in Union Transformation template. Do not assume that every custom transformation is a union.
- Some expressions use local variables and previous-row state. Their meaning needs separate investigation; a generic text substitution may change behaviour.
- Joins, grouping, routing, union semantics, nulls, ordering, dates, and numeric precision need deliberate support or an explicit limitation.
- Multiple targets occur in one mapping. Decide how the CLI selects a mapping and target before implementing output generation.

These observations do not establish that every path is executable or fully understood. The specification must state which cases are supported and how unsupported cases are reported.

## Reference mismatch

The linked `dbt-labs/jaffle_shop_duckdb` revision contains raw customers, orders, and payments seeds. The XML also describes items, products, supplies, and stores, with different source fields.

Therefore, the linked reference cannot be used as an exact oracle for every XML target. The XML controls conversion meaning. Use compatible comparisons and independently defined synthetic data for the remaining checks. Do not hard-code another Jaffle Shop project's output to bridge the mismatch.
