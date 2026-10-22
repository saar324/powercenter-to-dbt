# Technical and source addendum

This native BMAD sidecar preserves implementation detail and source depth without expanding the PRD's approval scope. The main review document is [prd.md](prd.md). No converter has been implemented and no result tests have run.

## Approved stack and considered alternatives

Saar approved the Python stack in prompt U28. The SQL/Python discussion concerned the converter language, as clarified in U26–U27; it was not a request to generate Python dbt models.

| Responsibility | Approved tool / approach |
|---|---|
| Converter | Python 3.13 command-line program |
| Dependency environment | uv; compatible dependencies locked during setup |
| XML | Standard-library ElementTree |
| Mapping structures | Dataclasses and type hints |
| CLI | argparse |
| SQL output | Explicit emitter for supported transformation rules |
| Tests | pytest, DuckDB and dbt-duckdb |
| Evidence | Standard CSV output and concise Markdown |

Python was recommended for its built-in XML/CLI facilities and fit with local data/testing tools. TypeScript/Node was a valid alternative for familiarity or an existing Node product; Go for compiled executable distribution. Existing npm/BMAD tooling does not make Node a converter dependency. No speed benchmark justified the choice. Add a parser/emitter library only for a demonstrated need; generic SQL parsing does not establish Informatica expression semantics.

Conversion structure remains an implementation design task: read source objects, resolve a typed mapping graph and emit SQL with explicit rules. A future source-specific-reader → shared-transformation-representation → SQL-emitter design is a practical proposal, not an implemented multi-vendor framework. Coding agents help build and review the converter; an AI API is not part of its conversion path.

## Dependency analysis

