---
title: 'Convert and verify PowerCenter mappings for reviewer use'
type: 'feature'
created: '2026-10-22'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '9369d443d9d6bdef7a5a552d4747950e045d21c9'
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/research/06-core-semantics-check.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The supplied PowerCenter export cannot run as dbt models. Reviewers need a converter whose rules, results and limitations they can inspect and reproduce.

**Approach:** Build a deterministic Python CLI that reads XML, checks dependencies and generates runnable DuckDB dbt models. Deliver one cohesive basic outcome through Epic 1's three incremental stories, including tests and the required submission evidence.

## Boundaries & Constraints

**Always:** Follow the approved PRD and architecture AD-1–AD-8. Verify STG_CUSTOMERS, STG_ORDERS, STG_PRODUCTS, STG_SUPPLIES and core CUSTOMERS; five is a verification floor, not an output limit. Derive operations, wiring and column order from XML. Generate supported preparation steps. Preserve complete independent outputs and report failures. Keep separation of concerns and explicit cross-mapping bindings. Capture prompts, decisions, real errors and measured tests during work. Aim near four hours from 16:34 Sofia; finish necessary work without a hard 20:30 cutoff.

**Never:** Hard-code Jaffle Shop SQL, infer missing relations from similar names, run imported SQL during conversion, silently replace unsupported rules, claim unmeasured equivalence, expose confidential material, alter supplied fixtures or vendor BMAD, or submit/message the employer. No universal XML/vendor coverage, UI or arbitrary workflow execution.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Basic conversion | Supplied XML, explicit bindings, fresh destination | One SQL model per target; named CTEs, project/configuration, sources and inventory | Contextual diagnostics |
| Data boundaries | Null/empty strings, duplicate/unmatched keys, numeric limits, two-digit dates | Researched bounded rules; preserve crossed price wiring and master-outer detail side | Unsupported/error behavior explicit |
| Invalid dependency | Missing port, loop, incompatible binding or failed producer | Retain independent outputs; block affected consumers | Nonzero exit; target identity and cause |
| Unknown operation | Unsupported expression, transformation or required preparation | No successful model for affected target | Report unsupported; block dependents |
| Cleanup and repeat | Customer preparation, absent/existing local table, stale rows | Generated target-bound cleanup runs safely through dbt | Never execute raw XML commands |
| Unsafe destination/XML | Nonempty directory or external entity expansion | Refuse overwrite; no external DTD fetch/entity expansion | Clear failure; preserve existing files |

</frozen-after-approval>

## Code Map

- `fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml`: unchanged source; three mappings, sixteen targets, exact instance/port identities; customer target pre-SQL.
- `docs/assignment.md`: original obligations; `docs/agent-prompts.md`: authoritative available prompt history.
- `_bmad-output/implementation-artifacts/epic-1-context.md`: adopted requirements, constraints and all architecture decisions; native planning remains authoritative.
- `research/06-core-semantics-check.md`: source/intermediate/target types, defaults, joins, strings, precision and date evidence; no executed PowerCenter oracle.
- Product source, Python manifest and tests do not yet exist. Reuse installed uv; preserve existing BMAD/npm setup and supplied hashes.
- Baseline: `9369d443d9d6bdef7a5a552d4747950e045d21c9`, branch `codex/converter`; clean at entry. Local artifact writes only; no irreversible action. No remaining owner intent gaps.

## Tasks & Acceptance

**Execution:**
- [x] `pyproject.toml`, `uv.lock` — resolve Python 3.13, pytest, DuckDB and dbt-duckdb; smoke-check compatibility.
- [x] `src/pwc_to_dbt/mapping.py` — centrally define typed identities, ports, types, diagnostics, canonical ModelPlan and preparation intents before delegation; one authoritative contract.
- [x] `src/pwc_to_dbt/xml_reader.py`, `dependencies.py` — read metadata, inventory targets, validate graphs/bindings and include producer closure; reject missing links, cycles and collisions.
- [x] `src/pwc_to_dbt/expressions.py`, `sql.py` — structurally translate supported expressions and qualifier/expression/join/aggregate/sort steps; apply separate boundary conversions and researched date/default rules.
- [x] `src/pwc_to_dbt/project.py`, `cli.py`, `examples/sample-bindings.json` — consume canonical plans; write deterministic runnable project and outcome manifest atomically to a fresh directory. Writer owns materialization and guarded target-bound cleanup; CLI owns selection and exits.
- [x] `tests/` — independent controlled data and expected results; actual dbt execution for five paths, preparation lifecycle, mutations, negative cases, types, duplicates, dates, sort semantics and deterministic files.
- [x] `reports/test-runs.csv`, `reports/validation.md`, `README.md`, `docs/agent-prompts.md`, `.github/workflows/tests.yml`, `.gitignore` — record actual evidence continuously; provide reproducible commands, all six README obligations and practical next work; exclude installed dependencies/caches.

