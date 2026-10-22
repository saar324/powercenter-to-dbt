# SQL semantics and testing

Research date: **22 October 2026**. This is pre-approval research, not an implementation choice or measured result. No converter tests or reference projects were run. Local XML inspection confirmed the expressions, port types, Joiner roles and Sorter settings discussed below.

## Evidence and access limits

Official web pages were read where accessible. Informatica's exact [PowerCenter 10.5 Master Outer Join page](https://docs.informatica.com/data-integration/powercenter/10-5/transformation-guide/joiner-transformation/defining-the-join-type/master-outer-join.html) and [10.5.6 IIF page](https://docs.informatica.com/data-integration/powercenter/10-5-6/transformation-language-reference/functions/iif.html) returned **403 Forbidden**. Direct PDF opening also failed. Relevant official PDF search excerpts were available; these were read as excerpts, not full manuals. Their stated releases are evidence boundaries, not the supplied export's verified application version.

DuckDB's stable links redirected to **2.0 documentation** during research. Lock and record the actual runtime version later; do not assume a documented 2.0 capability exists in an older installed dependency.

## Joins: preserve the correct input

**Observed XML:** `JNR_CUSTOMERS_ORDERS` uses `Master Outer Join`; customer fields have `MASTER` port roles. Names such as “customers” do not determine the preserved side.

**Verified related-product rule:** Informatica's [10.1.1HF1 Developer Transformation Guide, Join Types, p.323](https://docs.informatica.com/content/dam/source/GUID-5/GUID-5DAA379B-8659-49FA-949D-5C586920D195/31-2-1/en/IN_1011HF1_DeveloperTransformationGuide_en.pdf) says master outer retains detail rows plus matching master rows; detail outer retains master rows plus matching detail rows. This is the Developer/Data Integration Service guide, not exact-version PowerCenter confirmation.

**Implication and gap:** do not substitute familiar Jaffle Shop customer-preserving SQL. Confirm the applicable PowerCenter rule or explicitly bound the assumption before support. Build independent rows with one match, one master-only key and one detail-only key. Add duplicate keys and null keys. State the expected preserved rows before generating SQL; inspect the complete downstream result, including which customer identifier remains available after the join. A test merely asserting “left join exists” cannot establish correctness.

## Numbers: expression types matter

**Observed XML:** order subtotal/tax outputs are `double`; order total is `decimal(12,2)`. All divide by 100. Product and supply calculations also divide by 100. One uniform floating-point or decimal treatment would discard these distinctions.

**Verified DuckDB rule:** ordinary fixed-point division uses floating-point arithmetic, although decimal addition/subtraction/multiplication can remain exact. Casting inputs to DECIMAL therefore does not by itself establish exact division. [DuckDB numeric types, Arithmetic and Internal Representation](https://duckdb.org/docs/2.0/sql/data_types/numeric).

**Remaining source gap:** exact PowerCenter calculation precision, session high-precision mode and output-port conversion behavior need confirmation. Related Informatica engine documentation cannot silently substitute for that evidence.

**Proposed tests:** independently specify cents-to-currency results for 0, 1, 101, negative values, null and a declared precision boundary. Check values and output types; test rounding/overflow boundaries separately. Exact decimal expected values should not be computed with binary floats. Any floating-point tolerance must follow a stated rule, not hide a large discrepancy. Test totals after aggregation as well as individual rows.

## Nulls, empty strings and IIF

**Verified distinction:** Oracle 19c treats zero-length character values as null. [Oracle SQL Reference, Nulls](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Nulls.html). PowerCenter 10.4's language reference explicitly distinguishes NULL from empty strings and numeric zero. [PowerCenter 10.4 Transformation Language Reference, NULL, p.19](https://docs.informatica.com/content/dam/source/GUID-B/GUID-B280EAC3-3E82-40EB-923E-61F1F72E2DC4/23-1-5/en/PC_1040_TransformationLanguageReference_en.pdf). Oracle source/storage behavior is not automatically Informatica intermediate-expression behavior.

PowerCenter 10.1.1 documents optional IIF false branches with defaults dependent on result type: numeric zero, string empty string or datetime NULL. Its example sends a null comparison input to the omitted false result. [PowerCenter 10.1.1 Transformation Language Reference, IIF, p.96](https://docs.informatica.com/content/dam/source/GUID-B/GUID-B280EAC3-3E82-40EB-923E-61F1F72E2DC4/20/en/PC_1011_TransformationLanguageReference_en.pdf).

**Proposed tests:** the actual product expression must distinguish `' jaffle '`, `'BEVERAGE'`, another string, empty string and null. Supply tests exercise both OR alternatives and null. Three-argument IIF-to-CASE is a translation candidate, not proof of identical branch evaluation, coercion or errors. Reject unverified error-producing branches/defaults rather than silently replacing them with NULL or COALESCE.

## Dates: the century can change

**Observed XML:** `TO_DATE(TO_CHAR(ORDERED_AT,'DD-MM-YY'),'DD-MM-YY')` discards time and the original century when formatting. It is not automatically a date cast.

PowerCenter 10.2's documented example parses year `01` as 1901 when the current year is 1998 using `YY`, while `RR` returns 2001. [PowerCenter 10.2 Transformation Language Reference, Dates, p.38](https://docs.informatica.com/content/dam/source/GUID-B/GUID-B280EAC3-3E82-40EB-923E-61F1F72E2DC4/22/en/PC_102_TransformationLanguageReference_en.pdf). Oracle independently documents YY as using the current century; RR has different century rules. [Oracle Format Models, RR section](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Format-Models.html).

**Proposed tests:** declare the evaluation century; include 1999, 2000, 2049, 2050, leap day, null and non-midnight timestamps. Under a current-century YY interpretation, 1999 can become 2099: preserve the XML rule, not its presumed business intention. Define behavior for dates that become invalid after century replacement, or reject that range. Exact-release parsing/error behavior remains a boundary.

## Verification method and reporting

dbt supports unit tests with static inputs and expected SQL-model output; availability starts at v1.8. [dbt unit tests](https://docs.getdbt.com/docs/build/unit-tests). Use the approved pytest/dbt execution setup without requiring a second parallel test framework. [pytest parametrization](https://docs.pytest.org/en/stable/how-to/parametrize.html) supports named condition matrices; [assertions](https://docs.pytest.org/en/stable/how-to/assert.html) expose actual mismatches and expected errors.

Compare complete **bags** of rows: duplicates matter. Ordinary EXCEPT removes duplicates; EXCEPT ALL retains multiplicity. [DuckDB set operations](https://duckdb.org/docs/2.0/sql/query_syntax/setops). Joins/grouping do not guarantee input order. [DuckDB order preservation](https://duckdb.org/docs/2.0/sql/dialect/order_preservation). Check Sorter keys/directions/settings separately from unordered result equality; reject unsupported distinct/stateful behavior.

Mutate XML names, expressions, join roles and sorting settings; specify expected changes independently. Differential comparison against a reference is useful only with matching schemas, inputs and rules. Unsupported mutations must fail visibly. Follow the [native reporting contract](../_bmad-output/specs/spec-powercenter-to-dbt/validation-and-reporting.md): actual runs only, separate outcome/result/coverage denominators, final tested revision identified, earlier failures retained and practical **evidence → change → acceptance test** next steps. Small passing samples do not establish universal accuracy.
