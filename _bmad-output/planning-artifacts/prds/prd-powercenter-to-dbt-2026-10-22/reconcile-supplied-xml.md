# Supplied XML: fresh source reconciliation

Status: source inspection and **PROPOSED** coverage for user review. No converter or tests have been implemented by this extraction. Exact core coverage is not approved.

## Source and method

- Inspected the current supplied XML, upstream README and provenance directly on 22 October 2026. No removed historical analysis was used.
- Source: `fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml`.
- Upstream commit: `550a222cf73ecca3bd423b1f5770461914889615`.
- SHA-256 verified against provenance: `0c34e0ed2965e117b5de54ca2b1d1333286beb928a6bc63eaf131b04982a3522`.
- Original source files were not changed. Parsed XML locally with the standard library; no external DTD was fetched.
- Inventory uses direct `MAPPING/INSTANCE`, `MAPPING/TRANSFORMATION` and `MAPPING/CONNECTOR` elements. For each target instance, traced all incoming connectors recursively. Counts below describe upstream instances, not SQL execution order.

## Export boundaries

`POWERMART` has `REPOSITORY_VERSION="187.96"`; `REPOSITORY NAME="REPO_Jaffleshop"` has `VERSION="187"` and `DATABASETYPE="Oracle"`. These repository metadata values must not be presented as a verified PowerCenter application release. The export has one repository, one folder, 12 source definitions, 16 target definitions, 3 mappings, 98 transformation definitions, 1 workflow and 3 sessions.

`wf_FL_JAFFLESHOP_DEMO` references sessions for staging, core and enriched mappings. XML document order is staging, enriched, core; document order must not substitute for dependency analysis. The upstream README describes RAW → staging → core marts → enriched marts.

## Mapping and operation inventory

| Mapping | Targets | Connectors | Transformation definitions by type |
|---|---:|---:|---|
| `m_FL_JS_STAGING_FULL` | 6 | 165 | Source Qualifier: 7, Expression: 8, Sorter: 6, Router: 1, Custom Transformation: 1, Joiner: 1 |
| `m_FL_JS_MARTS_ENRICHED` | 5 | 624 | Source Qualifier: 9, Joiner: 8, Sorter: 7, Aggregator: 5, Expression: 13, Router: 1, Custom Transformation: 1, Filter: 1 |
| `m_FL_JS_MARTS_CORE` | 5 | 277 | Source Qualifier: 12, Joiner: 7, Sorter: 2, Aggregator: 4, Expression: 4 |

## Target dependency inventory

An upstream graph can branch and merge. These are complete incoming dependency sets for each target, rather than a claim that every graph is a single linear path. Instance names are distinct from referenced source/target definition names.