**Acceptance Criteria:**
- Given the sample and declared inputs, when conversion and dbt execution finish, then all five required outputs match independent expected columns, values and duplicate counts.
- Given changed supported XML rules or wiring, when conversion repeats, then SQL and tested results follow those changes rather than fixed sample output.
- Given supported preparation, when first and repeated local dbt runs execute, then lifecycle evidence proves correct relation/order and stale-row handling.
- Given measured runs, when the basic handoff is reviewed, then outcomes, result equivalence and support coverage remain separate, the tested revision/environment are identified, and every employer documentation requirement is present before optional breadth.

## Implementation Notes

Implementation entered through the installed native Build step 03; frontmatter context and the canonical companions were read before product edits. The central dataclasses were written before the reader/planner/emitter/writer. No vendor BMAD files, supplied fixtures or production data were changed.

Actual verification commands: `uv lock`, `uv sync --locked`, `uv run pwc-to-dbt --help`, successive measured `uv run pytest -q` invocations, a fresh-directory run of the README conversion/loader/dbt commands, and an all-target CLI attempt (expected exit 1 for retained unsupported paths). Final complete verification is run `20261022T171154-b71cfa` at snapshot `9369d443d9d6bdef7a5a552d4747950e045d21c9+code-sha256:9e1990a88646b0b25a5c3e3e20a223697ad6dbca18374f9b356a407069211389`; the [validation report](../../reports/validation.md) and [CSV](../../reports/test-runs.csv) own measured results. The final [README smoke evidence](../../reports/evidence/20261022T171154-b71cfa-readme-smoke.txt) uses a new destination `.generated/demo-final` because the earlier demo destination is intentionally preserved.

Actual mistakes, detection and corrections:

- The initial test evidence writer assumed its directory existed. Pytest setup raised FileNotFoundError; the writer now creates its parent before the first dbt transcript. The failed execution is retained in the CSV.
- The initial default wrapper placed volatile `error()` calls inside DuckDB TRY. Real dbt execution reported a binder error. Deterministic failing casts now represent bounded expression errors. An independent SQL audit then reproduced a double-default failure caused by repeated finite guards around an error-producing expression; conversion is now caught before finite/length validation. Decimal, double and bare-NUMBER regressions check legitimate NULL separately from replacement defaults; an XML mutation also executes the reached double-zero default through dbt.
- The example bindings initially omitted the exact STG_ORDERS2 instance consumed by CUSTOMERS. The dbt run exposed the missing external table; the configuration now binds the exact instance, and selection tests prove producer closure with no inferred suffix removal.
- Independently written order expectations initially assumed conventional cents/dollars names. Complete-result tests failed. Direct inspection of XML CONNECTOR records proved that all three order amounts cross at the target, as product prices also do. Expectations were corrected to those source records; the converter's XML-derived wiring was retained.
- A boundary test expected NULL for an invalid 2100 leap day without applying the output-default boundary in its test call. The test now exercises that same explicit boundary used by generated models.
- The decimal precision test showed that DuckDB directly rejects 9.9940 when cast to DECIMAL(3,2), although 9.99 is representable after scale rounding. Conversion now rounds declared decimal scale before casting; signed half values and overflow cases pass.
- An independent SQL audit added an unconnected UNUSED_COLUMN to bound source STG_CUSTOMERS. Binding validation accepted the consumed contract, while the old emitter selected all definition ports and would query a missing producer column. Source projection now uses exactly the consumed, checked fields. A mutated XML dbt regression verifies the complete customer result.
- An independent evidence audit identified missing Joiner/Aggregator mutation and empty-input checks, loose numeric type equality and inaccurate default input labels for synthetic tests. The final suite includes those operation/result/type checks and records actual mutated XML hashes or explicit scalar identities. Earlier rows are preserved with their historical label limitation stated in the report.

The implementation, tests and README are local artifacts. Native review/triage remains the coordinator's next Build step; no submission, push, employer message or remote CI result is claimed.

Coordinator verification: read the staged code/configuration changes and structured high-volume dependency/report sections from `/tmp/pwc-build-review-20261022-1714.diff` (103 changed files). Final source fingerprint and both supplied hashes match; all CSV evidence links resolve. `uv sync --locked` and installed CLI help pass. Initial coordinator metadata inspection used system Python lacking tomllib; rerunning in the documented uv environment passed. Raw captured transcripts and standard CSV CRLF remain unchanged; .gitattributes limits whitespace exclusions to those evidence files. README retains the user-reported personal Codex 20× plan.

