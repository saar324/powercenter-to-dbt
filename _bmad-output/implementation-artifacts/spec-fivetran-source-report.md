---
title: Fivetran source report for migration
type: feature
created: 2026-10-28
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 57ca4ef43a516b3b8481683c0e48e8ab5e6002ae
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/_bmad-output/specs/spec-fivetran-source-report/SPEC.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Migration planning lacks a report of the external source technologies and Fivetran connectors needed by the converted pipeline. Conversion success alone does not establish that input data can be supplied.

**Approach:** Inventory the whole export, classify exact source uses with explicit bindings, match technologies to a documented offline catalogue and expose unresolved facts. Provide report-only JSON and opt-in project output.

## Boundaries & Constraints

**Always:** Follow the canonical SPEC and its companions. Keep all definitions and uses, including unused, failed and unselected cases. Preserve source and session/workflow evidence with provenance. Binding, producer availability, connector availability and client compatibility are separate facts. Use specialist agents and core functional MVP checks; report verified behavior and limits.

**Never:** Infer servers or bindings from names, equate tables to connections, hide failed producers, guess effective runtime overrides or claim catalogue completeness. No live API, extraction, credentials, database access, imported SQL execution, publication or translation changes. Preserve supplied fixtures, XML guards and existing output protection.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
| --- | --- | --- | --- |
| Whole export | Supplied XML, partial conversion | 12 definitions and 28 uses, including failed/unselected paths | Conversion outcomes stay separate |
| Reuse | Multiple uses or identical names in different folders | One row per exact definition; all uses retained | Never merge physical endpoints |
| Binding | Bound, unbound, mixed or failed producer | Exact per-use classification and separate availability | No name inference or external fallback |
| Metadata | Unknown/missing type or conflicting evidence | Candidate match or explicit review state | No compatibility claim |
| Session context | Qualifier and workflow override references | Preserve source associations and both contexts | Unresolved associations remain visible |
| CLI | Report-only or opt-in conversion | Deterministic JSON; atomic extra artifact when requested | Existing fatal errors and exit statuses |

</frozen-after-approval>

## Code Map

- `src/pwc_to_dbt/mapping.py` — shared immutable objects; `Export.sources` contains instances, not all definitions. Add report facts with compatible defaults.
- `src/pwc_to_dbt/xml_reader.py` — folder definitions exist before mapping traversal. Retain raw metadata and contextual reader references; keep existing normalized nodes unchanged.
- `src/pwc_to_dbt/dependencies.py` — exact binding validation exists in `plan`; separate reusable validation only as required. Successful SourcePlans are not a complete inventory.
- `src/pwc_to_dbt/project.py` — `compile_models` supplies actual outcomes; `write_project` atomically publishes a fresh file set. Preserve default output.
- `src/pwc_to_dbt/cli.py` — coordinate report-only execution before conversion; existing duplicate-key configuration guard stays active.
- `tests/test_graph_cli.py`, `tests/helpers.py`, `tests/conftest.py` — CLI/output assertions, actual dbt execution and append-only measured history. An existing default-output test expects exactly 13 files.

## Tasks & Acceptance

**Execution:**
- [x] `src/pwc_to_dbt/mapping.py`, `src/pwc_to_dbt/xml_reader.py` — add definition/use/connection evidence without changing SQL interpretation.
- [x] `src/pwc_to_dbt/source_report.py`, `src/pwc_to_dbt/dependencies.py` — implement bounded catalogue, exact binding classification, diagnostics and deterministic report assembly.
- [x] `src/pwc_to_dbt/cli.py`, `src/pwc_to_dbt/project.py` — add the documented report flag and atomic opt-in artifact while preserving old invocations.
- [x] `tests/test_source_report.py`, `tests/test_graph_cli.py` — cover the matrix with a compact functional suite and an actual CLI report/conversion flow.
- [x] `README.md`, `reports/validation.md`, `docs/agent-prompts.md` — document commands, catalogue scope, measured checks, prompt evidence and limitations. Keep native implementation/review notes authoritative.