| Mapping | Target instance → definition | Upstream source instances | Upstream operation counts |
|---|---|---|---|
| `m_FL_JS_STAGING_FULL` | `STG_CUSTOMERS` → `STG_CUSTOMERS` | `RAW_CUSTOMERS` | Source Qualifier: 1 |
| `m_FL_JS_STAGING_FULL` | `STG_LOCATIONS` → `STG_LOCATIONS` | `RAW_STORES` | Expression: 4, Router: 1, Source Qualifier: 1, Sorter: 5, Custom Transformation: 1 |
| `m_FL_JS_STAGING_FULL` | `STG_ORDERS` → `STG_ORDERS` | `RAW_ORDERS` | Expression: 1, Source Qualifier: 1, Sorter: 1 |
| `m_FL_JS_STAGING_FULL` | `STG_ORDER_ITEMS` → `STG_ORDER_ITEMS` | `RAW_ITEMS` | Expression: 1, Source Qualifier: 1 |
| `m_FL_JS_STAGING_FULL` | `STG_PRODUCTS` → `STG_PRODUCTS` | `RAW_PRODUCTS` | Expression: 1, Source Qualifier: 1 |
| `m_FL_JS_STAGING_FULL` | `STG_SUPPLIES` → `STG_SUPPLIES` | `RAW_PRODUCTS1`, `RAW_SUPPLIES` | Expression: 1, Joiner: 1, Source Qualifier: 2 |
| `m_FL_JS_MARTS_ENRICHED` | `CUSTOMER_360` → `CUSTOMER_360` | `STG_CUSTOMERS`, `STG_CUSTOMERS1`, `STG_LOCATIONS`, `STG_ORDERS`, `STG_ORDERS1`, `STG_ORDER_ITEMS`, `STG_PRODUCTS`, `STG_SUPPLIES` | Aggregator: 3, Expression: 10, Joiner: 7, Router: 1, Source Qualifier: 8, Sorter: 4, Custom Transformation: 1 |
| `m_FL_JS_MARTS_ENRICHED` | `ORDER_FINANCIALS1` → `ORDER_FINANCIALS` | `STG_CUSTOMERS`, `STG_LOCATIONS`, `STG_ORDERS`, `STG_ORDERS1`, `STG_ORDER_ITEMS`, `STG_PRODUCTS`, `STG_SUPPLIES` | Aggregator: 2, Expression: 5, Joiner: 6, Router: 1, Source Qualifier: 7, Sorter: 4, Custom Transformation: 1 |
| `m_FL_JS_MARTS_ENRICHED` | `ORDER_ITEM_ENRICHED` → `ORDER_ITEM_ENRICHED` | `STG_CUSTOMERS`, `STG_LOCATIONS`, `STG_ORDERS`, `STG_ORDER_ITEMS`, `STG_PRODUCTS`, `STG_SUPPLIES` | Aggregator: 1, Expression: 1, Joiner: 5, Source Qualifier: 6, Sorter: 2 |
| `m_FL_JS_MARTS_ENRICHED` | `PRODUCT_DAILY_PERFORMANCE` → `PRODUCT_DAILY_PERFORMANCE` | `STG_CUSTOMERS`, `STG_LOCATIONS`, `STG_ORDERS`, `STG_ORDER_ITEMS`, `STG_PRODUCTS`, `STG_SUPPLIES` | Aggregator: 2, Expression: 2, Joiner: 5, Source Qualifier: 6, Sorter: 3 |
| `m_FL_JS_MARTS_ENRICHED` | `STORE_DAILY_KPIS` → `STORE_DAILY_KPIS` | `STG_CUSTOMERS`, `STG_LOCATIONS`, `STG_LOCATIONS1`, `STG_ORDERS`, `STG_ORDERS1`, `STG_ORDER_ITEMS`, `STG_PRODUCTS`, `STG_SUPPLIES` | Aggregator: 3, Expression: 7, Filter: 1, Joiner: 7, Router: 1, Source Qualifier: 8, Sorter: 6, Custom Transformation: 1 |
| `m_FL_JS_MARTS_CORE` | `CUSTOMERS` → `CUSTOMERS` | `STG_CUSTOMERS`, `STG_ORDERS2` | Aggregator: 1, Expression: 1, Joiner: 1, Source Qualifier: 2 |
| `m_FL_JS_MARTS_CORE` | `ORDERS` → `ORDERS` | `STG_ORDERS1`, `STG_ORDER_ITEMS1`, `STG_PRODUCTS2`, `STG_SUPPLIES2` | Aggregator: 2, Expression: 2, Joiner: 3, Source Qualifier: 4, Sorter: 1 |
| `m_FL_JS_MARTS_CORE` | `ORDER_ITEMS` → `ORDER_ITEMS` | `STG_ORDERS`, `STG_ORDER_ITEMS`, `STG_PRODUCTS1`, `STG_SUPPLIES1` | Aggregator: 1, Expression: 1, Joiner: 3, Source Qualifier: 4, Sorter: 1 |
| `m_FL_JS_MARTS_CORE` | `PRODUCTS` → `PRODUCTS` | `STG_PRODUCTS` | Source Qualifier: 1 |
| `m_FL_JS_MARTS_CORE` | `SUPPLIES` → `SUPPLIES` | `STG_SUPPLIES` | Source Qualifier: 1 |

### Exact upstream transformation instances

