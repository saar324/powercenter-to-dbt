# Core semantics check

22 October 2026. Bounded source review for architecture preparation. The five approved target ancestor graphs were inspected directly in the [unchanged XML](../fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml). No converter, dependency environment or semantic tests were run. Recommendations below are engineering rules to implement and verify, not measured PowerCenter equivalence or new owner decisions.

## Reached operations, functions and metadata

The selected paths reach seven Source Qualifiers, four Expressions, two Joiners, one Aggregator and one Sorter. Source Qualifiers have empty SQL/filter overrides and distinct disabled. Functions reached in expressions are `IIF`, `ISNULL`, `UPPER`, `LTRIM`, `RTRIM`, `TO_CHAR`, `TO_DATE`, `COUNT`, `MIN`, `MAX`, `SUM`; `ERROR('transformation error')` also occurs in output defaults. Operators include `/`, `=`, `>`, and `OR`. No local-variable state, Router or Custom Transformation is reached.

| Location | Exact relevant port metadata/defaults |
|---|---|
| `EXP_ORDERS` | Subtotal/tax and their cents outputs: `double(15,0)`. `ORDER_TOTAL`: `decimal(12,2)`; `ORDER_TOTAL_CENTS`: `decimal(12,0)`, despite its target `(12,2)`. `ORDERED_AT_DAY`: `date/time(29,9)`. All output-only defaults are `NULL`. |
| `EXP_PRODUCTS` | Price and cents outputs: `double(15,0)`; flags: `integer(10,0)`; strings: lengths 50/100/500. Output defaults `NULL`. Target price connectors cross the expression port names. Target `PRODUCT_PRICE_CENTS` records numeric precision 15, scale 0; `PRODUCT_PRICE` records `(12,2)`. |
| `EXP_SUPPLIES` | Cost/cents: `double(15,0)`; flag: `integer(10,0)`. Cost default `0`; cents default `ERROR('transformation error')`; flag default `0`; string outputs default `NULL`. Cost targets record `(12,2)`. |
| `AGG_ORDERS_BY_CUSTOMER` | `COUNT(ORDER_ID)` output `decimal(10,0)`; spending/tax sums `decimal(12,2)`; date extrema `date/time(29,9)`. All aggregate-output defaults are `ERROR('transformation error')`. Group port `CUSTOMER_ID` has empty default. |
| `EXP_CUSTOMER_METRICS` | Clean order count `decimal(10,0)`; clean sums `decimal(12,2)`; customer type string length 20. These computed outputs have `ERROR('transformation error')` defaults. Pass-through fields have empty defaults. |

**Closed prior gap:** both staging and core sessions explicitly set `Enable high precision="NO"`; each references `default_session_config`. This is recorded export configuration, not proof of the original service's actual runtime configuration. Do not describe the export's high-precision setting as missing.

## Join rules

**Recorded graph:** supplies/products uses `Normal Join`, condition `SKU1 = SKU`; the product input is master. Customers uses `Master Outer Join`, condition `CUSTOMER_ID = CUSTOMER_ID1`; customer fields are master, grouped orders detail.

**Recommended translation:** normal join becomes an inner equality join; master outer preserves every detail/grouped-orders row with matching master/customer rows. Use detail-left/master-right or equivalent master-right-join SQL. Do not substitute a customer-preserving left join. Unmatched order groups retain metrics but produce null master customer fields. In particular, downstream `CUSTOMER_ID` comes from the master port; do not fill it with the detail key by an invented `COALESCE`.

