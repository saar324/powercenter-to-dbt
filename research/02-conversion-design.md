# Conversion design research

22 October 2026. Primary-source review for a design decision before implementation. Findings below describe mature project practices; **applicability paragraphs are unapproved recommendations**, not new scope or completed capabilities. No packages were installed, examples executed, or benchmarks measured. Calcite and SQLGlot do not establish native understanding of PowerCenter XML or expressions. The approved small explicit emitter remains the starting point unless a demonstrated need justifies a change.

## 1. Separate parsing, meaning and output

**Finding:** Calcite's `Planner` exposes separate parsing, validation, conversion to relational expressions and transformation stages. Its type interfaces support validation with type information. These boundaries distinguish readable syntax from resolved meaning and a useful query representation.

**Source/scope:** [Official Planner API](https://calcite.apache.org/javadocAggregate/org/apache/calcite/tools/Planner.html); interface overview and parse/validate/rel/type method descriptions inspected, not its implementation or all linked APIs.

**Applicability:** A small converter can mirror the separation without adopting Calcite: parse XML; resolve definitions, instances and ports into a typed intermediate representation (IR); validate supported semantics; emit dbt SQL. Preserve original XML identity in each node for diagnostics. A dataclass graph is sufficient to start; a full optimizer is unnecessary. Each boundary gives tests a specific question: Was the attribute read, was its reference resolved, and was the intended operation emitted?

## 2. Use explicit relational operations and field identity

**Finding:** Calcite represents queries with relational operators such as scans, projections, filters, joins and aggregates. Its algebra guide explains that joined fields can have colliding names and that references identify both the input and its field. It illustrates field ordinals and stable expression identity rather than assuming a display name uniquely identifies a value.

**Source/scope:** [Official algebra guide](https://calcite.apache.org/docs/algebra.html); overview, builder examples, field names/ordinals and multi-input references inspected. Recursive-query and full API behaviour were not investigated.

**Applicability:** Keep `(mapping, instance, port)` identity separate from a source definition and generated SQL alias. Resolve connectors before generating aliases. In joins, identical `CUSTOMER_ID` names must not collapse into one field. Keep master/detail roles explicit. Carry source type, precision and nullability metadata where known; missing meaning remains a boundary, not a guessed type. A fixture selecting a real target tests the graph, not a target-name-specific query template.

## 3. Order dependencies, not XML elements

**Finding:** Python's `TopologicalSorter` accepts nodes and predecessors; a complete topological ordering requires an acyclic graph. `CycleError` reports a cycle. Valid ordering among independent nodes can depend on insertion order.

**Source/scope:** [Python3.13 graphlib documentation](https://docs.python.org/3.13/library/graphlib.html); the full short module page inspected, including predecessor orientation, ordering and cycle limits.

**Applicability:** Starting from selected targets, collect every incoming dependency and validate references before sorting. Missing references require a separate check: a sorter can accept a predecessor as a node without proving its definition exists. Sort independent ready nodes by stable identity when reproducible SQL is required. Detect cycles in the selected graph; do not claim that one reported cycle lists every defect. Independent targets can have independent outcomes, but partial success must remain explicit.

## 4. Parse expressions structurally

**Finding:** SQLGlot's AST primer represents SQL as typed nodes with child expressions. Its traversal examples distinguish columns, identifiers, literals and nested query scopes; transformation acts on structure rather than arbitrary substrings.

**Source/scope:** [Maintainer AST primer](https://github.com/tobymao/sqlglot/blob/main/posts/ast_primer.md); tree representation, traversal and mutation sections inspected. No SQLGlot execution or PowerCenter grammar evaluation occurred.

**Applicability:** For the bounded Informatica subset, tokenize literals, identifiers, operators, commas and parentheses, then parse supported expression forms. This preserves nesting and precedence. Replacing `IIF` or port names with unrestricted string substitutions can corrupt quoted text, nested calls or longer identifiers. A small source-expression AST can feed the existing explicit emitter. SQLGlot becomes useful only if its accepted grammar and needed extensions are established; accepting Oracle SQL does not establish Informatica expression compatibility.

## 5. Reject unsupported meaning deliberately

**Finding:** SQLGlot documents explicit source/target dialects, configurable unsupported errors and type-sensitive conversions requiring schema information. Some unsupported conversions otherwise warn and continue. Its FAQ warns that successful parsing does not ensure a query will execute.

**Source/scope:** [Official SQLGlot documentation](https://sqlglot.com/sqlglot.html); FAQ, parser/unsupported errors and build/modify sections inspected. No exhaustive dialect audit or performance claims adopted.

**Applicability:** Maintain a small support matrix by operation and relevant settings. Unknown functions, stateful variables, SQL overrides or unresolved input roles should identify the affected target and source node. If a library is later used, configure strict failure where applicable and retain independent result tests. SQL emission, SQL parsing, dbt execution and result equivalence remain distinct evidence. A successful rejection test demonstrates a working boundary, not supported conversion coverage.

## 6. Extend through evidence, with small changes

**Finding:** Calcite documents source adapters separately from other language interfaces. Its schema adapters present data as tables; that is not an ETL-program translator. SQLGlot's contribution guide requests small changes and bug reports with reproduction, expected behaviour, actual behaviour and references.

**Source/scope:** [Calcite adapters](https://calcite.apache.org/docs/adapter.html), adapter/language-interface sections; [SQLGlot contribution guide](https://github.com/tobymao/sqlglot/blob/main/CONTRIBUTING.md), submission and bug-report sections inspected. No maintainer ranking or comparative benchmark was attempted.

**Applicability:** A future product reader can translate its verified source semantics into the shared IR, then reuse validated operations and SQL emission. Configuration can provide names and declared options; different semantics require rules. Add each product/version with representative exports, a concrete translation and expected-result cases. Record unverified versions explicitly. For this exercise, use these projects as design references and adopt small, reproducible fixes; do not build a speculative multi-vendor framework before the agreed core works.

## 7. Keep XML reading a narrow responsibility

**Finding:** ElementTree exposes tags, attributes and children; namespace prefixes expand into qualified names. It provides limited XPath support and directs untrusted-input users to XML security documentation.

**Source/scope:** [Python3.13 ElementTree](https://docs.python.org/3.13/library/xml.etree.elementtree.html); parsing, namespaces, XPath and security notice inspected, not the entire module implementation.

**Applicability:** Use the approved reader to extract structure, then validate required PowerCenter objects separately. Successful XML parsing establishes neither a recognized export format nor correct transformation meaning. Preserve namespace/version boundaries instead of stripping all prefixes and assuming equivalent tags.
