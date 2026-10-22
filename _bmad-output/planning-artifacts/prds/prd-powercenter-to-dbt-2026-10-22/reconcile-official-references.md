# Official reference reconciliation

Research date: 22 October 2026. Reference evidence for PRD review, not implementation approval or a claim that any conversion has been tested. The supplied assignment remains authoritative for requested work. This extract adds no product requirements.

## Read scope and access

| Supplied reference | Material inspected | Access / scope |
| --- | --- | --- |
| [PowerCenter 10.5 mappings overview](https://docs.informatica.com/data-integration/powercenter/10-5/designer-guide/mappings/mappings-overview.html) | Direct request; targeted indexed passages from the official [10.5 Designer Guide PDF](https://docs.informatica.com/content/dam/source/GUID-B/GUID-B54ED1F4-60B8-4F11-8E22-48C4BECE109A/30/en/PC_1050_DesignerGuide_en.pdf), chapter 5 | HTML and PDF direct fetch returned 403. Indexed official passages were available; the full guide was not read. An official docs-test PDF mirror returned an unsupported content-type in the browser tool. |
| [PowerCenter 10.5 Transformation Guide preface](https://docs.informatica.com/data-integration/powercenter/10-5/transformation-guide/preface.html) | Preface/navigation; targeted indexed contents of [Working with Transformations](https://docs.informatica.com/data-integration/powercenter/10-5/transformation-guide/working-with-transformations.html) | Preface loaded; detailed overview and subsequent direct chapter fetch returned 403. The full transformation guide and individual operator semantics were not read. |
| [What is dbt](https://docs.getdbt.com/docs/introduction) | Relevant introduction/framework body | Targeted reading, not all linked documentation. |
| [About dbt models](https://docs.getdbt.com/docs/build/models) | Models and project explanation | Relevant page body inspected. |
| [SQL models](https://docs.getdbt.com/docs/build/sql-models) | Model files, execution, model dependencies, testing/documentation links | Targeted sections; linked test/reference documentation not exhaustively read. |
| [Quickstart guides](https://docs.getdbt.com/guides) | Guide index | Index inspected; no quickstart executed and no claim that all tutorials were read. |
| [Jaffle Shop DuckDB](https://github.com/dbt-labs/jaffle_shop_duckdb) | README overview/setup sections; complete customers.sql and orders.sql; targeted requirements.txt | Relevant source inspected; no clone/build/test execution and no exhaustive repository review. |
| [Modern Jaffle Shop](https://github.com/dbt-labs/jaffle-shop), linked by upstream | Relevant README sections; complete dbt_project.yml | Targeted inspection; not the full project. A seed-directory browser request failed. |
| [Infinite Lambda demo](https://github.com/infinitelambda/flowline-pwc-demo) | Complete short upstream README | Source description inspected. XML analysis belongs to the separate fixture evidence, not this web extract. |

These access limits mean this record supports orientation and compatibility caveats. It does not establish precise correctness rules for every PowerCenter transformation.

## PowerCenter concepts relevant to conversion

The official 10.5 Designer Guide's indexed mapping passages describe linked source, transformation and target objects, exporting mappings to XML, and source-column dependencies. A mapping is therefore more than a list of column names: links identify where values travel. The guide also discusses multiple target load-order groups. A multi-target export cannot be assumed to equal one output query. [Designer Guide, chapter 5](https://docs.informatica.com/content/dam/source/GUID-B/GUID-B54ED1F4-60B8-4F11-8E22-48C4BECE109A/30/en/PC_1050_DesignerGuide_en.pdf).

The 10.5 Transformation Guide contents distinguish expressions, aggregate expressions and group-by ports, filters and null values, join types, router groups, custom procedures, and other transformation families. These headings establish separate semantics to investigate; they do not establish that a generic SQL substitution preserves each behaviour. [Working with Transformations](https://docs.informatica.com/data-integration/powercenter/10-5/transformation-guide/working-with-transformations.html).

For the basic definition only, targeted official 10.2HF1 guide passages state that transformations generate, modify or pass data, with linked ports carrying values; the Integration Service performs their operations. This older source is contextual evidence, not proof of exact 10.5 behaviour. [Transformation Guide, overview pp24 onward](https://docs.informatica.com/content/dam/source/GUID-8/GUID-8C8FEE2A-EB08-4723-BCF2-1F87C12A9341/28-1-2/en/PC_102HF1_TransformationGuide_en.pdf).

### Join preservation risk raised by fixture inspection

Official indexed Informatica documentation defines **Master Outer** as retaining every detail row and matching master rows; **Detail Outer** retains every master row and matching detail rows. Thus a field marked MASTER does not imply that Master Outer preserves its unmatched rows. This matters when interpreting `JNR_CUSTOMERS_ORDERS`: a customer-preserving left join cannot be inferred from that label. The fixture analyst supplied the node/port observation; this research did not independently re-audit the XML. [Official 10.5 Mapping Specification Guide, chapter3 p32](https://docs.informatica.com/content/dam/source/GUID-7/GUID-756A93D0-F0EE-4F8E-8737-0A8470125468/20/en/IN_105_MappingSpecificationGuide_en.pdf), [official 10.1.1HF1 Developer Transformation Guide, Join Types](https://docs.informatica.com/content/dam/source/GUID-5/GUID-5DAA379B-8659-49FA-949D-5C586920D195/31-2-1/en/IN_1011HF1_DeveloperTransformationGuide_en.pdf).

Read scope: targeted indexed join descriptions only. Both are official related-product evidence; the exact [PowerCenter10.5 Master Outer page](https://docs.informatica.com/data-integration/powercenter/10-5/transformation-guide/joiner-transformation/defining-the-join-type/master-outer-join.html) and [PowerCenter10.5 Transformation Guide PDF](https://docs.informatica.com/content/dam/source/GUID-8/GUID-8C8FEE2A-EB08-4723-BCF2-1F87C12A9341/30/en/PC_105_TransformationGuide_en.pdf) returned403. Therefore this is a strongly supported semantic risk, with exact PowerCenter10.5 verification still limited by source access; no runtime comparison has been performed.

## dbt concepts relevant to the output

dbt describes transformation of data in the configured data platform and separates its language/project from the engine that compiles and executes the transformation graph. It also provides testing and documentation facilities. These capabilities do not themselves prove our generated queries preserve PowerCenter results. [Introduction](https://docs.getdbt.com/docs/introduction).

A SQL model is a select statement in a model file. A project contains configuration and can contain several models that reference each other. dbt normally builds a SQL model by wrapping its query in a view/table creation statement. `ref` supplies model dependencies and resolves environment-specific relation names. Therefore generating SQL, resolving a dbt project and checking result equivalence are distinct checks. [Models](https://docs.getdbt.com/docs/build/models), [SQL model files, execution and dependencies](https://docs.getdbt.com/docs/build/sql-models).

The quickstart URL is a changing guide index with several environments and version tracks. Its presence in the brief does not select a cloud platform, require a hosted account, or establish a specific project runtime version. [Guide index](https://docs.getdbt.com/guides).

## Reference-project mismatch

The assignment-linked DuckDB project describes a fictional ecommerce store whose raw data is customers, orders and payments. Its inspected customer model uses payment totals for lifetime value; its order model aggregates payment amounts by method. The README explicitly calls the project a small self-contained playground and says its use of seeds instead of sources is for convenience. It is useful reference evidence, not a production-design requirement. [README](https://github.com/dbt-labs/jaffle_shop_duckdb), [customers.sql](https://github.com/dbt-labs/jaffle_shop_duckdb/blob/duckdb/models/customers.sql), [orders.sql](https://github.com/dbt-labs/jaffle_shop_duckdb/blob/duckdb/models/orders.sql).

Infinite Lambda's README instead links to the modern Jaffle Shop and lists customers, orders, items, products, supplies and stores, three mappings and a workflow. It describes a RAW → staging → core → enriched pipeline targeting Oracle. These related demo projects do not establish interchangeable schemas or identical business rules. Comparing outputs requires matching actual inputs, columns and transformations first; the discrepancy is evidence to reconcile, not permission to hard-code either project's SQL. [Upstream README](https://github.com/infinitelambda/flowline-pwc-demo).

At inspection, modern Jaffle Shop's project file required dbt >=2.0.0. The DuckDB reference's requirements file listed dbt-core 1.12.5 and dbt-duckdb 1.11.0. These are mutable upstream observations, not selected dependencies or a tested compatible environment for our repository. [Modern project config](https://github.com/dbt-labs/jaffle-shop/blob/main/dbt_project.yml), [DuckDB requirements](https://github.com/dbt-labs/jaffle_shop_duckdb/blob/duckdb/requirements.txt).

## Format and version extension caveats already raised by the user

XML standardizes syntax, not application element names or meaning. Valid XML from two ETL products is not necessarily the same language. There is no verified fixed catalogue of eight shared ETL XML formats. [W3C XML specification, section 3](https://www.w3.org/TR/xml/).

Official PowerCenter 10.2HF1 repository documentation states that vendor-supported repository-object export/import is between repositories of the same version. That support restriction does not prove every release changes grammar or that a separate converter cannot support several versions. No cross-version converter support has been verified here. [Repository Guide, chapter11 p125](https://docs.informatica.com/content/dam/source/GUID-1/GUID-11B6F8F7-0FDC-4B5C-87B4-FCDD4C933B23/18/en/PC_102HF1_RepositoryGuide_en.pdf).

As a concrete second-product example, Microsoft documents SSIS DTSX as an XML-based data-flow format and calls version2 an enhanced refactoring of version1. This substantiates the user's concern about product-specific and version-specific interpretation. It does not establish SSIS support, nor a requirement to implement it in this exercise. [DTSX specification](https://learn.microsoft.com/en-us/openspecs/sql_data_portability/ms-dtsx/235600e9-0c13-4b5b-a388-aa3c65aec1dd), [DTSX2 introduction](https://learn.microsoft.com/en-us/openspecs/sql_data_portability/ms-dtsx2/39efc022-1b2b-4538-8656-d147845d9135).

## Draft reconciliation

Reviewed the written [PRD](prd.md) and [addendum](addendum.md) against this reference extract on 22 October 2026. **No material source-reconciliation gaps found.** This checks the draft's use of sources; it is not approval of proposed scope or product validation.

- The PRD links this extract for targeted read scope and access limits. The addendum explicitly qualifies the Master Outer rule as related official Informatica evidence, notes the PowerCenter10.5 access failure, and requires the applicable rule and unmatched-row expectations to be established before support is claimed. It does not assert that customer-side master ports imply customer-preserving output or that a PowerCenter runtime comparison occurred.
- Both documents preserve the classic/modern Jaffle Shop schema and rule mismatch. Reference comparison requires matched inputs and rules, with independent expected data as an alternative. Neither reference is described as already executed or interchangeable.
- Upstream version observations remain evidence rather than selected dependencies. The addendum requires locking and verifying the actual environment later, and correctly distinguishes export repository-version metadata from a verified PowerCenter application release.
- Arbitrary XML and universal cross-vendor/version conversion remain outside the exercise scope. Future readers and version fixtures are proposals requiring semantics and tests; the same-version vendor-import restriction is not overstated as proof that every grammar changes.
