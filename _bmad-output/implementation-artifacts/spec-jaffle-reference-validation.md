---
title: Pinned Jaffle Shop reference validation
type: chore
created: 2026-10-22
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 4a1ad5471af382efdfc929bf356ede4713cdb25c
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/_bmad-output/specs/spec-powercenter-to-dbt/SPEC.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Existing tests do not execute Jaffle Shop reference SQL. U89–U90 require this minimum-stage evidence, historical version correlation and an accuracy CSV grouped by converter aspect.

**Approach:** Execute pinned classic and historical modern references and generated models on aligned inputs. Report measured agreement, source-rule differences, provenance and practical recommendations.

## Boundaries & Constraints

**Always:** Preserve XML and upstream model SQL; record SHAs, file hashes, licenses, environment and input/configuration adaptations. Run the original assignment-linked classic project on original seeds. Execute modern reference SQL; label bounded model harnesses separately from full upstream-project runs. Cover all five core paths, with ordinary, empty, null/duplicate/unmatched and numeric/text/date discrepancy inputs. Compare complete outputs and clearly labelled projections separately; preserve duplicate counts and physical type differences. Classify differences using XML/reference evidence.

**Never:** Change converter rules, swap output price columns, reverse joins or remove mismatch rows to force agreement. Treat dates as evidence of exact ancestry, call a detected mismatch an agreement, or claim universal accuracy. Unsupported/non-comparable conditions remain visible. No publication or feature-support expansion.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
| --- | --- | --- | --- |
| Historical correlation | Publication and XML dates differ | Pinned candidates and bounded exact-match conclusion | Unknown ancestry stays unproven |
| Shared rules | Aligned inputs | Exact complete/scoped comparison of values and duplicates | Record execution/schema errors |
| Different rules | Prices, dates, flags, joins or counts differ | Actual discrepancy and cause | Preserve both rule sets |
| Empty/edge data | No rows, nulls, duplicate/unmatched keys | Recorded agreement or difference | Missing execution is not an empty match |
| Aggregate | Mixed comparison outcomes | Traceable per-aspect rates and counts | Zero denominator has no rate |

</frozen-after-approval>

## Code Map

- `tests/helpers.py` — reuse conversion and actual dbt execution.
- `tests/test_dbt_results.py`, `examples/load_demo.py` — existing independent expectations and synthetic edge inputs; not external-reference evidence.
- `tests/conftest.py` — append-only measured history and snapshot identity.
- `research/07-reference-version-correlation.md` — historical candidates, limitations and difference inventory; ignored clones are available locally.
- `reports/validation.md`, `reports/test-runs.csv` — authoritative measured summary/history. Original `fixtures/powercenter/` remains unchanged.

## Tasks & Acceptance

**Execution:**
- [x] `fixtures/references/` — retain bounded upstream SQL/macros/data with pinned provenance, licenses and declared harness configuration for reproducibility.
- [x] `tests/reference_support.py`, `tests/test_reference_results.py` — run both references and generated models; measure complete and scoped comparisons across the five paths, including mismatch probes.
- [x] `tests/conftest.py`, `scripts/summarize_accuracy.py` — record actual reference runs and derive `reports/accuracy-by-aspect.csv` from evidence, not manual scores.
- [x] `tests/test_reference_reporting.py` — independently verify denominators, zero/error handling, duplicate sensitivity and exclusion visibility.
- [x] `README.md`, `reports/validation.md`, research/native/prompt records — document commands, measured results, adaptations, differences and next actions.

**Acceptance Criteria:**
- Given pinned source files, when documented commands run, then the original classic seed baseline and the disclosed modern scope execute with retained dbt evidence.
- Given equivalent or differing rules, when comparisons run, then every core target has a disposition, at least one complete equivalent target is checked, and partial projections never claim whole-target parity.
- Given measured cases, when aggregation runs, then groups identify run/reference/revision/dataset/aspect/scope. Case agreement is `matched/(matched+different+errors)`; unsupported/non-comparable counts stay visible outside that denominator. Row agreement is duplicate-aware overlap divided by maximum row count per case; both-empty is100% only after successful execution/schema checks. Execution errors have blank row agreement. Aggregate row rates sum overlap and per-case maximum counts; no rate combines overlapping aspects into one overall score.
- Given the existing converter, when full verification runs, then prior behavior remains verified; a test that correctly observes a reference difference is reported separately from actual data agreement.

