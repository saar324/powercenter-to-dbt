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
- Compare Jaffle Shop references only where inputs and rules match, as described in `source-compatibility.md`.

## Human report

Keep one short final summary of the tested revision, actual environment, measures above, verified strengths and known limits. Link detailed run evidence. Separate observed failures, deliberate unsupported cases and untested risks.

For each material weakness or unresolved issue use: **evidence → concrete next change → acceptance test**. Include practical compatibility extensions where relevant. Do not present proposed fixes as completed work or produce a generic feature wishlist.
