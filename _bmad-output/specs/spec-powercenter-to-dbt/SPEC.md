---
id: SPEC-powercenter-to-dbt
companions:
  - ../../../docs/assignment.md
  - source-compatibility.md
  - validation-and-reporting.md
  - ../../planning-artifacts/prds/prd-powercenter-to-dbt-2026-10-22/prd.md
  - ../../planning-artifacts/prds/prd-powercenter-to-dbt-2026-10-22/addendum.md
  - ../../planning-artifacts/architecture/architecture-powercenter-to-dbt-2026-10-22/ARCHITECTURE-SPINE.md
sources: []
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# PowerCenter mapping to dbt

## Why

Meet Infinite Lambda's take-home brief with a small, explainable converter that derives dbt models from PowerCenter mapping XML. Saar wants a complete tested core, visible BMAD development evidence and a concise account of measured behavior and limits. The broader cross-product migration ambition reported by Saar informs future work, not an assumed universal conversion promise.

## Capabilities

- **CAP-1**
  - **intent:** Convert supported PowerCenter mapping logic into equivalent dbt SQL models without fixed Jaffle Shop output.
  - **success:** The five required complete paths in the adopted PRD produce runnable DuckDB dbt models, and supported XML changes alter behavior as independently expected. Supported preparation commands also produce locally verified equivalent steps; unconverted commands are explicit. Reusable supported rules apply beyond the five-target verification minimum.
- **CAP-2**
  - **intent:** Verify supported conversions and expose unsupported behavior.
  - **success:** Actual tests check independent expected results, XML changes and relevant edge/rejection cases; evidence separates successful execution from correct results under the tested conditions.
- **CAP-3**
  - **intent:** Let reviewers assess measured behavior, strengths, limits and practical next work.
  - **success:** A minimal run CSV and concise summary distinguish test outcomes, result checks and path coverage by actual input, condition, environment and stage; each improvement names a concrete change and acceptance test, as defined in `validation-and-reporting.md`.
- **CAP-4**
  - **intent:** Provide a transparent, reproducible handoff that Saar can explain.
  - **success:** The short README covers every submission requirement in `docs/assignment.md` and links actual prompts, native BMAD records, verification evidence and the documented agent correction; supplied fixtures remain unchanged.

## Constraints

- Aim for about four hours from 16:34 Europe/Sofia on 22 October 2026, including understanding, planning, agent coordination, testing and documentation. The 20:30 finish is a target, not a hard cutoff; 20:40 is acceptable, and finish work in progress when needed. Keep effort near four hours and complete a working tested core before optional extensions.
- Individually approved scope decisions are recorded in the adopted PRD and its addendum. Final PRD signoff is resolved in U64; required native architecture, stories, readiness and Build preparation precede product code changes; removed setup analysis and superseded proposals are not approved inputs.
- Use the installed official BMAD workflows openly in the repository; keep native requirements, implementation and review records authoritative instead of duplicate work logs.
- Use Saar's approved Python command-line stack and local verification tools specified in `source-compatibility.md`; generated SQL targets DuckDB. Keep dependency analysis in a separate Python file.
- Capture actual prompts, decisions, real agent mistakes and their detection/correction as work proceeds. Include relevant BMAD, research, verification and dependency records; exclude installed packages, credentials and confidential third-party context. Do not reconstruct unavailable history or claim a curated prompt list is a full supported export.
- Use five to ten relevant specialist subagents in successive groups where useful; respect the platform limit of four active agents including the coordinator. Do not treat user-described model settings as verified metadata or guaranteed throughput.
- Follow the adopted architecture AD-1–AD-8: separate responsibilities, one authoritative checked graph/model plan, target model files with project configuration, explicit relation bindings and failure propagation.
- Preserve product/version compatibility boundaries from `source-compatibility.md`. Establish source date/join/type/null/error rules before implementing their translation; unknown meaning blocks affected support. Preserve target column order and meaningful sorting; compare all row values and duplicate counts without incidental display-order equality. Report only actual runs, inputs, revisions and environments.

## Non-goals

- Claim support for arbitrary XML, all ETL products, all PowerCenter releases or every transformation without evidence.
- Build optional coverage before the agreed core works and is tested.
- Add a UI, cloud service, live PowerCenter connection, automatic synchronization or submission action without a corresponding agreed requirement.

## Success signal

Within the time box, Saar can demonstrate conversion of the agreed complete XML paths, run the generated dbt models, explain how the rules were derived and show independent result checks. Reviewers can reproduce the result and identify unsupported, unverified and remaining work from measured evidence rather than a claimed universal accuracy score.

## Open Questions

- No product-scope question is currently open; U64 approves the consolidated PRD. The architecture is reviewed; complete required native stories/readiness and Build preparation before implementation.
- Verify source-specific join, date, numeric, null and error semantics during native preparation; return only concrete unresolved support or effort decisions to Saar.

Source-rule checks and native planning/readiness gates remain. The PRD and scope are approved; no product implementation or submission has started.