**Acceptance Criteria:**
- Given the supplied export, when report-only execution runs, then all 12 definitions and 28 uses appear without depending on supported SQL or target selection.
- Given repeated, unused and mixed uses, when reporting runs, then exact identities and explicit bindings determine classification, while producer availability remains separate.
- Given absent, unknown or conflicting metadata, when matching runs, then uncertainty is visible and client compatibility remains unverified.
- Given a conversion with the new option, when outputs publish, then the complete report accompanies both successful and partial results atomically; without it, previous output bytes and exit behavior remain unchanged.
- Given the stable candidate, when focused functional and affected regression checks run, then all required checks pass with actual revision/input evidence and a clear account of untested behavior.

## Implementation Notes

- Added frozen source-definition, association and reader-reference facts to the shared representation with compatible defaults. The XML reader retains all folder SOURCE declarations, exact source instances, qualifier associations, session DSQ associations and distinct workflow task overrides. Existing normalized nodes and SQL interpretation are unchanged. Writer connection references are excluded; invalid/ambiguous reader associations remain unassigned with provenance and diagnostics. Missing metadata remains null or its original empty string, without the emitter's schema fallback.
- Extracted exact configuration identity resolution from target planning. The new offline `source_report.py` builds its inventory independently of target graphs/SQL support. It retains all uses, mixed/unused definitions, unresolved definition references, explicit bindings and separate actual producer outcomes. Report-only producer availability is `not_evaluated`. Bound-use external ingestion remains `not_established`, including when a producer emits, because emission alone does not validate this use's fields or data supply.
- Added `--source-report` for deterministic report-only stdout and opt-in `fivetran-source-report.json` in the writer's existing atomic publication. Target selection remains conversion-only; report scope remains whole export. Existing CLI/output/DTD/entity guards remain active. Default artifact bytes are compared directly with flagged conversion after removing the single extra report artifact.
- Bounded catalogue identity is `fivetran-databases-bounded-v1`, review date 2026-10-28. Oracle, PostgreSQL, MySQL and SQL Server primary documentation and catalogue links were opened on that date; MySQL/SQL Server URLs were followed from the official catalogue. Exact aliases only. Candidate availability, unknown/no-known-match/conflict review states, client-compatibility limits and Oracle table/materialized-view restriction are explicit. No live service/account/database API or extraction was used.
- Initial focused run `20261028T154722-f03774` recorded 85 passing checks and two failing new assertions. The implementation agent had assumed the supplied STG_ORDER_ITEMS producer was unsupported. Actual compilation/report evidence showed it emits; pytest caught the mistaken expectation. Corrected the failed-producer case to inject an unsupported expression and checked partial conversion against actual manifest failures. Product behavior was not changed to fit the mistaken assertions. The subsequent focused run recorded 87 passes. History remains append-only.
- During implementation review, the coordinator caught an overclaim in the draft `external_ingestion` field: producer emission alone had marked a bound use as not needing extraction. Corrected it to `not_established` for all bound uses, retaining `producer_availability=emitted` as a separate fact. A regression emits a producer while an incompatible bound use remains unselected, and asserts the conservative ingestion state. The exact correction prompt is retained in `docs/agent-prompts.md`.
- Stable affected gate: `uv run pytest -q tests/test_source_report.py tests/test_graph_cli.py tests/test_dbt_results.py` → **102 passed in 24.07 seconds**, run `20261028T154947-c70eea`, snapshot `57ca4ef43a516b3b8481683c0e48e8ab5e6002ae+code-sha256:9c366fb67beff38030783253ec0c7e5c7e5e902f6f7b9e9b8748f60ee312257d`. Includes 33 report checks, 57 existing graph/CLI checks and 12 independent result/lifecycle checks. Ten complete-result comparisons and actual first/repeated dbt runs pass. [Measured history](../../reports/test-runs.csv), [command/environment transcript](../../reports/evidence/20261028T154947-c70eea.txt), [human interpretation](../../reports/validation.md). Native review and final coordinator reconciliation remain pending; the larger reference matrix was not rerun.
- Manual supplied report command in Verification completed with exit 0. Its 12 definitions/28 uses have 12 bound and 16 external uses, five mixed definitions, 35 reader connection references and zero unassigned fixture references. Both staging session MART and workflow override RAW contexts are retained. `git diff --check` passed; supplied fixture hashes remain unchanged under the regression checks. No push, publication or submission occurred.

