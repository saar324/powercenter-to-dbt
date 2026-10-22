---
status: final
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
inputDocuments:
  - _bmad-output/specs/spec-powercenter-to-dbt/SPEC.md
  - _bmad-output/planning-artifacts/prds/prd-powercenter-to-dbt-2026-10-22/prd.md
  - _bmad-output/planning-artifacts/architecture/architecture-powercenter-to-dbt-2026-10-22/ARCHITECTURE-SPINE.md
---

# powercenter-to-dbt - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for powercenter-to-dbt, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Read the supplied XML; inventory all mappings/targets and retain exact source/definition/instance/port identities. Diagnose malformed input, missing links and cycles.
FR2: Select complete targets and recursively include required generated producers. Apply explicit cross-mapping bindings; validate consumed columns/types and diagnose ambiguity. Supported rules apply beyond the five-target verification minimum.
FR3: Derive SQL from connector lineage and supported source/expression/join/aggregation/sorter semantics, preserving types, null/default behavior and actual crossed price wiring. Reject unsupported variants; no fixed Jaffle Shop output.
FR4: Emit one model per target with CTE steps, dbt project/config/source declarations and local profile. Generate supported preparation steps separately, verify first/repeat-run lifecycle, resolve source/ref dependencies and keep conversion free of SQL execution/live extraction.
FR5: Diagnose affected mapping/target/operation. Retain complete independent outputs, block dependents of failed producers, return nonzero for any selected failure and prevent stale files appearing as current success.
FR6: Execute core models through dbt on controlled data; compare independent expected columns,values,duplicate counts. Test relevant null/empty/duplicate/unmatched/numeric/date cases, XML mutations,rejection,sort settings,determinism and preparation repeat runs. Reference comparison only with matched schemas/rules.
FR7: Produce actual reports/test-runs.csv and concise reports/validation.md with revision,input,environment,case counts and separate outcome/result/coverage measures. Preserve history and concrete evidence-backed next work; no fabricated or universal accuracy claims.
FR8: Basic-stage README includes reproducible commands,assumptions/exclusions,wrong-output risks,a genuine agent error/detection/correction,prompts from initial plus shareable full export if supported,and actual process. Saar can trace/explain code; prepare reproducible repository/ZIP for reviewer access without submitting or messaging now.
FR9: Capture prompts,decisions,real agent corrections and verification evidence as work occurs in native BMAD and the authoritative prompt record. Preserve original hashes and transparent tooling metadata; label unavailable history/redactions honestly.

### NonFunctional Requirements

NFR1: Python3.13 CLI,uv lock,ElementTree,typed mapping data,argparse,explicit SQL rules,pytest and local DuckDB/dbt-duckdb verification; no converter model API or service.
NFR2: Deterministic generated artifacts for identical input/configuration; exact identity,collision checks and one canonical checked ModelPlan consumed by all stages.
NFR3: Do not modify original fixtures,fetch external DTDs or expand external entities. Use controlled local fixture data; no live database writes or imported-command execution during conversion.
NFR4: Separation of XML reading,graph analysis,translation,file/project writing,CLI and independent validation. Planner owns names/contracts; writer owns dbt lifecycle/hooks.
NFR5: Keep effort around four hours from16:34Sofia22October,flexible20:30target; complete tested basic stage and all employer evidence before bonuses. No artificial five-target capacity cap.
NFR6: Preserve privacy/exact prompt provenance and exclude installed dependencies,caches,credentials and the confidential earlier project. Share relevant BMAD/source/test/config/lock/evidence records.
NFR7: Unknown semantics block affected support; tested evidence must distinguish emitted,executable,result-checked and unsupported paths. Controlled date-test context never silently fixes production year.

### Additional Requirements

- Follow architecture AD1–AD8; no starter,UI,cloud deployment,authentication or new scheduler.
- Shared mapping identities include repository/folder/mapping,instance and exact field. Source/intermediate/target types and output-error defaults remain distinct.
- Initial core: STG_CUSTOMERS,STG_ORDERS,STG_PRODUCTS,STG_SUPPLIES and core CUSTOMERS; source-equivalent rules also work for other targets after verification.
- Supported setup translation includes customer cleanup, typed intent classification and dbt-resolved relation ownership. Explicit original relation metadata may supply export omissions.
- Define shared stage interfaces centrally before parallel implementation; centrally resolve/lock/test package compatibility.
- Use research/06-core-semantics-check.md for bounded source evidence and carry join,date,precision,null,error/default cases into verification.
- No source-system runtime equivalence,installed dependency compatibility or passing results claimed by planning artifacts.

### UX Design Requirements

Not applicable: approved CLI has no UI design contract.

### FR Coverage Map

FR1: Epic 1 — XML discovery
FR2: Epic 1 — complete graph selection
FR3: Epic 1 — rule-based translation
FR4: Epic 1 — runnable project and preparation
FR5: Epic 1 — explicit failures/partial results
FR6: Epic 1 — independent execution/result tests
FR7: Epic 1 — measured reporting
FR8: Epic 1 — all six README obligations
FR9: Epic 1 — continuous BMAD/prompt evidence

## Epic List

### Epic 1: Convert and verify PowerCenter mappings for reviewer use

Saar can convert supported XML into a runnable dbt project,prove the five required target paths and setup behavior,inspect explicit failures and share reproducible evidence. The same supported rules can cover further targets without a name allowlist.