Saar raised a separate dependency-map component in U33 and approved a separate Python file in U59. Responsibility: given a resolved mapping graph, collect a selected target's prerequisites, detect missing references/cycles and produce a stable processing order. Field lineage still needs port-level connections. This is dependency analysis for conversion, not a new job scheduler. Python's [graphlib](https://docs.python.org/3.13/library/graphlib.html) can supply ordering/cycle primitives; see [design research](../../../../research/02-conversion-design.md). Any implementation here must be original and use public-source reasoning. A private reference received only a bounded structural read-only check; its identity, paths, code and implementation details are excluded. No private code reuse or algorithm review is claimed. The separate dependency-analysis file is approved; other component boundaries remain for the implementation design.

## Supplied export and integrity

- Source repository: [Infinite Lambda demo](https://github.com/infinitelambda/flowline-pwc-demo).
- Recorded upstream commit: `550a222cf73ecca3bd423b1f5770461914889615`.
- XML SHA256: `0c34e0ed2965e117b5de54ca2b1d1333286beb928a6bc63eaf131b04982a3522` (728,727 bytes).
- Fresh inspection: one repository/folder, twelve source definitions, sixteen target definitions, three mappings, ninety-eight transformations, 1,066 connectors, one workflow and three sessions.
- `POWERMART.REPOSITORY_VERSION="187.96"` and repository `VERSION="187"` are export metadata, not a verified PowerCenter application release.
- XML document order is staging, enriched, core. Follow graph/dependency information rather than that order. Upstream describes RAW → staging → core → enriched.

The complete freshly inspected graph inventory and semantic evidence are in [reconcile-supplied-xml.md](reconcile-supplied-xml.md). This is source evidence, not a claim that any target is supported.

### Planned fixture coverage

| Mapping | Target instance(s) | PRD proposal |
|---|---|---|
| `m_FL_JS_STAGING_FULL` | `STG_CUSTOMERS`, `STG_ORDERS`, `STG_PRODUCTS`, `STG_SUPPLIES` | Core |
| `m_FL_JS_STAGING_FULL` | `STG_ORDER_ITEMS` | First bonus |
| `m_FL_JS_STAGING_FULL` | `STG_LOCATIONS` | Deferred router/custom-union graph |
| `m_FL_JS_MARTS_CORE` | `CUSTOMERS` | Core |
| `m_FL_JS_MARTS_CORE` | `PRODUCTS`, `SUPPLIES`, then `ORDER_ITEMS` | Bonuses in that order |
| `m_FL_JS_MARTS_CORE` | `ORDERS` | Deferred stateful graph |
| `m_FL_JS_MARTS_ENRICHED` | `ORDER_ITEM_ENRICHED`, `PRODUCT_DAILY_PERFORMANCE` | Later bonuses if full dependencies/results can be verified |
| `m_FL_JS_MARTS_ENRICHED` | `CUSTOMER_360`, `ORDER_FINANCIALS1`, `STORE_DAILY_KPIS` | Deferred larger stateful/router/custom graphs |

`ORDER_FINANCIALS1` is an instance referring to definition `ORDER_FINANCIALS`; `RAW_PRODUCTS1` refers to `RAW_PRODUCTS`. Suffixes cannot be stripped to resolve identity. A core acceptance target name selects a graph; it is not a license to hard-code its SQL.

### Semantic acceptance detail

- Fresh research traces crossed product connectors: `EXP_PRODUCTS.PRODUCT_PRICE = PRICE/100` feeds target `PRODUCT_PRICE_CENTS`; passthrough `PRODUCT_PRICE_CENTS = PRICE` feeds target `PRODUCT_PRICE`. Use distinct independent inputs and check final type/precision. Treat this as surprising source wiring, not a proven source defect or a reason to repair the mapping. See the [actual XML walkthrough](../../../../research/01-powercenter-xml-structure.md).
- The seven Source Qualifiers reached by the proposed core have empty SQL overrides/source filters and distinct disabled. Treat that as the initial supported profile; a nonempty override/filter or enabled distinct needs a dedicated translation or explicit rejection, verified with mutated input.
- Product expressions include `PRICE/100`, nested `IIF(UPPER(LTRIM(RTRIM(TYPE))) = 'JAFFLE',1,0)` and beverage classification. Supplies include `COST/100` and an OR condition on perishable values. Test nested syntax, literals, null conditions and numeric behavior rather than substitute text blindly.
- `JNR_SUPPLIES_PRODUCTS` is a Normal Join with condition `SKU1 = SKU`; the product-side `SKU1` port is master. Test missing matches, null keys and duplicate SKUs.
- `AGG_ORDERS_BY_CUSTOMER` groups `CUSTOMER_ID` and computes COUNT/MIN/MAX/SUM. `JNR_CUSTOMERS_ORDERS` is a Master Outer Join with customer-side master ports. Related official Informatica documentation defines master outer as preserving detail rows. The PowerCenter 10.5 pages returned HTTP 403 during research; do not turn related-version terminology into a claimed PowerCenter runtime comparison. Establish/document the rule, preserve input roles and verify independent unmatched-row expectations before calling the path supported.
- `EXP_ORDERS` uses a two-digit-year date round trip, not a literal date cast. `SRT_ORDERS` sorts ORDER_ID ascending with distinct disabled and explicit case/null settings. Determine meaningful effects on the selected relational results. No stateful ordering rewrite is part of the proposed core.
- Local variables in `EXP_CUSTOMER_ORDER_NUM` retain previous-row state. Other local variables can be row-local; reject/translate based on actual behavior rather than the mere presence of a local port.
- `UN_REGIONS` and `UN_ORDER_BANDS` are Custom Transformations identifying a particular Union template/module. Recognition of that template could be a future feature; treating all custom transformations as unions would be incorrect.
- Runtime parameters such as `$$RUN_DATE` and defaults such as `ERROR('Transformation Error')`, NULL and 0 need explicit boundaries. SQL model conversion does not automatically reproduce PowerCenter error routing or sessions.
- Document and test numeric precision/scale and source, intermediate-expression and target-conversion null rules separately. Oracle storage's empty-string behavior is not automatically PowerCenter expression behavior. Related PowerCenter YY documentation uses the evaluation century; formatting/parsing can change the source year. Preserve evidence/version limits and test declared century boundaries rather than assume a date cast. See [SQL semantics research](../../../../research/03-sql-semantics-and-testing.md).
- The target instance includes `TRUNCATE TABLE STG.STG_CUSTOMERS` as pre-SQL. U57 supersedes the report-only proposal: generate equivalent supported dbt preparation steps and test them locally. Resolve source table names to the correct generated relation; verify table existence, materialization order and repeat-run removal of stale rows before claiming equivalent behavior. Conversion itself does not execute imported SQL. Report commands that cannot be converted; arbitrary workflow-command support is not approved or established.
- Validate Sorter keys/directions/settings separately from unordered result checks; changing a sort key need not change the result multiset. Do not infer persistent table order or support distinct removal without a separate rule.

## Verification and report contract

Carry forward the [existing native verification/reporting companion](../../../specs/spec-powercenter-to-dbt/validation-and-reporting.md). Planned files are `reports/test-runs.csv` and `reports/validation.md`. They do not exist as measured results yet.

Proposed run columns:

```csv
run_id,utc,revision,stage,environment,case_id,test_type,input_id,target,status,detail,evidence
```

Record the tested commit plus dirty-change fingerprint if applicable, fixture/hash, relevant installed versions, actual timestamps and evidence. Status is passed/failed/error/skipped. CSV rows are authoritative measured history; native verification records hold command/evidence links and interpretation, not another copy of rows. Final reporting filters to the final revision and keeps earlier failures visible as history.

Pass rate, if shown, is passed / (passed + failed + error), with skips separate. For result checks, divide the number of cases whose complete output matches the expected output by the number of executed result cases. Fixture coverage separately counts supported, emitted, executable and result-checked targets out of sixteen. A negative-test pass does not imply target support. SQL output determinism excludes changing timestamped run metadata.

Use synthetic controlled datasets, not real staff/customer identities or client credentials. Compare expected columns, values and duplicate counts. Declare numeric/date assumptions; row order is not part of equality unless explicitly required. Versioned fixture hashes and case identifiers distinguish realistic conditions without an excessive environment matrix.

## Reference boundaries and future work

[The research index](../../../../research/README.md) links five focused notes, including [Jaffle Shop explained](../../../../research/04-jaffle-shop-duckdb.md) and mature-tool design patterns. They are reference evidence, not a second decision log or a mandatory dependency list.

[reconcile-official-references.md](reconcile-official-references.md) records official reading scope/access limits. The classic DuckDB Jaffle Shop has customers/orders/payments; modern Jaffle Shop linked by Infinite Lambda has additional entities. Their current project requirements differ too. Neither was executed during PRD drafting. Use matched data/rules for comparisons and lock a compatible local environment during implementation rather than claim the references are drop-in equivalent.

XML is common syntax, not a common ETL language. Software-specific schemas, semantics and versions require representative exports and tests. A vendor same-version repository import rule is not proof that every XML grammar changes or that multiple versions cannot be supported.

| Boundary / future need | Concrete next work | Acceptance test |
|---|---|---|
| Unsupported expression/operator | Define its type/null/state rules and add a supported translation. | Focused edge cases plus a complete target result check; unsupported variants still fail visibly. |
| Stateful order-number logic | Specify evaluation order and tie rules, then evaluate a window-based rewrite. | Repeated customers, ties, nulls and boundary groups match independently expected sequences. |
| Router / recognized Union template | Model branch/group/default semantics and recognize the exact template signature. | Overlapping/default groups and duplicate rows preserve expected counts. |
| Additional export release | Obtain a representative fixture and document actual differences. | Versioned fixture converts with expected results or an explicit unsupported result. |
| Additional product | Build one fixture-backed reader against that product's official schema/semantics. | A nontrivial matched transformation yields the same independently expected result. |

These are practical candidates, not implementation commitments or observed converter defects. The final report must prioritize actual evidence, unresolved failures and realistic next work.

## Process evidence and privacy

Use [the prompt record](../../../../docs/agent-prompts.md) and native BMAD memory/verification records. The setup scope mistake remains documented once in [README](../../../../README.md#agent-error-caught-during-setup); the later language misunderstanding has detection/correction evidence in native memory and prompts U25–U27. Do not invent another incident or imply code was affected.

The record is curated, not a full conversation export. Available app tools did not expose a file-export function; desktop UI export availability is not established. Include a shareable full task export if supported, otherwise disclose the limitation and preserve available exact prompts. Keep private submission links, mail identifiers, signatures and unrelated context outside the submission.

Use Codex desktop and the pinned official BMAD installation openly. Saar's personal Codex 20× plan and description of GPT 5.6 with high thinking and fast execution are self-reported; only record actual runtime model settings when captured. The approval covers the converter stack, not an unverified model-speed claim.
