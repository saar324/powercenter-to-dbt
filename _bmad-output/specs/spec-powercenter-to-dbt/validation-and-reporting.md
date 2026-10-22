# Validation and reporting

## Requested artifacts

Produce `reports/test-runs.csv` from actual test executions and `reports/validation.md` as a concise human summary. These are planned deliverables, not existing run evidence. Do not populate sample passing rows or accuracy percentages before execution.

The CSV is the authoritative machine-readable run history. Native BMAD verification records retain actual commands, interpretation, review findings and links to evidence; they do not repeat the rows. The human report summarizes measured outcomes and links those records. The short README links the report and supplies the assignment's required handoff information.

## Minimal run record

One row per actual test execution, including reruns. Keep earlier failures as history; assess final behavior using the explicitly identified final tested revision, not a mix of old and new runs.

```csv
run_id,utc,revision,stage,environment,case_id,test_type,input_id,target,status,detail,evidence
```

- `run_id` groups an invocation; `utc` is the actual execution timestamp.
- `revision` identifies tested code, including a diff fingerprint for uncommitted changes.
- `stage` identifies the real development milestone; `environment` records relevant converter/dbt/database versions and conditions. Do not invent multiple environments or model settings.
- `case_id` and `test_type` identify the check and category; `input_id` identifies the fixture and hash; `target` identifies the complete output path, where relevant.
- `status` is `passed`, `failed`, `error` or `skipped`. `detail` gives a short reason; `evidence` points to the reproducible command/output or native verification record.

Keep conditions visible in case identifiers or short detail fields rather than add a second spreadsheet. No styling or dashboard is required.

## Measures and limits

| Measure | Meaning and reporting rule |
|---|---|
| Test outcomes | Show passed, failed, error and skipped counts. If showing pass rate, use passed / (passed + failed + error); show the denominator and skips separately. |
| Result checks | Show matching complete-result cases / executed result cases, grouped by actual input, operation/condition and environment. Execution errors do not count as matches. |
| Fixture coverage | Show supported complete target paths / all target paths in the supplied fixture; distinguish emitted, executable and independently result-checked paths. |
| Unsupported input | Name rejected formats, versions, operations or paths and reasons. Correct rejection can pass a negative test without increasing conversion support. |
| Unverified behavior | Mark conditions and versions without evidence as untested; never infer general correctness from compilation or a small sample. |

Preserve target column order and compare all result values and duplicate counts; account for nulls and relevant numeric/date semantics. Incidental row display order is not part of equality, but mapping-required sorting and order-dependent calculations need separate verification.

Report only observed conditions. Use counts before percentages for small samples. No aggregate score represents universal converter accuracy, and independent expected cases do not prove agreement with all PowerCenter runtime behavior.

## Verification priorities for the agreed core

These categories guide the later native implementation plan; they do not select which operators are supported.

- Run a generated model through actual dbt against a controlled local dataset and compare its complete result with independently specified expected rows.
- Change supported expressions and rename source/output fields in XML fixtures; check that generated behavior changes correctly instead of reproducing fixed SQL.
- Cover relevant null, duplicate, unmatched-join, grouping and numeric cases for the operations selected for the core.
- Check explicit diagnostics for malformed/unsupported inputs; do not count omitted logic as successful conversion.
- Check that identical input and configuration yield identical generated artifacts.
- Execute supported generated preparation steps locally, testing first-run table existence/lifecycle, command order and stale-row removal on a repeated dbt run. Conversion must not execute imported commands; unconverted setup commands remain explicitly reported.
- Execute pinned Jaffle Shop references as a mandatory minimum gate (U89–U90), preserving model SQL and recording source-data/harness adaptations. Score converter correctness only where rules and inputs match; report literal reference disagreement, partial projections, unsupported and non-comparable conditions separately.

## Reference comparison aggregation

`reports/test-runs.csv` remains the only actual execution history. The requested `reports/accuracy-by-aspect.csv` is a derived summary, not a second manually maintained run log. Group by actual run, pinned reference, comparison scope and converter aspect (for example field mapping, arithmetic, text conditions, dates, joins and aggregation). Include matched, different, error and non-comparable counts with explicit compared denominator and a numeric match-rate percentage only when the denominator is nonzero. Keep expected source-rule differences visible; a successful test that detects a difference is not a matching result. Reference/project execution checks are not data-equivalence checks.

Trace each summary group to recorded comparison details/evidence, input identity, tested revision and environment. Distinguish complete-target schema/type/value/duplicate equality from selected-column or normalized-representation comparisons. Identify every alignment and normalization; never swap output price columns, reverse join sides, change reference formulas or drop mismatch rows to manufacture agreement. No single percentage represents universal accuracy. A missing reference/model/required runtime must produce an explicit execution error or non-comparable outcome, never an empty successful report.

Case agreement is matched / (matched + different + execution errors); unsupported/non-comparable counts remain visible outside this denominator. Row agreement is duplicate-aware row overlap / max(reference rows, generated rows) per successful case. Both empty is 100% only after execution/schema checks; failed execution has blank row agreement. Aggregate row agreement sums overlap and per-case maximum counts within a declared dataset/aspect/scope. Do not merge overlapping aspects or complete/projected comparisons into one overall accuracy score. Require an original classic-project seed baseline and label any bounded modern model harness separately from full upstream-project execution.

## Human report

Keep one short final summary of the tested revision, actual environment, measures above, verified strengths and known limits. Link detailed run evidence. Separate observed failures, deliberate unsupported cases and untested risks.

For each material weakness or unresolved issue use: **evidence → concrete next change → acceptance test**. Include practical compatibility extensions where relevant. Do not present proposed fixes as completed work or produce a generic feature wishlist.