Matrix audit: basic conversion is covered by the five complete-result/type tests; data boundaries by semantics, duplicate/unmatched/null and empty-result cases; dependency/unknown-operation cases by graph and unsupported tests; cleanup by actual first/repeat SQL-order and stale-row checks; unsafe destination/XML by preservation/entity/DTD tests. All covering tests ran and passed in final run 20261022T171154-b71cfa; no covering test is skipped. Every task is complete; native review remains pending.

Coordinator final verification after native review patches: `uv run pytest -q` passed 140 cases in 28.49 seconds, run `20261022T172637-34c669`, snapshot `9369d443d9d6bdef7a5a552d4747950e045d21c9+code-sha256:675594da1da100fb75f6ab86e38a1abc318363881414bc6b4cecf9bed4a08650`. One separate successful invocation record is not counted as a test. A fresh conversion/loader/dbt smoke and all-target expected partial exit also pass; [current validation](../../reports/validation.md) owns final links and counts. Read all patch changes and matched each confirmed review finding to passing regression coverage. Both supplied hashes remain unchanged. Targeted patch failures identified two test-harness defects (BIGINT parameter binding and collection-path resolution); corrected probes and full verification pass. No product-code changes follow this measured run.

Native Build step05 completed after all tests, matrix checks and confirmed review corrections. The epic-level implementation covers all three planned stories; sprint tracking is synchronized to review for owner walkthrough using the native status-sync rules. This does not claim three separate implementation-spec runs. Final code fingerprint and a bounded changed-file confidentiality scan passed.

Local implementation commit receipt: `137255f59bbfc9aedcd2f0bc763a5a23dfdb9950`. Post-commit code fingerprint matches the final tested snapshot. Only this verification-to-commit receipt is added afterward; no push or submission.

Final local requirements audit requested in U80: original assignment and all six README obligations rechecked, including independent read-only D53 audit. No missing local functional deliverable within the agreed basic scope was found. Current source/tests/examples/lock/CI fingerprint still matches run20261022T172637-34c669 with140 passing test cases; original hashes and README/report links pass. No tests rerun because product code is unchanged. Owner code understanding/walkthrough, publication or ZIP preparation, actual submission and recruiter notification remain separate pending handoff actions. The curated prompt log is not a full export: no conversation-export tool is currently exposed; desktop UI export capability remains unestablished. Matched Jaffle Shop comparison and remote CI are optional, not employer omissions. No additional feature work, publication or submission was performed.

Owner calculations review O1 (after the prior140-case completion gate): denominator-zero handling precedes NULL propagation in expressions.py:133. D54 reported it; coordinator independently reproduced15 focused cases across decimal/double/bare-NUMBER defaults, with9passing and6failing at unchanged product fingerprint. Evidence: [focused probes](../../reports/evidence/20261022T175334-owner-calculations-44bf61.json). For NULL/0, defaults0 andERROR produce the wrong behavior; documented source arithmetic returnsNULL. Supplied mandatory paths use divisor100, so existing complete-result evidence remains valid but calculation review is reopened. Smallest correction is a NULL guard before the zero guard; no new intent/public surface. Re-engage the same implementer through native patch handling, add regressions, then full verification before closure.

Owner calculations O1 closure: same implementation agent changed one division guard to propagate NULL operands before zero handling. D55 targeted17 tests passed. Coordinator re-ran the same15 manual probes:15passed; the initial6failures remain in history. Full coordinator verification run `20261022T175519-80ee06` passed149cases in29.18s at `6e4694bfc67487ce400a24f710b476db4d71bfe7+code-sha256:8d4c1ea03b8f4969ce51666ec72c577e7fe9a72b2a05bcba57f625c453b0c91c`, with actual five-path dbt/type/result checks and the strengthened COST/0 null-row mutation. Locked sync, installed CLI help, fresh README conversion/loader/dbt and all-target expected partial exit pass. Product source was read after the patch; no new intent or public interface. O1 is closed and native Build returns done; owner discussion of calculations is ongoing and the other review areas remain pending.

Comprehensive area1 discussion covers Python generating SQL rather than evaluating customer data; parser tokens/AST/precedence; checked function arities and names; separate source/intermediate/target conversions; decimal rounding and integer width; legitimate NULL versus output error defaults with boxed TRY results; runtime-century dates; Oracle storage empty strings versus intermediates; aggregate restrictions; deterministic output, contextual rejection and known source-runtime/ASCII/row-recovery limits. These are explanations of current code and bounded measured policy, not full PowerCenter-equivalence proof or human signoff.

