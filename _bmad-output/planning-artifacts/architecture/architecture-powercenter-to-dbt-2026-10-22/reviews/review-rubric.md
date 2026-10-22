# Architecture rubric review

**Verdict: PASS for architecture finalization. No critical, high or medium material findings.** The feature-level spine fixes the relevant component and data-integrity divergence points, covers CAP-1–CAP-4 and remains consistent with the approved PRD. This verdict is not product implementation readiness, dependency compatibility, semantic verification or completed conversion evidence.

## Reviewed inputs and limits

Read `ARCHITECTURE-SPINE.md`, the good-spine checklist in `bmad-architecture/references/reviewer-gate.md`, the canonical SPEC and its validation/source-compatibility companions, the current approved PRD and `research/06-core-semantics-check.md`. Checked that no `src/`, `tests/`, `pyproject.toml` or `uv.lock` product artifacts were present in the bounded file inventory. No product code was written, no commands from the export were executed and no new product decisions or external research were introduced.

The coordinator supplied the clean deterministic linter result and completed input-reconciliation status; this reviewer did not claim to rerun those checks. Runtime dependency installation and compatibility testing remain explicitly unperformed.

## Good-spine checklist

| Criterion | Result and reasoning |
|---|---|
| Fixes real divergence points | Pass. Shared identity/schema ownership, exact field lineage, checked-plan entry into generation, module responsibilities, target/CTE granularity, relation bindings, partial-result propagation and preparation semantics are decided rather than left to independent builders. |
| Every AD has an enforceable rule that addresses its divergence | Pass. See per-rule review below. Rules identify concrete artifacts, interfaces, diagnostic states or verification gates; they are not only intentions such as “be accurate.” |
| Safe deferrals | Pass at feature altitude. Exact interfaces/grammar are assigned to one native Build contract before coding; package pins are centrally resolved and locked before any agent uses the environment. These are gated shared decisions, not permission for parallel components to invent incompatible representations or dependencies. Deferred new products/semantics require fixture-backed support and are not implicit capabilities. |
| Named technology and brownfield fit | Pass within the stated evidence boundary. The spine records the existing Python/uv/BMAD tooling and distinguishes those verified tooling versions from uninstalled product/test runtime packages. It does not claim adapter compatibility or installed dbt/DuckDB versions. No existing product implementation is contradicted; the structural seed is expressly future organization. Installation, central pins and a runtime smoke check remain implementation-preparation obligations. |
| Capability coverage | Pass. CAP-1 has the complete reader/planner/translation/output chain; CAP-2 has diagnostics and independent execution/result checks; CAP-3 has one authoritative measured history and a concise revision/environment summary; CAP-4 has runnable output, reproducible commands, original-fixture preservation and all six submission-evidence obligations. Native reporting companions supply the detailed counts/schema without a competing report definition. |
| Inherited constraints | Pass. No parent architecture is asserted. The spine preserves the SPEC/PRD's target minimum without an output allowlist, DuckDB output, separate dependency file, preparation conversion, source semantics, column order, meaningful sorting and visible unsupported cases. |
| Operational/environmental envelope | Pass for a local CLI feature. Conversion is offline with respect to model APIs and databases; validation uses controlled local fixtures. No cloud/server/auth/production/extraction infrastructure is introduced. External DTD/entity access, imported-command execution during conversion, credentials, output ownership and deterministic artifacts have explicit boundaries. Publishing/submission remains separate. |

## Invariant enforceability

| Rule | Review |
|---|---|
| AD-1 | A checked target plan is the required generator input; original mapping/instance/port identities remain traceable. This prevents bypassing unresolved connections. |
| AD-2 | Representation, XML, dependency, expression, SQL, writer and CLI ownership are separate; independent expected values cannot import production translation helpers. Import boundaries and shared types can be checked directly. |
| AD-3 | One target model, internal CTEs, XML column order and collision rejection prevent incompatible output layouts or implicit identity merging. |
| AD-4 | Exact configured source-to-producer bindings, recursive producer inclusion and `ref`/`source` separation prevent guessed or dangling cross-mapping dependencies. Invalid bindings must fail before emission. |
| AD-5 | Four explicit target outcomes, dependency failure propagation, nonzero CLI status, nonempty-destination refusal and current-run artifact/inventory ownership prevent stale or partial output being called complete. |
| AD-6 | Structural expression parsing and contextual rejection of unknown settings prohibit silent translation guesses. The referenced bounded source rules and verification-before-support gate preserve unresolved numeric/default/date limits rather than pretending they are proven. |
| AD-7 | Preparation classification is separate from SELECT translation and conversion never executes imported commands. Exact relation resolution, first/repeated-run tests and blocking unsupported required preparation preserve the approved cleanup requirement. |
| AD-8 | Actual dbt execution, independent full-result comparisons, mutation/rejection/preparation checks, distinct coverage measures and basic-stage README/process evidence prevent compilation or breadth from replacing correctness and handoff. |

## Remaining gates, not architecture defects

Before implementation, the one native Build contract must settle shared interfaces and expression grammar, lock compatible runtime dependencies and carry the recorded semantic boundaries into executable checks. Before claiming support, verification must establish the reached conversion/default/date/string rules and preparation lifecycle. The architecture explicitly preserves these gates; finalizing this spine must not be described as passing them.

No spine edits are requested by this rubric review.