- `m_FL_JS_STAGING_FULL / STG_CUSTOMERS`: `SQ_RAW_CUSTOMERS`.
- `m_FL_JS_STAGING_FULL / STG_LOCATIONS`: `EXP_AMER_RENAME_TRANS`, `EXP_APAC_RENAME_TRANS`, `EXP_EMEA_RENAME_TRANS`, `EXP_LOCATIONS`, `RTR_REGION`, `SQ_RAW_STORES`, `SRT_AMER`, `SRT_APAC`, `SRT_EMEA`, `SRT_LOC_AFTER`, `SRT_LOC_BEFORE`, `UN_REGIONS`.
- `m_FL_JS_STAGING_FULL / STG_ORDERS`: `EXP_ORDERS`, `SQ_RAW_ORDERS`, `SRT_ORDERS`.
- `m_FL_JS_STAGING_FULL / STG_ORDER_ITEMS`: `EXP_ORDER_ITEMS`, `SQ_RAW_ITEMS`.
- `m_FL_JS_STAGING_FULL / STG_PRODUCTS`: `EXP_PRODUCTS`, `SQ_RAW_PRODUCTS`.
- `m_FL_JS_STAGING_FULL / STG_SUPPLIES`: `EXP_SUPPLIES`, `JNR_SUPPLIES_PRODUCTS`, `SQ_RAW_PRODUCTS1`, `SQ_RAW_SUPPLIES`.
- `m_FL_JS_MARTS_ENRICHED / CUSTOMER_360`: `AGGTRANS`, `AGG_ITEMS_BY_ORDER`, `AGG_SUPPLIES_BY_PRODUCT`, `EXP_CUSTOMER_METRICS`, `EXP_CUSTOMER_ORDER_NUM`, `EXP_HIGH_BAND`, `EXP_ITEM_CALCULATIONS`, `EXP_ORDER_FINANCIALS`, `EXP_RECENCY1`, `EXP_RECENCY2`, `EXP_RFM_SCORES`, `EXP_RFM_SEGMENT`, `EXP_STD_BAND`, `JNR_ADD_CUSTOMERS`, `JNR_ADD_LOCATIONS`, `JNR_ADD_PRODUCTS`, `JNR_ADD_SUPPLIES`, `JNR_CUSTOMERS`, `JNR_ITEMS_ORDERS`, `JNR_ORDERS_ITEMS_AGG`, `RTR_ORDER_VALUE_BAND`, `SQ_STG_CUSTOMERS`, `SQ_STG_CUSTOMERS1`, `SQ_STG_LOCATIONS`, `SQ_STG_ORDERS`, `SQ_STG_ORDERS1`, `SQ_STG_ORDER_ITEMS`, `SQ_STG_PRODUCTS`, `SQ_STG_SUPPLIES`, `SRT_BEFORE_ROUTER`, `SRT_FOR_CUSTOMER_SEQ`, `SRT_ORDER_ID`, `SRT_SUPPLIES`, `UN_ORDER_BANDS`.
- `m_FL_JS_MARTS_ENRICHED / ORDER_FINANCIALS1`: `AGG_ITEMS_BY_ORDER`, `AGG_SUPPLIES_BY_PRODUCT`, `EXP_CUSTOMER_ORDER_NUM`, `EXP_HIGH_BAND`, `EXP_ITEM_CALCULATIONS`, `EXP_ORDER_FINANCIALS`, `EXP_STD_BAND`, `JNR_ADD_CUSTOMERS`, `JNR_ADD_LOCATIONS`, `JNR_ADD_PRODUCTS`, `JNR_ADD_SUPPLIES`, `JNR_ITEMS_ORDERS`, `JNR_ORDERS_ITEMS_AGG`, `RTR_ORDER_VALUE_BAND`, `SQ_STG_CUSTOMERS`, `SQ_STG_LOCATIONS`, `SQ_STG_ORDERS`, `SQ_STG_ORDERS1`, `SQ_STG_ORDER_ITEMS`, `SQ_STG_PRODUCTS`, `SQ_STG_SUPPLIES`, `SRT_BEFORE_ROUTER`, `SRT_FOR_CUSTOMER_SEQ`, `SRT_ORDER_ID`, `SRT_SUPPLIES`, `UN_ORDER_BANDS`.
- `m_FL_JS_MARTS_ENRICHED / ORDER_ITEM_ENRICHED`: `AGG_SUPPLIES_BY_PRODUCT`, `EXP_ITEM_CALCULATIONS`, `JNR_ADD_CUSTOMERS`, `JNR_ADD_LOCATIONS`, `JNR_ADD_PRODUCTS`, `JNR_ADD_SUPPLIES`, `JNR_ITEMS_ORDERS`, `SQ_STG_CUSTOMERS`, `SQ_STG_LOCATIONS`, `SQ_STG_ORDERS`, `SQ_STG_ORDER_ITEMS`, `SQ_STG_PRODUCTS`, `SQ_STG_SUPPLIES`, `SRT_ORDER_ID`, `SRT_SUPPLIES`.
- `m_FL_JS_MARTS_ENRICHED / PRODUCT_DAILY_PERFORMANCE`: `AGG_BY_PRODUCT_DAY`, `AGG_SUPPLIES_BY_PRODUCT`, `EXP_ITEM_CALCULATIONS`, `EXP_PRODUCT_METRICS`, `JNR_ADD_CUSTOMERS`, `JNR_ADD_LOCATIONS`, `JNR_ADD_PRODUCTS`, `JNR_ADD_SUPPLIES`, `JNR_ITEMS_ORDERS`, `SQ_STG_CUSTOMERS`, `SQ_STG_LOCATIONS`, `SQ_STG_ORDERS`, `SQ_STG_ORDER_ITEMS`, `SQ_STG_PRODUCTS`, `SQ_STG_SUPPLIES`, `SRT_BEFORE_AGG_PDP`, `SRT_ORDER_ID`, `SRT_SUPPLIES`.
- `m_FL_JS_MARTS_ENRICHED / STORE_DAILY_KPIS`: `AGG_BY_LOCATION_DAY`, `AGG_ITEMS_BY_ORDER`, `AGG_SUPPLIES_BY_PRODUCT`, `EXP_CUSTOMER_ORDER_NUM`, `EXP_HIGH_BAND`, `EXP_ITEM_CALCULATIONS`, `EXP_MARK_FIRST_CUSTOMER`, `EXP_ORDER_FINANCIALS`, `EXP_STD_BAND`, `EXP_STORE_KPIS`, `FIL_LOCS`, `JNR_ADD_CUSTOMERS`, `JNR_ADD_LOCATIONS`, `JNR_ADD_LOCATION_INFO`, `JNR_ADD_PRODUCTS`, `JNR_ADD_SUPPLIES`, `JNR_ITEMS_ORDERS`, `JNR_ORDERS_ITEMS_AGG`, `RTR_ORDER_VALUE_BAND`, `SQ_STG_CUSTOMERS`, `SQ_STG_LOCATIONS`, `SQ_STG_LOCATIONS1`, `SQ_STG_ORDERS`, `SQ_STG_ORDERS1`, `SQ_STG_ORDER_ITEMS`, `SQ_STG_PRODUCTS`, `SQ_STG_SUPPLIES`, `SRT_BEFORE_AGG`, `SRT_BEFORE_ROUTER`, `SRT_FOR_CUSTOMER_SEQ`, `SRT_FOR_DISTINCT_CUSTOMER`, `SRT_ORDER_ID`, `SRT_SUPPLIES`, `UN_ORDER_BANDS`.
- `m_FL_JS_MARTS_CORE / CUSTOMERS`: `AGG_ORDERS_BY_CUSTOMER`, `EXP_CUSTOMER_METRICS`, `JNR_CUSTOMERS_ORDERS`, `SQ_STG_CUSTOMERS`, `SQ_STG_ORDERS2`.
- `m_FL_JS_MARTS_CORE / ORDERS`: `AGG_ITEMS_BY_ORDER`, `AGG_SUPPLIES_BY_PRODUCT2`, `EXP_CUSTOMER_ORDER_NUM`, `EXP_ORDERS_CALC`, `JNR_ITEMS_PRODUCTS`, `JNR_ITEMS_SUPPLIES`, `JNR_ORDERS_ITEMS_AGG`, `SQ_STG_ORDERS1`, `SQ_STG_ORDER_ITEMS1`, `SQ_STG_PRODUCTS2`, `SQ_STG_SUPPLIES2`, `SRT_BY_CUSTOMER`.
- `m_FL_JS_MARTS_CORE / ORDER_ITEMS`: `AGG_SUPPLIES_BY_PRODUCT`, `EXP_ORDER_ITEMS_CALC`, `JNR_ADD_PRODUCTS`, `JNR_ADD_SUPPLY_COST`, `JNR_ORDER_ITEMS_ORDERS`, `SQ_STG_ORDERS`, `SQ_STG_ORDER_ITEMS`, `SQ_STG_PRODUCTS1`, `SQ_STG_SUPPLIES1`, `SRT_SUPPLIES`.
- `m_FL_JS_MARTS_CORE / PRODUCTS`: `SQ_STG_PRODUCTS`.
- `m_FL_JS_MARTS_CORE / SUPPLIES`: `SQ_STG_SUPPLIES`.

