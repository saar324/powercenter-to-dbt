# Verification and reporting source reconciliation

PRD preparation input, read on 22 October 2026. This document reconciles existing requirements; it is not implementation approval, a run log or measured evidence. Sources: `docs/assignment.md`; U23 in `docs/agent-prompts.md`; native SPEC companions `validation-and-reporting.md` and `source-compatibility.md`, including the corrected Python stack approval. No converter tests were run for this reconciliation.

## Required outcome and evidence

The assignment requires tests and a clear explanation of assumptions, exclusions, likely wrong output, an actual agent mistake and detection, prompts and the process followed. Saar additionally requests a minimal measured run history and concise report of strengths, weak points and practical next work, segmented by actual test type, input, condition, environment and development stage. Keep these distinct from claims of general or universal accuracy.

The user approved Python for the converter. SQL remains the generated dbt model language. The approved verification tools are pytest, DuckDB and dbt-duckdb, with isolated locked dependencies through uv. This choice supplies a local verification environment; it does not establish broader database-dialect support or prove any test has run.

For each agreed complete source-to-target path, acceptance evidence must connect original XML logic, generated output, actual local execution and an independently specified expected result. Identify the tested code revision, input fixture/hash, relevant tool versions, condition and reproducible command/output. Preserve original supplied fixtures; use separate test fixtures for mutations.

## Verification requirements for the agreed core

1. Execute generated models through actual dbt against controlled local inputs. Compare complete result columns, values and duplicate counts with independently specified expected rows. Handle nulls and relevant numeric/date semantics explicitly. Do not require row order unless the supported contract does.
2. Change supported expressions and source/output names in XML test fixtures. Confirm the corresponding generated behavior changes as independently expected. This demonstrates derivation rather than fixed Jaffle Shop output.
3. Cover relevant nulls, duplicate rows, unmatched joins, grouping and numeric cases for the operations selected for the core. Do not imply every listed operation is already in scope.
4. Test malformed and unsupported input diagnostics. A path with omitted or untranslated logic cannot be reported as a successful equivalent conversion.
5. Check that identical input and configuration produce identical generated artifacts.
6. Compare against Jaffle Shop only when source schema, input rows and intended rules match. The supplied XML and classic DuckDB example are different related variants; mismatched references are not evidence of a converter defect. Use independent expected-result cases when a valid reference comparison is unavailable.

Compilation or SQL execution alone does not establish result correctness. Independent small-case checks establish behavior for their specific conditions, not complete PowerCenter runtime equivalence. Product/version compatibility needs representative export evidence; shared XML syntax or filename extensions do not establish support.

## Report content and denominator boundaries

Keep one authoritative CSV of actual per-test executions, including reruns, and one concise human summary. Native BMAD verification records retain commands, interpretation, review findings and evidence links without copying the CSV rows. The README links these records and covers the assignment checklist. No extra spreadsheet, dashboard or parallel work/test log is required.

| Measure | Required boundary |
|---|---|
| Test outcomes | Show passed, failed, error and skipped counts. Optional pass rate is passed / (passed + failed + error); show that denominator and skips separately. |
| Complete-result checks | Matching complete-result cases / executed result cases, with execution errors counted as nonmatches. Group only by actual tested input, operation/condition and environment. |
| Supplied-fixture coverage | Supported complete target paths / all target paths in the supplied fixture. Distinguish emitted, executable and independently result-checked paths. Record each target once per revision for coverage, regardless of rerun count. |
| Unsupported behavior | List rejected operations, formats, versions or paths and the reason. Correct rejection may pass a negative test but does not increase conversion support. |
| Untested behavior | Label conditions without evidence as untested. Do not silently classify them as supported or failed. |

Use counts before percentages for small samples. Keep earlier failures as history; assess final behavior using the explicitly identified final tested revision rather than combining old and new runs. Do not fabricate passing rows, environments, model settings, compatibility claims or accuracy percentages. The human summary must distinguish verified strengths, observed failures, deliberate exclusions and untested risks.

## Practical improvement record

