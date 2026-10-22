# Measured validation

**Open minimum-stage acceptance gap (U89):** Saar requires an executed Jaffle Shop reference comparison as part of minimum functionality. This supersedes treating that comparison as optional. Existing passing tests remain valid evidence for their stated cases, but the minimum-stage validation is incomplete until reference execution, comparable-rule result checks and explicit mismatch reporting are recorded. No reference accuracy score has yet been measured. The omission from the earlier minimum-completion assessment is a process error.

Owner calculations review follow-up: NULL/0 propagation was corrected before denominator-zero handling. The same15 focused probes now pass; the earlier9pass/6fail run remains in history. The final full-suite result below includes the new regression cases. Owner walkthrough continues one area at a time; dependency and preparation review are still pending.

Final full invocation: `uv run pytest -q`, run `20261022T175519-80ee06` on 22 October 2026. **149 passed, 0 failed, 0 error, 0 skipped** (149 test-case executions; one separate successful invocation record). Earlier runs remain historical; they are not mixed into this result.

Tested snapshot: `6e4694bfc67487ce400a24f710b476db4d71bfe7+code-sha256:8d4c1ea03b8f4969ce51666ec72c577e7fe9a72b2a05bcba57f625c453b0c91c`. The suffix hashes product source, tests, examples, Python manifest/lock and CI files; it identifies the working snapshot at test time precisely. Corresponding implementation commit: `93de53298c5157a2bfdd2e51ee82054d8a89c612`. Documentation/report writes are outside that code fingerprint; the code fingerprint identifies the exact tested product snapshot. Environment: `Python=3.13.16;platform=Darwin-arm64;pytest=9.0.2;duckdb=1.4.4;dbt-core=1.12.6;dbt-duckdb=1.10.1`. CI is configured but has not been run remotely.

Input: supplied XML SHA-256 `0c34e0ed2965e117b5de54ca2b1d1333286beb928a6bc63eaf131b04982a3522`. Both supplied-file hashes are checked. Mutations record their own XML hashes; scalar cases identify inline inputs and test-source hashes. Earlier rows initially labelled synthetic/scalar checks with the base XML hash; that reporter defect was corrected before this final run. Those earlier labels are preserved as history, not exact synthetic-input provenance.

| Measure | Actual evidence |
| --- | --- |
| Jaffle Shop reference-project comparison | Not run; accuracy against the linked reference project has not been measured. Current result checks use independently specified expectations on synthetic data, not executed Jaffle Shop output. The linked classic DuckDB project and supplied XML have schema/rule differences; see the research note and README before defining a valid comparison. |
| Required complete results | 5/5 nonempty target cases match independently specified column order, DuckDB output types, all values and duplicate counts. |
| Empty-input complete results | 5/5 required target cases match the independent empty result and output schema. |
| XML mutation checks | 10 passed, with actual dbt execution: expression/wiring, source and target renaming, a new target instance, sort options, Joiner condition, Aggregator expression, unused bound-port regression, double error-default regression and reversed physical target-field order. These remain separate from the 10 baseline/empty result cases. |
| Supplied-fixture output inventory | 9/16 targets emitted with example configuration; 7/16 explicitly unsupported. Emission is not execution evidence. |
| Executed and independently checked paths | 5/16 supplied target paths. The four other emitted paths remain unverified. |
| Preparation | Actual first and repeated dbt runs for all five outputs; absent-table guards, resolved target identity, delete-before-create SQL order and customer stale-row removal passed. |