## Significant semantics visible in the source

1. **Connector and instance identity matter.** The enriched target instance `ORDER_FINANCIALS1` references target definition `ORDER_FINANCIALS`. In staging, `RAW_PRODUCTS1` references source definition `RAW_PRODUCTS`. Suffixes cannot be removed by guesswork. Connectors name exact instance ports and determine lineage.

2. **Nontrivial row expressions exist in short paths.** `EXP_PRODUCTS` has `PRODUCT_PRICE=PRICE/100`, `PRODUCT_PRICE_CENTS=PRICE`, and `IS_FOOD_ITEM=IIF( UPPER(LTRIM(RTRIM(TYPE))) = 'JAFFLE', 1, 0 )`, plus the BEVERAGE counterpart. `EXP_SUPPLIES` has `SUPPLY_COST=COST/100` and `IS_PERISHABLE=IIF(PERISHABLE = 'Y' OR PERISHABLE = '1', 1, 0)`. Numeric division, nested calls, null conditions and string handling require deliberate translation and tests.

3. **A compact real join path is available.** `STG_SUPPLIES` depends on `RAW_SUPPLIES → SQ_RAW_SUPPLIES` and `RAW_PRODUCTS1 → SQ_RAW_PRODUCTS1`, merged at `JNR_SUPPLIES_PRODUCTS`, then `EXP_SUPPLIES`. Its `Join Condition` is `SKU1 = SKU`; `Join Type` is `Normal Join`. `SKU1` is marked `PORTTYPE="INPUT/OUTPUT/MASTER"`; other incoming supply ports are not master ports. Duplicate product SKUs can multiply matching supply rows and unmatched/null keys need testing.