## Implementation Notes

- D59 loaded both frontmatter context files before implementation. Retained pinned upstream bytes, original classic seeds and provenance/individual SHA-256; classic/dbt_utils Apache-2.0 licenses are retained. Modern December pin has no LICENSE file; no license grant or publication is asserted.
- Added actual dbt execution of the full classic SQL project with original seeds and three controlled aligned datasets; modern execution uses a disclosed eight-model dependency closure, original orders/order_items SQL, original macros and a bounded local dbt_utils 1.1.1 package at commit74a661ca00452da7d2b2811ff1e5a37f152c3ee2. Runtime is the repository lock, not the classic old requirements lock. Configuration, synthetic classic seed/field bridges, supplemental item data and comparison normalization are declared in [reference README](../../fixtures/references/README.md).
- No converter source, supplied XML, original reference model SQL/macros/seeds or output connector wiring changed. Complete checks and projected normalized-value checks have separate scope. All output rows, duplicate multiplicities, physical schemas/types, queries, input identities and dbt manifests/run_results are retained as evidence linked from the existing history.
- Reporter records actual reference dispositions independently of pytest pass/fail and captures setup/execution/schema errors. Snapshot identity now includes scripts and retained reference files. The standard-library aggregator derives 41 groups by run/reference/pin/revision/dataset/aspect/scope/environment. Error-inclusive case denominators, exclusion visibility, duplicate overlap, blank zero/error row rates, both-empty schema checks and overlapping scope separation have independent tests.
- D59 focused invocation20261022T182314-b4cde4:96passed. Two additional missing-runtime/relation reporting checks were then added; full invocation20261022T182459-a40e5d:247passed,0failed/errors/skipped. It includes88measured reference cases:35matched,45different,8non-comparable,0execution errors; no combined accuracy rate is inferred. Original classic seeds execute100customers/99orders/113payments. Modern complete customer staging matches ordinary/empty and differs on Oracle empty-string edges. All five target paths have dispositions. [Measured report](../../reports/validation.md), [CSV](../../reports/test-runs.csv), [derived groups](../../reports/accuracy-by-aspect.csv).
- Schema/rule differences are classified with XML/reference evidence: crossed price wiring, current-century YY dates, flag representation/conditions, supply inner-join duplication/drop behavior, customer outer-join direction, null metrics and distinct/non-distinct counts. Exact modern ancestry, full modern upstream-project/seed execution and a PowerCenter runtime oracle remain unproven/unexecuted; concrete follow-ups are in the report. Documentation added during the full invocation changes the broad reference-fixture fingerprint; coordinator final verification after review will pin the final stable snapshot.
- Coordinator Step3 audit: staged all changes since full baseline into `/var/folders/k0/crmvwhg95zdfk_911sf9fgd40000gn/T/pwc-reference-review-20261022.diff` (27,106,844 bytes, dominated by retained machine-generated dbt manifests). Read all new/changed Python source and contract/report changes; inspected high-volume evidence structurally against every final comparison/history row and all retained run_results. All88 detail files reconcile with recorded row counts/dispositions; all actual dbt results succeed. Original converter-source diff is empty. Matrix maps to pinned-byte checks and historical inspection, original classic baseline, actual complete/projected cases, edge/empty cases and independent aggregation/error tests; all covering test cases passed in the247-case invocation. Tasks/acceptance are implemented; native review follows before final stable-snapshot verification.