**FRs covered:** FR1,FR2,FR3,FR4,FR5,FR6,FR7,FR8,FR9. All NFRs and AD1–AD8 apply. One cohesive user outcome; no technical-layer epics. Core completion precedes optional verified reuse.

## Epic 1: Convert and verify PowerCenter mappings for reviewer use

Deliver the approved XML-derived converter, locally executable dbt project and basic-stage evidence. Story dependencies are sequential; no story requires future work to demonstrate its own outcome.

### Story 1.1: Generate and run a first XML-derived model

As a reviewer,
I want to convert a simple target from the supplied XML and run the generated dbt model,
So that I can confirm the tool reads actual mapping connections and can reproduce a result.

**Requirements:** FR1,FR2,FR3,FR4,FR5,FR6,FR7,FR8,FR9; AD1–AD5,AD8. No starter template is required.

**Acceptance Criteria:**

**Given** the supplied export and a fresh destination,
**When** I inspect the export and select STG_CUSTOMERS,
**Then** the inventory records three mappings and sixteen targets with exact instance/definition/field identities,
**And** generated columns follow the XML connections and target order,with one model,required local dbt configuration and the supported customer preparation step.

**Given** controlled customer rows and the generated project,
**When** I execute the model through dbt,
**Then** complete rows match independently stated expected values and duplicate counts,including customer cleanup on first/repeated runs,
**And** an XML rename mutation changes the generated column without a name-based SQL template.

**Given** malformed XML,missing links or a nonempty destination,
**When** I run conversion,
**Then** I receive contextual errors/nonzero status and no misleading stale success,
**And** no external DTD/entity retrieval or database command occurs during translation.

**Given** the first real work unit,
**When** it completes,
**Then** run evidence,actual prompts/decisions/errors and current README instructions are recorded truthfully with the working revision/environment.

### Story 1.2: Convert and verify the complete basic mapping paths

As a reviewer,
I want the approved relational rules and preparation behavior to work across complete targets,
So that I can assess a reusable converter rather than a fixed demonstration query.

**Requirements:** FR1–FR9; all NFRs and AD1–AD8. Depends only on Story1.1.

**Acceptance Criteria:**

**Given** the supplied export,explicit source-to-producer bindings and controlled raw rows,
**When** I select the five required targets,
**Then** STG_CUSTOMERS,STG_ORDERS,STG_PRODUCTS,STG_SUPPLIES and core CUSTOMERS execute through dbt in dependency order and match independent complete expected outputs,
**And** expressions,normal/master-outer joins,grouping,sort effects,column order,source/intermediate/target casts,nulls and error-default boundaries follow the documented supported profile without correcting the crossed product wiring.

**Given** the reached two-digit-year date and numeric/default rules,
**When** focused boundary tests run,
**Then** recorded clock context,century/time/null/invalid-date handling and declared precision/rounding behavior are independently checked,
**And** exact-version/runtime-equivalence limits and unverified ranges remain explicit rather than claimed proven.

**Given** supported customer cleanup and a first/repeated local dbt run with stale rows,
**When** generated preparation executes,
**Then** the correct dbt-resolved target relation is prepared in compatible lifecycle order and stale rows are removed,
**And** unsupported required preparation blocks its target; unrelated workflow commands are reported as unconverted.

**Given** a bad binding,unsupported expression/cycle or failed generated producer,
**When** conversion runs,
**Then** consumed field/type compatibility and transitive failures are enforced,
**And** independent complete outputs can be retained with an explicit incomplete inventory and nonzero selected-failure status.

**Given** XML mutations and edge-case rows,
**When** tests exercise every supported core operation category,
**Then** arithmetic/conditions/renames/joins/grouping/sorting and meaningful settings respond as independently expected,
**And** ordinary nulls,empty strings,duplicates,unmatched/null join keys,empty inputs and invalid/out-of-domain values are tested without counting correct rejection as support.

### Story 1.3: Reproduce and explain the verified basic submission

As Saar and the evaluator,
I want a reproducible working package with concise evidence and limitations,
So that I can run it,understand its code and assess its measured behavior.

**Requirements:** FR6,FR7,FR8,FR9; all basic-stage completion gates. Depends only on Stories1.1–1.2.

**Acceptance Criteria:**

**Given** the completed basic implementation and locked dependencies,
**When** I follow the README from a clean checkout,
**Then** documented conversion and real dbt/result verification commands pass,
**And** CI runs the actual relevant converter tests instead of only repository-setup checks.

**Given** actual executions including failures/reruns,
**When** reports are produced,
**Then** one CSV retains real run history and one concise Markdown summary identifies final revision/environment,outcome counts,complete-result checks and coverage separately,
**And** verified strengths,unsupported/unverified risks and each practical next change/acceptance test are clear.

**Given** the original assignment,
**When** basic completion is assessed,
**Then** all six short-README obligations and relevant BMAD/prompt/review/dependency evidence are ready before optional outputs,
**And** actual agent errors have detection/correction evidence,missing full-export availability is stated honestly,and supported export capability is used if available.

**Given** the submitted code and one generated column,
**When** Saar reviews the implementation,
**Then** its responsibilities and XML-to-SQL trace can be explained,
**And** the public repository/ZIP can include source/tests/config/locks/evidence without installed packages,credentials or confidential context.

Further outputs using existing rules may be verified after this basic gate; new unsupported semantics remain future work with concrete tests. This optional reuse is not a separate mandatory story and never an output-name cap.