4. **A compact real aggregation-plus-join path is available.** Core `CUSTOMERS` reads `STG_ORDERS2 → SQ_STG_ORDERS2 → AGG_ORDERS_BY_CUSTOMER` and `STG_CUSTOMERS → SQ_STG_CUSTOMERS`; joins them at `JNR_CUSTOMERS_ORDERS`; applies `EXP_CUSTOMER_METRICS`. The aggregator marks `CUSTOMER_ID` with `EXPRESSIONTYPE="GROUPBY"`, uses `COUNT(ORDER_ID)`, `MIN(ORDERED_AT_DAY)`, `MAX(ORDERED_AT_DAY)` and three `SUM(...)` measures; `Sorted Input="NO"`. The final expression has nested IIF/ISNULL null replacement and returning/new classification. No local-variable port, Router, Sorter or Custom Transformation occurs on this incoming graph.

5. **Outer-join orientation is a high-risk interpretation.** `JNR_CUSTOMERS_ORDERS` has `Join Type="Master Outer Join"`, `Join Condition="CUSTOMER_ID = CUSTOMER_ID1"`; customer ID/name ports are marked MASTER. Do not substitute a familiar Jaffle Shop LEFT JOIN or decide the preserved side from table names. Official Informatica documentation describes master outer as preserving detail rows; before implementation, confirm this against the applicable PowerCenter guide and derive expected unmatched-row behaviour from the supplied port roles. The XML may intentionally differ from a reference model.