## Spec Change Log

## Review Triage Log

All three native layers returned before classification. Each finding was checked separately; no intent gap or re-derivation is needed. The surviving corrections are local validations/casts/report hooks/tests on demonstrated existing states, with no new user option or conversion feature.

| Finding | Verdict | Verified evidence and route |
| --- | --- | --- |
| Blind B1: writer Insert disabled | high | XML mutation Insert=NO still emits unchanged customer SELECT. Existing supported-writer profile must reject it; patch. |
| Blind B2: source row mode | high | Treat source rows as=Delete still emits replacement models; no delete semantics exist. Reject incompatible mode; patch. |
| Blind B3: incremental aggregation | high | Enabling the core session setting leaves a stateless aggregate emitted. Stateful execution is unsupported; reject it; patch. |
| Blind B4: integer widths | medium | DuckDB execution accepts 2147483648 through integer and 32768 through small integer because both use BIGINT. Official Informatica datatype tables distinguish ranges. Correct cast mapping and boundary/default tests; patch. |
| Blind B5: unrelated malformed precision | medium | Bad precision on unselected STG_ORDERS raises global ValueError while selecting STG_CUSTOMERS. Store contextual node metadata failure; patch. |
| Blind B6: output-only qualifier port | medium | Added unconnected EXTRA output reaches inputs[port.name] and raises uncaught KeyError. Diagnose unsupported passthrough shape and retain independent outputs; patch. |
| Blind B7: falsy wrong config type | medium | [], false, 0 and empty string all reach default planning instead of type error. Default only None; patch with E3 below. |
| Blind B8: ambiguous field ordinals | medium | Duplicate customer FIELDNUMBER still emits. Validate present, positive, unique source/target ordinals contextually; patch. |
| Blind B9: manifest omits binding config | false | XML hash is not claimed to identify the whole run. Measured fingerprint includes the supplied configuration; generated source declarations, source-instance CTEs/ref calls and model/dependency inventory retain effective relations. No demonstrated incorrect conversion or untraceable submitted run; standalone manifest provenance enhancement is not a required correction. |
| Blind B10: collection failures absent from CSV | medium | Reporter has no collection hook; ROWS is filled only by individual case reports, so collection-only failure has no CSV outcome. Record collection/run failure and verify via isolated pytest invocation; patch. |
| Edge E1: nongrouped aggregate expression | medium | Changing LIFETIME_SPEND to ORDER_TOTAL emits SQL, then DuckDB EXPLAIN raises GROUP BY BinderException. Reject ungrouped/nested unsupported aggregate shape before emission; patch. |
| Edge E2: deep expression recursion | medium | 1200 parentheses raise uncaught RecursionError from translate. Convert that known unsupported-complexity exception to contextual ConversionError; patch. |
| Edge E3: falsy wrong config type | medium | Independently verified as B7; same normalization defect, grouped with B7 for one patch. |
| Verification V1: FIELDNUMBER permutation test | medium | Pre-verified regression gap: physical field order equals ordinal order in every existing target fixture. Add reversed-element XML mutation with actual dbt column/result assertion; patch. |


Patch disposition: B1–B8, B10, E1–E3 and V1 are corrected, with B7/E3 sharing one normalization fix. B9 remains rejected on the evidence above. No unresolved confirmed finding, intent gap or deferred native review item remains.

Owner targeted-review triage O1: **medium · patch**. Exact NULL/0 state is reproduced and source-documented. One local guard-order correction, no scope change; same implementer and required post-patch verification. Earlier completed-gate statements above are historical; O1 is currently open.

Owner O1 patch disposition: corrected and verified in full run `20261022T175519-80ee06`; no remaining confirmed calculations defect from D54. This supersedes the earlier O1-open state without removing its evidence.

## Design Notes

Shared interfaces are set centrally before parallel work on disjoint modules. Planner alone owns model identities/contracts; writer alone owns dbt lifecycle. Tests calculate expectations independently. Production date handling uses runtime context; controlled tests do not introduce a fixed production year. Source-runtime rounding, collation and row-error recovery limits remain explicit.

## Verification

**Commands:**
- `uv sync --locked` — restores the tested dependency environment.
- `uv run pytest -q` — meaningful unit, mutation and actual local dbt result/lifecycle checks pass; retain failed-run history.
- `uv run pwc-to-dbt --help` — documented CLI is installed and usable.
- Run the README's conversion and local dbt commands from a fresh destination — models execute and independent checks match.
- Check fixture hashes, final diff and tracked files — preserve inputs, exclude confidential material/dependencies, and tie claims to the tested revision.