- Coordinator Step3 audit read the staged source/test/document changes against the baseline and reconciled the measured CSV/evidence. All five tasks and every Given/When/Then acceptance criterion are satisfied within the stated MVP scope; every I/O matrix row has an executed passing test. [Coordinator baseline and matrix receipt](../../reports/evidence/20261028-source-report-coordinator-baseline.json) records exact tests and sample report counts. Default required-target output is byte-identical across all13files; whole-export partial output is byte-identical across all17files, with unchanged exit0/1. The original baseline was reconstructed outside the repository. Its first probe used host Python3.9 and failed on the project's3.13syntax; rerunning with the repository3.13interpreter corrected the probe without product changes. Native independent review follows; no approval or result scope is inferred beyond these checks.

- Bounded native review corrections (D75): qualifier readers now require both complete qualifier and DSQ evidence before assignment; direct SOURCE readers apply DSQ validation too. Inherited DSQ linking reuses the real session declaration and labels inherited provenance, without fabricating task-local association rows. Final contextual disagreement/ambiguity/absence errors are retained on the original association evidence with explicit failing-context diagnostics. Worklet-contained sessions/tasks remain unresolved and unassigned with an unsupported-scope diagnostic; no worklet precedence resolver was added.
- Report correction: one shared three-field completeness predicate covers missing/whitespace CONNECTIONNAME, CONNECTIONSUBTYPE and CONNECTIONTYPE at reader and definition level. Technology conflicts use wording that does not invent an absent source type. Catalogue, per-row checks and candidate limits are copied independently. Failed bound uses include the actual producer outcome reason, retaining bound classification and unchecked ingestion.
- Correction regressions preserve populated OWNERNAME and DBDNAME exactly and verify used same-name definitions in two folders retain their exact definition/use/binding/reader ownership. Additional compact cases cover every corrected review outcome. `uv run pytest -q tests/test_source_report.py` → **44 passed in 1.90 seconds**, run `20261028T160132-14df09`, snapshot `57ca4ef43a516b3b8481683c0e48e8ab5e6002ae+code-sha256:c911d0bd085dc9a3788bd68e57faaa344e6fb1c6cfffac9d5fdc955458242c4f`; [actual transcript](../../reports/evidence/20261028T160132-14df09.txt). No wider verification was run during correction; final verification belongs to the coordinator. `git diff --check` passed. B5/E1 remain the separately triaged unchanged source-only input restriction; README/report now state at least one mapping is required. Frozen intent and review triage are unchanged.

- Final coordinator verification: `uv run pytest -q tests/test_source_report.py tests/test_graph_cli.py tests/test_dbt_results.py` passed113checks in10.16seconds, run20261028T160227-d20777, at snapshot57ca4ef43a516b3b8481683c0e48e8ab5e6002ae+code-sha256:c911d0bd085dc9a3788bd68e57faaa344e6fb1c6cfffac9d5fdc955458242c4f. Reconciled114CSV rows including the invocation,44report/57graphCLI/12dbtchecks, all evidence paths and current code fingerprint. [Final receipt](../../reports/evidence/20261028-source-report-final-receipt.json) confirms all13required and17partial default artifacts still match baseline bytes and exits. Regenerated sample report has12definitions/28uses,12bound/16externaluses,35readerreferences,56actualassociationdeclarations and no fabricated taskDSQdeclarations. No code changed after this passing run; later writes only close native/report evidence.
- Review closure: B1-B4/B6-B10 and G1-G2 are corrected and covered in the44reportchecks; all three native layers completed. B5/E1 remain one documented baseline source-only input restriction in deferred-work.md. No other confirmed finding remains open. The complete frozen intent hash is unchanged. Native Build Step5 marks this local MVP done; live client compatibility, worklet/override resolution and bound-use data availability remain unverified. Full reference matrix was not rerun, and no push/publication/submission is authorized.

## Spec Change Log