6. **Date and sort semantics affect the proposed customer pipeline.** `EXP_ORDERS.ORDERED_AT_DAY` is `TO_DATE(TO_CHAR(ORDERED_AT, 'DD-MM-YY'), 'DD-MM-YY')`; assuming this always means a date cast can hide two-digit-year rules. `SRT_ORDERS` sorts `ORDER_ID` ascending with `Distinct="NO"`, `Case Sensitive="YES"`, `Null Treated Low="NO"`. Relational row-set equality is different from guaranteeing persistent table row order. State the intended comparison and translation boundary explicitly.

7. **Some graphs are stateful.** Core `EXP_CUSTOMER_ORDER_NUM` has local variables `v_PREV_CUSTOMER_ID=CUSTOMER_ID` and `v_ORDER_SEQUENCE=IIF(v_PREV_CUSTOMER_ID = CUSTOMER_ID, v_ORDER_SEQUENCE + 1, 1)`, feeding `CUSTOMER_ORDER_NUMBER`. Upstream `SRT_BY_CUSTOMER` keys include CUSTOMER_ID, ORDERED_AT_DAY and ORDER_ID. Treating this as a stateless expression is unsafe. Enriched `EXP_MARK_FIRST_CUSTOMER` likewise uses previous location/day/customer variables; some other local variables are row-local derived values, so LOCAL VARIABLE alone is not a sufficient statefulness classification.

8. **Custom does not always mean arbitrary executable code.** `UN_REGIONS` and `UN_ORDER_BANDS` are `TYPE="Custom Transformation"` with `TEMPLATENAME="Union Transformation"`, `TEMPLATEID="303001"`, module `pmuniontrans` and function `pmunionfunc`. A precisely recognized union template might be supported later; unknown custom transformations must not be treated as union. `RTR_REGION` has APAC/AMER/EMEA groups and a default group. Group conditions, connections and default routing must be inspected; blindly concatenate branches can lose or duplicate rows.

9. **Runtime parameters and failures are separate semantics.** Enriched recency expressions reference `$$RUN_DATE` and `DATE_DIFF`. Fields include explicit defaults such as `ERROR('Transformation Error')`, `NULL` and `0`; these are not necessarily interchangeable SQL fallbacks. A model-only scope must state which error handling and session/runtime features it does not reproduce.

## PROPOSED complete core for review

Recommendation, not an approved scope or completed capability: five complete target graphs—staging `STG_CUSTOMERS`, `STG_ORDERS`, `STG_PRODUCTS`, `STG_SUPPLIES`; core `CUSTOMERS`. This supplies one connected RAW_CUSTOMERS/RAW_ORDERS → staging → customer-metrics slice, plus independently useful product-expression and normal-join/supply-expression paths. It exercises projection, arithmetic, conditional/function translation, normal join, outer-join orientation and aggregation. It does not claim all 16 targets.

The lowest-risk first complete output is `STG_PRODUCTS`; `STG_SUPPLIES` adds a real normal join; `CUSTOMERS` adds aggregation and an outer join once its exact semantics are verified. Core acceptance must cover generated dbt execution, independently expected rows, changed XML, unmatched/null/duplicate keys, empty groups and declared unsupported cases. If date or join semantics cannot be established in the remaining budget, report the limitation and renegotiate the core explicitly rather than silently promise equivalence.

## PROPOSED optional extensions

- `STG_ORDER_ITEMS`, core `PRODUCTS` and `SUPPLIES`: short projection graphs, useful low-cost coverage after the meaningful core works.
- Core `ORDER_ITEMS`: real additional aggregation/three-join/expression graph with a sorter; lacks local-variable ports, router and custom transformation. Validate sorting/grouping/error semantics before claiming support.
- Enriched `ORDER_ITEM_ENRICHED` and `PRODUCT_DAILY_PERFORMANCE`: no router or custom union on their incoming graphs, but materially larger join/aggregate paths. They still depend on external staged locations unless that path is also supported or declared as an external input.
- `STG_LOCATIONS`, core `ORDERS`, enriched customer/order-financial/store-KPI paths: defer unless recognized union/router, ordering/state and parameter semantics are explicitly implemented and tested.