For each material weakness or unresolved issue use **evidence → concrete next change → acceptance test**. Candidate future work is not an observed defect or completed work.

| Boundary | Practical next change | Acceptance evidence |
|---|---|---|
| A currently unsupported operation | Define that operation's relevant type/null/order rules; implement the supported translation or retain explicit rejection. | Focused edge cases plus a complete converted path match independent expected results; unsupported variants remain rejected. |
| An unverified PowerCenter release | Obtain a representative versioned export, inspect actual differences and add necessary compatibility rules. | The fixture yields verified equivalent results for declared supported logic, or a clear unsupported diagnostic. |
| Another source product | Obtain its official format specification and a nontrivial representative mapping; evaluate a source-specific reader. | Equivalent examples yield the same independent target result for the declared shared operations. |
| A result mismatch observed during implementation | Link the failing input/result evidence; specify a focused rule correction after finding the cause. | The original failing case and relevant adjacent cases pass in a new identified revision. |

## Material gaps and conflicts for PRD review

- Exact core paths and operations remain unresolved. The PRD must name a reviewable minimum and bonuses before implementation readiness; stack approval does not settle this scope. Operator-specific acceptance cases depend on that decision.
- DuckDB is selected for local verification; target SQL dialect claims beyond it remain unresolved. A reference/project variant mismatch must not be resolved by claiming unsupported equivalence.
- U23 asks for useful accuracy by condition. The companion correctly translates this into bounded test outcomes, result checks and path coverage, rather than one universal score. The PRD should preserve that distinction and explicitly retain unsupported/untested counts.
- The current documentation rule rejects duplicate test-results logs, while U23 explicitly requests a CSV and report. There is no need for parallel logs: make the CSV authoritative, the report a concise derived view, and native BMAD records the command/interpretation source. Keep their roles explicit in the PRD.
- Run artifacts are planned only. No measured results, dependency compatibility success, exact supported-format/version list or full PowerCenter-runtime comparison currently exists. Do not populate these gaps with assumptions.

## Implementation addendum recommendation

The companion proposes `reports/test-runs.csv` and `reports/validation.md`; these paths and the schema are agent-developed details, not verbatim user choices. Keep the PRD focused on evidence behavior and put exact schema details in the implementation addendum unless needed for review:

```csv
run_id,utc,revision,stage,environment,case_id,test_type,input_id,target,status,detail,evidence
```

One row represents one actual test execution. `revision` must identify uncommitted code via a diff fingerprint where applicable. `stage` is the real development milestone; actual operation/condition and environment remain visible. Status values are `passed`, `failed`, `error` or `skipped`; brief detail and evidence links explain exceptions. Final reporting must define whether a result case is a whole model/path or a smaller operation case so that unlike units are not combined.

## Draft reconciliation

Compared this extract with the current `prd.md` and `addendum.md` on 22 October 2026. No material verification/reporting gaps remain in the drafts.

- PRD FR-6 and the addendum require independently specified complete expected results, XML mutations, relevant edge cases, rejection tests, deterministic output and actual dbt execution. They explicitly separate unordered duplicate-preserving result checks from Sorter key/direction/settings validation; a sort mutation need not change the result multiset.
- PRD FR-7, success measures and the addendum preserve actual run identities, all four statuses, explicit denominators, separate fixture coverage and unsupported/unverified distinctions. Correct negative-test rejection does not count as conversion support. Final measurements identify the final tested revision while earlier failures remain history.
- The CSV remains the single measured-row source; native BMAD records retain commands, interpretation and evidence links. The human report is a concise derived view, not another run log. Practical future work uses evidence, a concrete change and an acceptance test and must distinguish candidate extensions from observed failures.
- Remaining choices are explicit approval matters, not missing evidence: the proposed five-target core, DuckDB output dialect and bounded semantic/checkpoint assumptions. No draft claims that results, dependency compatibility or broader product/version equivalence have been demonstrated.

During implementation, define the result-case unit and identify the selected final verification invocation(s), so the final summary cannot combine unlike cases or count historical reruns as extra coverage. This operational detail does not require a PRD scope change. No tests were run during this draft reconciliation.