- Review correction B1/E1/E2: exact Decimal keys replace context-sensitive normalize(); 29/38-digit distinctions and signed-zero equality have passing regressions. B2 restores typed classic RAW customer/order inputs after seed table creation, preserving NULL/empty before unchanged SQL; the original seed baseline is untouched. B3 now asserts all88 independently specified dispositions; exactly one former false match changes (classic edge customer field mapping), yielding34matched/46different/8non-comparable. Classic edge order ID/customer fields still match, as their raw rows have no empty values; the actual source rows and source-storage rule justify that expectation.
- Review correction B4/B10: unequal outputs use observed_unresolved_reference_difference with candidate rule evidence; no blanket causal certification. Every measurement/CSV group explicitly labels end-to-end combined effects and explains upstream influences on customer spend/counts and join projections. B9 retains canonical duplicate-preserving consumed-input rows and physical column/type schemas for both sides, including classic payments, plus hashed manifest evidence and declared adaptations.
- Review correction B5/B6/V2: exporter verifies selected measurement/baseline/lifecycle JSON against history metadata, output counts/rates and successful input manifests before atomic replacement. Default selects the latest passed complete88-case matrix with successful original baseline/invocation; explicit run selection discloses partial/failed status and expected/actual/missing counts. Real CLI regressions cover two complete runs, later unrelated/partial/error runs, explicit selection, missing/contradictory case or baseline evidence and preserving an existing CSV on rejection. Pre-patch JSON has no history-binding metadata and is historical; no compatibility bypass was added.
- Review correction B7/B8/E3/V1: one setup/call measurement per case; failed teardown is a separate lifecycle-error identity/evidence file. Baseline setup failure retains reference/pin/dataset metadata. An isolated real pytest session verifies success, setup and teardown rows/JSON, including that a matched call survives its teardown failure without duplicate counting or overwritten evidence. Deliberately failed probe invocations remain separate historical rows.
- Correction verification: `uv run pytest -q tests/test_reference_results.py tests/test_reference_reporting.py tests/test_reporting.py` →106passed, [run20261022T183812-828fdd](../../reports/evidence/20261022T183812-828fdd.txt); later `uv run pytest -q tests/test_reference_reporting.py tests/test_reporting.py` →17passed, [run20261022T183947-12522e](../../reports/evidence/20261022T183947-12522e.txt). `uv run python scripts/summarize_accuracy.py` accepts the complete corrected run and writes41end-to-end groups with88/88visible counts. No full suite or converter edit was made during these corrections. Frozen intent and coordinator triage remain unchanged; final full verification stays with the coordinator.

- Final narrow formatting check: derived CSV uses LF line endings; `uv run pytest -q tests/test_reference_reporting.py` →16passed, [run20261022T184105-84b1e5](../../reports/evidence/20261022T184105-84b1e5.txt). Strict re-export of run20261022T183812-828fdd succeeds with88/88cases and41groups; `git diff --check` passes. Converter-source diff remains empty.

## Spec Change Log

## Review Triage Log