## Research limitation

This artifact records XML evidence, not a successful PowerCenter runtime comparison. A primary-source search found the master-outer definition in the [Informatica Developer Transformation Guide](https://docs.informatica.com/content/dam/source/GUID-5/GUID-5DAA379B-8659-49FA-949D-5C586920D195/31-2-1/en/IN_1011HF1_DeveloperTransformationGuide_en.pdf); that is supporting terminology, not proof of the supplied export runtime/version. Consult the applicable [PowerCenter Transformation Guide](https://docs.informatica.com/data-integration/powercenter/10-5/transformation-guide/working-with-transformations.html) before finalizing join/date/stateful rules.


## Draft reconciliation against PRD and addendum

Reviewed the current `prd.md` and `addendum.md` on 22 October 2026. The five-target core remains **PROPOSED**. No product code, tests or result measurements were added by this review.

The stated totals, five core dependency graphs, instance aliases and larger-path exclusions match the inspected XML. The proposed customer slice includes its actual staging dependencies (`STG_CUSTOMERS` and `STG_ORDERS`); no locations/router/custom-union/stateful graph is hidden in that slice. There is no material false-coverage or missing-whole-target-dependency claim in the draft. The draft correctly treats date/join interpretation as unresolved acceptance gates rather than proven support.

The following boundaries need precise implementation-contract treatment:

1. **Source Qualifier acceptance is not yet explicit.** Freshly checked all seven qualifier instances reached by the five core targets: staging `SQ_RAW_CUSTOMERS`, `SQ_RAW_ORDERS`, `SQ_RAW_PRODUCTS`, `SQ_RAW_SUPPLIES`, `SQ_RAW_PRODUCTS1`; core `SQ_STG_ORDERS2`, `SQ_STG_CUSTOMERS`. Every one has empty `Sql Query`, `User Defined Join`, `Source Filter`, `Pre SQL` and `Post SQL`; `Select Distinct=NO`; `Number Of Sorted Ports=0`. Their observed core form is simple, but FR-3 must not imply arbitrary qualifier support. Declare this supported attribute profile or implement a broader rule. A mutation adding a filter/SQL override or enabling distinct must change semantics correctly or reject the target visibly; it must never remain an unnoticed passthrough.

2. **Sorter mutation acceptance needs a distinct check type.** FR-6 requests mutation evidence for every core operation category, while A3 excludes row order from result equality. Changing only `SRT_ORDERS` key/direction cannot be required to change an unordered row multiset. Verify the understood sort configuration through SQL/metadata inspection where applicable; use a `Distinct=YES` mutation as either a correctly supported row-count change or an explicit unsupported rejection. Do not present a sort-only result comparison as proof of ordering fidelity, and do not count rejection as added target coverage.

3. **Type, null and default boundaries need executable examples.** The draft names these risks but does not yet define the accepted input domain or conversion rules. The supplied core includes floating and decimal ports, `number(p,s)` target precision/scale, NULL/zero/ERROR output defaults, and Oracle-backed sources. Decide how numeric casting/rounding, empty strings and expression-error defaults are represented in the controlled source data and generated SQL. In particular, determine whether a port default applies to null values, evaluation errors or another condition before translating it. Excluding PowerCenter row-error routing does not authorize invented `COALESCE` fallbacks. Test the chosen valid-input boundary and fail/reject outside it where equivalence cannot be supported.

4. **Pending semantic gates remain binding.** The two-digit-year date round trip and master/detail preservation are not resolved by passing tests whose expected values were chosen using the same unverified assumption. Establish the rule from appropriate primary evidence, record any bounded domain assumption, and independently specify boundary/unmatched-row expectations. If this cannot be done within the remaining time, obtain an explicit scope change rather than count either affected target as complete.

These are semantic and verification clarifications for the next native contract, not newly approved features or a recommendation to enlarge the five-target core.