## Review Triage Log

All three native layers returned before triage. Coordinator reproduction evidence is [review probes](../../reports/evidence/20261028-source-report-review-probes.json). Each finding was classified before grouping; the source-only pair shares one pre-existing reader guard. Corrections are bounded patches under unchanged frozen intent, not a design loopback.

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Blind B1: incomplete qualifier/DSQ evidence still assigns readers | medium | Reproduced both single omissions: source_uses remains assigned while absence diagnostics are present. Patch validation ordering so incomplete associations stay unassigned; regress both omissions. |
| Blind B2: direct source reader skips DSQ errors | medium | Direct SOURCE reader with DSQINSTNAME=ABSENT plus connection reference produces an assigned row with empty diagnostics. Patch existing DSQ validation into this branch before assignment. |
| Blind B3: inherited declarations appear task-local | medium | Fixture has zero task DSQ declarations but report contains seven task DSQ association rows. Patch retained declaration provenance; inherited linking must not fabricate task-local declarations. |
| Blind B4: association diagnostics omit contextual conflicts | low | Reproduced mismatched qualifier/session evidence with empty association diagnostics and a disagreeing reader diagnostic. Patch finalization of the already-reported association evidence so scoped validation errors are visible there too. |
| Blind B5: source-only exports rejected | medium | Current and baseline read_xml both reject a valid SOURCE-only file with No mappings found. Defer the unchanged reader input restriction, explicitly document it; no new parser shape is claimed for this MVP. |
| Blind B6: incomplete definition summary | low | Removing CONNECTIONTYPE produces reader-level missing-field diagnostic but no incomplete declaration summary. Patch the existing completeness predicate to cover all three fields and whitespace. |
| Blind B7: conflict wording overstates source evidence | low | With missing DATABASETYPE and conflicting reader subtypes, the summary falsely names a source-to-reader disagreement. Patch to accurate general technology-declaration wording; preserve raw evidence. |
| Blind B8: report mutates shared catalogue/check lists | low | Mutating a returned report changes a later report review date and clears other rows checks. Patch report boundary copies, including per-row lists; no new public interface. |
| Blind B9: worklet scope collapses to folder/workflow | medium | Moving the reusable session into WORKLET still attaches its readers and resolves the workflow task as if folder scoped, without diagnostics. Patch by explicitly diagnosing unsupported worklet scope and leaving its reader evidence unassigned; do not add worklet resolution. |
| Blind B10: failed producer reason omitted | low | Unsupported UNKNOWN expression yields a failed bound producer with empty use diagnostics while its outcome contains the reason. Patch by copying the existing failure reason into use diagnostics. |
| Gap G1: populated owner/database evidence not asserted | medium | Accepted pre-verified regression gap: existing checks assert missing metadata only. Add one controlled XML check for distinct populated OWNERNAME/DBDNAME values under their correct report keys. |
| Gap G2: used definition ownership across folders untested | medium | Accepted pre-verified regression gap: duplicate-name test uses unused definitions only. Add compact used same-name definitions in two folders, verifying exact use/binding/reader ownership. |
| Edge E1: source-only report rejected | medium | Same unchanged No mappings found reader guard as B5; retain an individual verdict, group the shared cause for one documented deferral. |


## Design Notes

Inventory is independent of conversion. Source definitions own multiple exact uses; the sample has mixed STG bindings. Reusable staging readers name MART_Jaffleshop while workflow task overrides name RAW_Jaffleshop: retain both, without runtime precedence claims. The catalogue is versioned offline data; no match does not establish vendor-wide absence. Report-only producer availability is not evaluated.

## Verification

**Commands:**
- `uv run pytest -q tests/test_source_report.py tests/test_graph_cli.py` — core report and existing CLI/graph checks pass.
- `uv run pytest -q tests/test_dbt_results.py` — existing independent result/lifecycle checks pass where required by shared reader/writer changes.
- `uv run pwc-to-dbt fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml --source-report --bindings examples/sample-bindings.json` — inspect complete inventory and explicit limits.
- `git diff --check` — no new whitespace errors; supplied fixtures remain unchanged.