Preserve duplicate-key multiplication and use ordinary equality, not null-safe equality. Verify matched, master-only, detail-only, duplicate and null-key cases. The [official Developer Transformation Guide 10.1.1HF1](https://docs.informatica.com/content/dam/source/GUID-5/GUID-5DAA379B-8659-49FA-949D-5C586920D195/31-2-1/en/IN_1011HF1_DeveloperTransformationGuide_en.pdf), printed pp.318/323, documents null nonmatching and join preservation. [Official Cloud Data Integration join documentation](https://docs.informatica.com/content/dam/source/GUID-2/GUID-2B5E2342-3D75-4BCE-B092-A78F85631717/17/en/CDI_Spring2020September_Transformations_en.pdf), pp.160–161, corroborates normal/detail/master behavior. These are related Informatica products, not exact PowerCenter runtime confirmation. The [PowerCenter 10.5 master-outer page](https://docs.informatica.com/data-integration/powercenter/10-5/transformation-guide/joiner-transformation/defining-the-join-type/master-outer-join.html) and normal-join page still returned HTTP 403 in this check; retain this evidence limit.

## Three-argument IIF and empty strings

All reached `IIF` calls have three arguments. Use structured `CASE WHEN condition THEN true_value ELSE false_value END`: null conditions select the explicit false branch. `ISNULL(x)` becomes an explicit null predicate. Product flags and supply perishability return 0 for null comparison inputs; the customer clean metrics select 0 for null aggregates.

The [PowerCenter 10.1.1 language reference](https://docs.informatica.com/content/dam/source/GUID-B/GUID-B280EAC3-3E82-40EB-923E-61F1F72E2DC4/20/en/PC_1011_TransformationLanguageReference_en.pdf), IIF p.96, explicitly shows null comparison inputs taking the false result. This supports these pure reached branches; it does not prove general eager/lazy branch or error-evaluation equivalence. Do not add support for omitted false arguments from this subset.

[Oracle 19c storage rules](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Nulls.html) treat empty character values as null; the [PowerCenter 10.4 language reference](https://docs.informatica.com/content/dam/source/GUID-B/GUID-B280EAC3-3E82-40EB-923E-61F1F72E2DC4/23-1-5/en/PC_1040_TransformationLanguageReference_en.pdf), p.19, distinguishes intermediate NULL from empty string. Model Oracle source/target normalization only at declared storage boundaries, not with blanket `NULLIF` after every expression. Trimming a spaces-only string can produce an intermediate empty string. Test null, empty and spaces separately; preserve ordinary string identity and declare the supported character/collation profile rather than claim arbitrary code-page equivalence.

## Numeric and default boundaries

Carry source, expression-port and target metadata separately. `double` scale 0 does not make it an integer; conversely the explicit decimal cents port `(12,0)` cannot be silently treated as `(12,2)`. Target conversion is a separate step, especially for crossed product-price fields. [Oracle numeric rules](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Data-Types.html) distinguish bare `NUMBER` from `NUMBER(p,s)`, round excess scale and reject excess precision. XML metadata is not independent verification of live Oracle DDL; state how exported precision/scale is interpreted.

Use declared double arithmetic for reached double ports and bounded decimal conversion for declared decimal ports; independently check small positive/negative cents, half-rounding, nulls, sums and precision limits. Do not claim exact high-precision decimal arithmetic merely by casting inputs: [DuckDB decimal division](https://duckdb.org/docs/2.0/sql/data_types/numeric) uses floating-point results. Actual adapter/database versions and cast behavior must be verified during Build.

Defaults on output ports handle transformation errors, not every legitimate null result. Therefore `DEFAULTVALUE="0"` is not a license to coalesce every input/result null. The [official Informatica Developer guide](https://docs.informatica.com/content/dam/source/GUID-5/GUID-5DAA379B-8659-49FA-949D-5C586920D195/31/en/IN_1011_DeveloperTransformationGuideTransformationGuide_en.pdf), p.46, distinguishes null-input defaults and output-error defaults; [Informatica's PowerCenter example](https://marketplace.informatica.com/listings/on-premise/data-integration/mapping_capture_invalid_records_in_bad_file.html) confirms replacing an output error with NULL as an intentional configuration. Full row rejection/recovery/logging remains outside the agreed core: reject unsupported error-producing expression variants or fail visibly on declared out-of-domain values; do not pretend whole-query failure reproduces per-row handling.

## Two-digit-year date round trip

The reached expression is exactly `TO_DATE(TO_CHAR(ORDERED_AT, 'DD-MM-YY'), 'DD-MM-YY')`, output default `NULL`. The [PowerCenter 10.2HF2 language reference](https://docs.informatica.com/content/dam/source/GUID-B/GUID-B280EAC3-3E82-40EB-923E-61F1F72E2DC4/23-1-2/en/PC_102HF2_TransformationLanguageReference_en.pdf), Dates p.40, shows YY resolving within the evaluation century: year 98 evaluated in 2003 becomes 2098. The [PowerCenter 10.1.1 reference](https://docs.informatica.com/content/dam/source/GUID-B/GUID-B280EAC3-3E82-40EB-923E-61F1F72E2DC4/20/en/PC_1011_TransformationLanguageReference_en.pdf), TO_DATE p.199, shows midnight when time is omitted and NULL input producing NULL. These indexed excerpts are versioned documentation, not an executed source-runtime oracle.

Recommended rule: retain day/month and two-digit year, reconstruct in the current evaluation century, and discard time. Use the actual runtime clock/context; controlled tests inject a context. No fixed production year or required user-facing run-year flag is approved. DuckDB's ordinary `%y` parsing pivot must not be assumed equivalent.

Check century changes, midnight, null and leap-day cases. A date such as 2000-02-29 can become invalid when evaluated in the 2100s. The reached output's NULL error default supports evaluating a guarded date conversion with NULL fallback, subject to the documented output-default policy; do not generalize it to ERROR-default ports. Validate exact invalid-date/default interaction before counting this boundary verified; otherwise state that boundary as unverified rather than silently normalizing the date.

## Remaining concrete verification work

Architecture can use the bounded rules above. Build must verify type conversions and rounding against the declared export-metadata policy, error-default handling for the reached operations, controlled evaluation-century behavior and supported string/collation assumptions. Related-product joins and older PowerCenter function references remain explicitly version-bounded evidence. No owner terminology quiz or generic research expansion is needed; raise only a newly evidenced blocker that changes the agreed support boundary.

## Build review: integer ranges

The official [PowerCenter 10.2 Data Validation Option guide, datatype reference p.212](https://docs.informatica.com/content/dam/source/GUID-B/GUID-B929434E-CCDE-41DA-BC4A-8C6847BBAE21/11/en/PC_102_DataValidationOptionUserGuide_en.pdf) lists transformation integer as signed 32-bit, small integer as -32768 through 32767, and bigint as signed 64-bit. The indexed official [PowerCenter 10.5 Designer Guide](https://docs-test.informatica.com/content/dam/source/GUID-B/GUID-B54ED1F4-60B8-4F11-8E22-48C4BECE109A/32/en/PC_1050_DesignerGuide_en.pdf) corroborates the integer/bigint bounds; direct PDF fetch returned an unsupported content-type in this check. The Build audit demonstrated that mapping every integer family to BIGINT missed overflow behavior. Preserve the distinct casts and verify endpoints, overflow and output-default behavior. This is versioned documentation, not an executed PowerCenter oracle.

## Owner calculations review: null arithmetic

The indexed official [PowerCenter10.2HF2 Transformation Language Reference, Arithmetic Operators p.26](https://docs.informatica.com/content/dam/source/GUID-B/GUID-B280EAC3-3E82-40EB-923E-61F1F72E2DC4/23-1-2/en/PC_102HF2_TransformationLanguageReference_en.pdf) states that arithmetic with a null yieldsNULL; official10.4 excerpts corroborate this. D54 referenced10.5.6, whose direct PDF fetch was inaccessible to the coordinator. Apply null propagation before checking for denominator zero. Actual DuckDB before/after evidence and the scoped source-runtime limit are in the native Build record and measured report.