The final [test transcript](evidence/20261022T175519-80ee06.txt), [first dbt run](evidence/20261022T175519-80ee06-dbt-first.txt), [repeat run](evidence/20261022T175519-80ee06-dbt-repeat.txt), [cleanup SQL order](evidence/20261022T175519-80ee06-cleanup-order.txt), [fresh README smoke run](evidence/20261022T175519-80ee06-readme-smoke.txt), [all-target CLI outcome](evidence/20261022T175519-80ee06-all-targets.txt) and [full inventory](evidence/final-inventory.json) support these measures. The [CSV](test-runs.csv) is the authoritative invocation history. Native commands, corrections and review status are in the [Build record](../_bmad-output/implementation-artifacts/spec-powercenter-basic-conversion.md#implementation-notes).

The required paths preserve both the product and order crossed cents/dollars wiring, master-outer detail preservation, duplicate multiplication, ordinary null-key equality and all-null aggregate handling. Boundary tests cover two-digit dates under controlled 1900/2000/2100-century contexts, invalid leap-day NULL fallback, midnight, strings at storage/intermediate boundaries, decimal rounding/overflow, finite numbers and error-default versus legitimate-null behavior. Sort direction, null placement and ASCII case sensitivity are checked separately from unordered result equality. Conversion determinism, destination preservation, dependency errors and unsupported/security rejection are also measured. Passing a rejection test does not add supported conversion coverage.

Seven paths are deliberately unsupported: core ORDERS reaches unsupported COUNT(*) syntax; staging STG_LOCATIONS reaches TRUNC; all five enriched marts reach stateful local variables. Other unsupported settings/functions/types and imported dbt templates are rejected contextually. This export's repository metadata is not a verified PowerCenter release range, and no PowerCenter service executed these test inputs. Result checks establish the declared bounded policy on controlled data, not universal source-runtime equivalence.

Practical next work:

- **Evidence:** four emitted paths lack independent result checks → add controlled fixtures and actual dbt comparisons for STG_ORDER_ITEMS plus core ORDER_ITEMS/PRODUCTS/SUPPLIES → accept only after complete columns/types/values/duplicate counts and relevant edge cases match.
- **Evidence:** seven targets stop at explicit unsupported operations → specify one operation's source type/null/state/order rules before extending the parser/emitter → require an XML mutation, boundary tests and a complete-path dbt comparison; retain rejection for unimplemented variants.
- **Evidence:** there is no executed source oracle, and only bounded ASCII/numeric/date conditions are verified → obtain matched PowerCenter input/output evidence for floating ties, code pages/collation, session settings and row-error recovery → compare complete results under recorded source and target runtime versions.
- **Evidence:** only this PowerCenter export layout is exercised → obtain representative versioned exports or one official second-product format (for example SSIS DTSX) → add a source-specific reader and equivalent complete-result fixtures, or reject that format explicitly. XML syntax alone is not compatibility.

Native review is complete. Confirmed review findings were corrected and regression-tested: incompatible writer/session modes, integer widths, malformed independent metadata, ambiguous ordinals, passthrough output shape, wrong configuration types, unsupported aggregate shapes, expression complexity and pytest collection reporting. Invocation rows use `test_type=run` and are excluded from test-case totals. Deliberately failed isolated collection probes verify the reporter; they are separate from this final full invocation. The review triage retains every finding, including one rejected provenance enhancement.

Calculation O1 evidence: [before correction](evidence/20261022T175334-owner-calculations-44bf61.json) and [same probes after correction](evidence/20261022T175544-owner-calculations-fbadf9.json). New scalar regression covers both null operands, zero/nonzero denominators and NULL/zero/ERROR defaults across decimal/double/bare-NUMBER. The generated supplies COST/0 mutation also checks a null COST row.

## How to read the test suite

Owner clarification U88 requests an explanation of the suite after asking specifically about Jaffle Shop comparison evidence. This records a request for clarification, not approval of the test strategy or a claim that a reference comparison was performed.

| Latest full-run group | Cases | What is checked |
| --- | ---: | --- |
| Complete results | 10 | Convert the supplied XML, create a temporary DuckDB database, execute actual dbt models and compare all columns in order, output types, values and duplicate counts with hand-specified expectations. Five populated cases plus five empty-input cases cover the agreed five paths. |
| XML mutations | 10 | Change a copy of the XML, regenerate and execute dbt, then check the expected changed or preserved behavior. Examples include calculations, connector wiring, renames, joins, aggregation, sorting and field ordinals. |
| Semantic boundaries | 55 | Probe conditions such as nulls, error defaults, division by zero, integer limits, decimal rounding/overflow, empty strings, dates and explicit sorting. These are focused cases, not 55 complete target-path comparisons. |
| Rejection/error handling | 63 | Check malformed, unsupported or inconsistent inputs are rejected/reported, and independent outputs survive where appropriate. A passed rejection test does not mean that input can be converted. |
| Structural/CLI/reporting checks | 10 | Check inventory, dependency selection, external inputs, deterministic files, command behavior, supplied hashes, conversion side-effect boundaries and the test reporter. |
| Preparation lifecycle | 1 | One scenario executes first and repeated dbt runs across five outputs, checks absent-table handling and cleanup order, inserts a stale customer row and verifies its removal. One case contains several assertions. |

The 149 cases include parameterized variants; they are not 149 independent datasets or target models. Ordinary complete-result comparisons ignore row order but preserve duplicate counts; column order and types must match. Sorting rules have separate checks.

Expected rows/types are written in the tests separately from the converter and are not computed by calling the converter's expression functions. They are based on our interpretation of the XML and documented bounded semantics, so an interpretation error can still affect both implementation and expectations. Neither an executed Jaffle Shop comparison nor a PowerCenter runtime oracle currently validates that interpretation. The latest suite has a 100% pass rate for its cases; this is not a general accuracy percentage. Target result-verification coverage remains 5/16, with 4 other emitted paths unverified and 7 explicitly unsupported.