All three native review layers returned before classification. Findings concern comparison/reporting correctness within the approved intent; converter source remains unchanged. Each finding is judged separately below before shared corrections.

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Blind B1: Decimal normalization rounds | medium | Root reproduced distinct29-digit decimals receiving100% agreement because normalize() uses context precision; exact Decimal comparison plus regression, patch. |
| Blind B2: classic seed bridge collapses NULL/empty | medium | csv.writer serializes both as empty fields; typed source-only restoration can preserve them before unchanged reference SQL runs. Current classic edge match can conceal that distinction; patch bridge and disclose. |
| Blind B3: ordinary shared-scope regressions can pass | medium | Most reference assertions accept any non-error disposition. Add expected dispositions for known cases, retaining measured differences as differences; patch. |
| Blind B4: differences automatically attributed | medium | measure() labels every unequal output source_rule_or_schema_difference without checking cause. Use unresolved observation plus candidate rule basis, avoid declaring cause proven; patch. |
| Blind B5: missing/contradictory evidence accepted | medium | CLI reads only CSV detail; it does not open referenced evidence, so deleted/mismatched JSON can yield a published rate. Verify selected evidence before export; patch. |
| Blind B6: partial latest invocation replaces full report | medium | latest reference_rows[-1] has no completeness/exit check. Require successful full matrix by default; existing explicit run selection may expose partial status with counts; patch. |
| Blind B7: baseline setup failure lacks identity | medium | Only reference marker has fallback; reference_execution metadata is assigned after preparation. Initialize/fallback execution identity and test persisted setup failure; patch. |
| Blind B8: teardown doubles comparison | medium | reporting hook reuses reference_comparison at failed teardown and overwrites same JSON path. Separate lifecycle-error event from unique measurement, regress actual reporting boundary; patch. |
| Blind B9: input identity omits classic inputs/schema | medium | Hash includes only unsorted RAW rows, no schemas or classic seed/payment tables actually consumed. Record canonical duplicate-preserving schemas/rows for both sides and evidence; patch. |
| Blind B10: aspect scores include upstream effects | medium | Customer aggregation includes spend from crossed upstream money; joins projections include values. Label end-to-end combined effects explicitly in evidence/CSV/docs, avoid isolated-operator claim; direct metadata correction, patch. |
| Edge E1: high-precision false match | medium | Same reproduced state as B1; grouped canonical numeric correction after separate verdict. |
| Edge E2: signed-zero false difference | medium | Root reproduced Decimal0 versus Decimal-0 as0% agreement despite numeric equality; exact Decimal keys and signed-zero regression, patch with B1. |
| Edge E3: teardown duplication | medium | Same concrete hook state as B8, grouped reporter correction after separate verdict. |
| Verification V1: persisted hook untested | medium | Pre-verified regression gap: in-memory comparisons/manual aggregate rows bypass reporter; existing isolated test covers collection failure only. Add isolated real reference reporting/setup/teardown assertions; patch. |
| Verification V2: summarizer CLI untested | medium | Pre-verified regression gap: aggregate() tests cannot catch oldest/default selection or export/overwrite failures. Add subprocess CLI checks for full/partial/latest/explicit/error evidence and preserved destination; patch. |

Disposition: local exact-value/source-bridge/reporting guards and regression checks; no intent gap, public converter change or frozen-block amendment. Re-engage same implementer once with all grouped corrections, then coordinator full verification.

Final patch disposition: all B1–B10, E1–E3 and V1–V2 are corrected, with shared root causes fixed once and every bad outcome regression-covered. Root read the actual patch, verified the frozen block unchanged and converter-source diff empty, then ran the full final suite:256passed in68.41seconds, run `20261022T184153-42a500`, snapshot `4a1ad5471af382efdfc929bf356ede4713cdb25c+code-sha256:263425202e99f38b6e922ed8eb5b14a2b1d53686c09d6ced9e6fcd56cbf85851`. All88 expected matrix dispositions pass:34matched,46different,8non-comparable,0execution errors. Both scalar review probes pass after correction. Independent reconciliation verifies every41aggregate groups,88detail counts, actual dbt statuses and append-only history. Default and explicit final-run exports validate bound evidence and produce the same report. No confirmed issue is deferred; exact reference ancestry/source-runtime equivalence and documented unexecuted scope remain evidence limits.

## Verification

**Commands:**
- `uv run pytest -q tests/test_reference_results.py tests/test_reference_reporting.py` — executed reference comparisons and aggregation checks.
- `uv run python scripts/summarize_accuracy.py` — reproducible aggregate for an identified run.
- `uv run pytest -q` — full suite; preserve real failures and report mismatch observations separately.
- Inspect pins, original hashes, denominators and final diff; exclude clones and dependency caches.

**Actual implementation verification:**
- `uv run pytest -q tests/test_reference_results.py tests/test_reference_reporting.py` →96passed; [transcript](../../reports/evidence/20261022T182314-b4cde4.txt).
- `uv run pytest -q` →247passed; [transcript](../../reports/evidence/20261022T182459-a40e5d.txt). All I/O-matrix conditions execute; no skipped reference cases.
- `uv run python scripts/summarize_accuracy.py` →selected run20261022T182459-a40e5d,41groups; [derived CSV](../../reports/accuracy-by-aspect.csv). Historical runs remain append-only. Final native review/coordinator gate is pending.
- Independent byte check: all34retained upstream files equal their exact pinned Git objects and recorded SHA-256. `git diff --check` passes. Explicit `--run-id 20261022T182459-a40e5d` aggregation reproduces41groups, all with actual evidence paths. Ignored upstream clones/dependency caches remain excluded.
