# Source compatibility and reference boundaries

## Confirmed context

The written exercise concerns Informatica PowerCenter mapping XML. Saar reports that the company also wants broader conversion across products. Preserve that direction as practical future work; it does not establish that arbitrary XML carries interchangeable transformation meaning.

XML standardizes document syntax. Element names and application semantics are outside that standard. There is no verified fixed set of eight ETL export layouts; that number was Saar's hypothetical example. [W3C XML specification](https://www.w3.org/TR/xml/).

PowerCenter can export selected repository objects and their dependencies. One XML file can contain several mappings, sessions and workflows; it need not represent the entire system. [PowerCenter Repository Guide, chapter 11](https://docs.informatica.com/content/dam/source/GUID-1/GUID-11B6F8F7-0FDC-4B5C-87B4-FCDD4C933B23/17/en/PC_102_RepositoryGuide_en.pdf).

The PowerCenter 10.2HF1 guide limits vendor-supported repository export/import to the same version. This is an import-support rule, not proof that every release changes XML syntax or that a converter cannot support several releases. Compatibility with other exports requires evidence. Do not infer the supplied export's version from the version of documentation consulted. [Official guide, chapter 11, page 125](https://docs.informatica.com/content/dam/source/GUID-1/GUID-11B6F8F7-0FDC-4B5C-87B4-FCDD4C933B23/18/en/PC_102HF1_RepositoryGuide_en.pdf).

Microsoft SSIS provides a concrete second example: its DTSX2 specification describes a versioned XML format and calls version 2 an enhanced refactoring of version 1. Shared XML syntax therefore does not establish shared export structure or transformation rules. [Microsoft DTSX2 introduction](https://learn.microsoft.com/en-us/openspecs/sql_data_portability/ms-dtsx2/39efc022-1b2b-4538-8656-d147845d9135).

## Design consideration, not a selected architecture

Evaluate source-specific readers feeding a shared representation of transformations and a dbt SQL generator after establishing the PowerCenter core. Configuration can express names and simple layout differences. Translation rules and tests must establish the meaning of expressions, joins, nulls, data types, ordering and runtime behavior. Similar tags alone do not justify grouping readers.

Some custom transformations or scripts have no direct SQL equivalent. Future support may require a supported rewrite, external execution or explicit rejection; configuration alone does not guarantee deterministic equivalent SQL.

Record the source product, available export/version evidence and tested fixtures for each supported reader. Distinguish known unsupported input from unverified input. Do not claim support by filename extension or silently process unknown semantics.

## Jaffle Shop variants

These are related teaching projects using a shared fictional business name, not different real clients. The assignment's [DuckDB reference](https://github.com/dbt-labs/jaffle_shop_duckdb) uses the classic customers/orders/payments example. [Infinite Lambda's README](https://github.com/infinitelambda/flowline-pwc-demo) instead links [modern Jaffle Shop](https://github.com/dbt-labs/jaffle-shop) and lists customers, orders, items, products, supplies and stores.

U89–U90 require executed reference comparison in the minimum. Pin and execute the assignment-linked classic project and an evidenced historical modern candidate. Align source data explicitly; preserve original model SQL. Use equivalent schemas/rules for scored converter-correctness comparisons. Report literal cross-project differences separately when rules differ, including non-comparable fields and projected rather than complete outputs. Controlled independent expected results remain required for XML-specific behavior and do not replace reference execution. Do not describe mismatched project variants as a proven converter defect. See research/07-reference-version-correlation.md for the bounded historical investigation when available.

## Converter implementation stack

Saar clarified in U26 that U25 concerned the converter's own implementation stack. The agent's prior interpretation as a request to consider Python/hybrid dbt output was incorrect and is superseded. SQL output remains the task target. Saar approved the proposed Python stack on 22 October 2026 in U28. The preference for avoiding unnecessary language mixing applies to the converter.

The following comparison is engineering judgment for this exercise, not measured implementation performance.

| Option | Fit and tradeoff |
|---|---|
| Python | Selected for a small XML-to-SQL command-line tool: built-in XML, typed data structures and CLI facilities, plus direct access to Python database/testing tools. Keep modules explicit and verify semantics with result tests. |
| TypeScript / Node.js | Strong alternative when TypeScript familiarity or integration with an existing Node product is the priority. Types can express the transformation structure; choose an XML package and SQL-generation approach. Existing npm files serve BMAD and do not commit the converter to Node. |
| Go | A reasonable choice when distributing a compiled executable is a priority. It has standard XML support; that distribution benefit is not a requirement of this exercise. |

Approved stack: Python 3.13; uv for isolated locked dependencies; standard-library ElementTree for XML, dataclasses/type hints for mapping structures, argparse for CLI, and a small explicit SQL emitter for supported operations. Add a parsing/emission library only if the selected expression/dialect requirements justify it. Do not assume generic SQL parsing translates Informatica expression semantics automatically.

Use pytest for converter tests, DuckDB for local result checks and dbt-duckdb for actual dbt model execution. CSV and Markdown reports use standard Python file/CSV facilities. These test tools do not imply that the converter needs a running database to translate XML. Pin compatible dependency versions during setup; approval alone does not mean dependencies are installed or compatibility tests have run. Saar subsequently approved DuckDB as the output SQL dialect in U51; other output dialects are future work.

The relevant standard facilities and tools are documented in [ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html), [argparse](https://docs.python.org/3/library/argparse.html), [uv](https://docs.astral.sh/uv/), [pytest](https://docs.pytest.org/en/stable/), [dbt-duckdb](https://github.com/duckdb/dbt-duckdb), [TypeScript](https://www.typescriptlang.org/docs/) and [Go encoding/xml](https://pkg.go.dev/encoding/xml).

Background from the user's reading: dbt Core introduced Python models in version 1.3, and their package/runtime support depends on the platform/adapter. That capability does not require generating Python models or dictate the converter language. [Official introduction](https://www.getdbt.com/blog/introducing-support-for-python), [current Python model documentation](https://docs.getdbt.com/docs/build/python-models).

## Practical future work

These are candidate extensions, not observed implementation defects or committed extra scope. The final report must replace generic risks with actual evidence where available.

| Boundary | Concrete next work | Acceptance evidence |
|---|---|---|
| Unverified PowerCenter release | Obtain a representative export and inspect its structural and semantic differences; add only the required compatibility rules. | Convert the versioned fixture and compare complete expected results, or produce an explicit unsupported diagnostic. |
| Additional source product | Obtain one official format specification and a representative nontrivial mapping; implement a reader for its supported operations. | Equivalent source examples produce the same independently expected result in the target database. |
| Unsupported operation | Specify one operation's type/null/order rules and implement its translation where SQL can preserve them. | Focused edge cases and a complete path pass; unsupported variants remain clearly rejected. |

Research recorded on 22 October 2026; a consulted document is evidence about its stated product/version, not a blanket support claim.

## Approved conversion and preparation boundaries

The adopted PRD and addendum preserve the approved target minimum and complete-path requirements. The five targets are verification fixtures, not an output allowlist: reusable supported rules must work for other targets, with additional result checks before claiming verified support. Dependency analysis lives in a separate Python file (U59).

Generate equivalent dbt preparation steps for supported XML setup commands, including the supplied customer cleanup (U57). Resolve generated relation names and verify materialization/lifecycle compatibility, command order and stale-row removal on repeated local runs. Do not execute imported SQL while converting XML or claim arbitrary workflow support. Unconverted commands are explicitly reported.

No user-facing run-year setting is approved. Clock/context-dependent tests must record controlled evaluation context; production date semantics must follow the researched source rules rather than a silently fixed 2026 year. Exact date/join/numeric/null/error boundaries require evidence before implementation or support claims.
