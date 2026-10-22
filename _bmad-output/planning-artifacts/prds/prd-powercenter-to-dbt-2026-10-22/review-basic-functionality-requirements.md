# Basic-stage requirements audit

Read on 22 October 2026 after user direction U63. Compared the original employer brief and recruiter excerpt in `docs/assignment.md`, `AGENTS.md`, `README.md`, current `prd.md`/`addendum.md`, native `SPEC.md` and both companions, and `_bmad/custom/bmad-build.toml`, `bmad-build-auto.toml` and `bmad-retrospective.toml`. This is a contract/documentation audit, not implementation verification or final owner signoff.

## Requirement mapping

| Requirement and authority | Basic-stage coverage | Actual evidence status |
|---|---|---|
| Read supplied PowerCenter XML and explain its mapping (employer). | PRD FR-1, §4.1, §13; native CAP-1; addendum/source research. | Source inspection and original fixture/provenance exist. A running converter does not. |
| Derive equivalent dbt output from XML, without fixed Jaffle Shop SQL (employer). | FR-2–FR-4, SM-1/SM-2; CAP-1. Complete incoming graph and exact port wiring are required. | Design covered; generated models, independent results and mutation evidence pending. |
| Include tests (employer). | FR-6; SM-1–SM-3; CAP-2; native validation companion. | Required before basic completion, not a bonus. No converter test results exist yet. |
| Reasonable coverage in approximately four hours; reasoning over exhaustive support (employer). | PRD §1, §4–§5, §8, §10; native constraints. | Five approved targets are a verification floor, not a name allowlist/output cap. All sixteen targets, arbitrary XML and universal conversion are not employer mandates. |
| Coding-agent use with clear process (employer). | FR-9; CAP-4; AGENTS; addendum process evidence. | Agent-assisted preparation exists. Do not describe preparation reviews as implementation/review completion. |
| Candidate understands and can explain any submitted code (employer). | FR-8 and §2; CAP-4. | Product code and Saar's code-understanding review remain pending. |
| README: actual run instructions (employer item 1). | FR-8, SM-3, AGENTS README maintenance. | Setup commands exist; converter commands and clean-checkout verification are pending. |
| README: assumptions and deliberately unsupported cases (item 2). | FR-8; §8/§12; CAP-4. | Draft boundaries exist; final README must match implemented and verified behavior. |
| README: likely wrong-output cases and reasons (item 3). | FR-8; §11; FR-7. | Research risks exist; final evidence-based limitations remain pending. |
| README: a genuine agent mistake and how caught (item 4). | FR-8/FR-9; AGENTS; addendum process evidence. | Setup scope incident is already documented once in README. Later language correction has prompt/native evidence. Do not invent another error. |
| Prompts beginning with initial prompt, plus full conversation export if supported (item 5). | FR-8/FR-9; AGENTS; addendum export limits. | Curated exact available prompt record exists with omissions/redactions disclosed. It is not a full export; desktop export availability is not established. A supported export cannot be waived by the prompt list. |
| README: short actual process outline (item 6). | FR-8/FR-9; CAP-4. | Native preparation history exists. Final process must describe the build/tests/reviews actually performed, not proposed stages. |
| Sensible handling, visible breaking points and clear README reasoning (employer). | FR-3/FR-5/FR-7/FR-8; CAP-2–CAP-4. | Covered by explicit diagnostics, supported/unsupported/unverified separation and concise evidence links; execution remains pending. |
| Reproducible repository or zip handoff; deadline and later notification (employer). | FR-8 submission checklist; §13; AGENTS transparency. | The records say public access was verified; this audit did not recheck it. Local drafts still need publication. External deadline is 23 October; actual submission/notification require separate authorization. |
| Capture directions, decisions, prompts, actual commands/results and genuine corrections during work (later user direction). | FR-9; native constraints; AGENTS work-unit rule; Build/Auto completion reminders and retrospective checklist. | Policy is present now. Hooks remind maintainers; their presence does not prove future capture or workflow execution. |
| Minimal measured CSV/report and practical next work (user addition). | FR-7; CAP-3; native validation companion. | Included in agreed basic completion, with real runs and separate denominators; no fabricated rows. Not an employer substitute for conversion/tests/README. |
| Convert supported preparation commands, including customer cleanup (user-approved addition). | A5, FR-4; CAP-1; both native companions. | Basic scope includes generated steps and local lifecycle/repeated-load tests. Converter does not execute imported commands. Arbitrary workflow support remains excluded. |
| Open BMAD, approved Python stack and separate dependency-analysis file (user additions). | FR-9, §10; native constraints; addendum stack/dependency sections. | Tooling and contract exist; Build, product environment and implementation remain pending. |

Jaffle Shop is an optional comparison/reference method under the employer brief. It must not become an excuse to copy fixed SQL or compare mismatched schemas/rules. Independent expected-result tests are valid. The background reading is reference material, not a requirement to add every transformation or reproduce every runtime feature.

## Ongoing evidence capture

The current policy correctly makes documentation part of every authorized work unit: exact available prompts and actual delegated prompts in the single prompt source; requirements/decisions/corrections in native memory and companions; commands, verification and review in their native records; actual test rows in one CSV with links rather than duplicate result logs; affected README sections maintained as behavior becomes real. Build and Build Auto completion reminders expressly invoke this policy; the retrospective checks every original submission item and requires honest disclosure of missing evidence.

The repository handoff must include relevant source, tests, supplied material/provenance, BMAD and shared configuration, requirements/native history, research, prompts, implementation/review evidence, measured reports, CI and dependency manifests/locks. Exclude dependencies/caches, credentials, machine-only settings and confidential third-party context. Distinguish local files from committed/published files. The complete record and privacy rules are basic handoff work, not optional extras.

## Explicit basic-stage completion gate

Basic is complete only when all the following hold on the identified final tested revision:

1. The approved converter derives runnable DuckDB dbt models for all five required complete target paths, with exact lineage and relevant semantic boundaries established. Reusable rules are not restricted to five names. No silent repair of source wiring, skipped logic or fixed Jaffle Shop output is accepted.
2. Required independent result, XML mutation, edge, negative and determinism checks pass, and generated models execute through actual dbt. Supported preparation steps pass local first-run/repeated-load tests. Skips, unsupported cases and unverified behavior are explicit.
3. Real measured runs and a concise summary identify revision, fixture, environment, strengths, limitations and practical acceptance-tested next work. Separate outcome, result and path-coverage measures; preserve earlier failures as history.
4. The short README contains all six employer items with working commands and authoritative evidence links. Available prompts begin with the initial request; include a full export if supported and disclose any unavailable/redacted history honestly. Actual error detection/correction and process evidence are current through that revision.
5. Saar can explain the submitted code and trace outputs back through XML and implementation. Do not infer this check passed merely because agents wrote documentation.
6. Clean-checkout execution and public-review handoff are checked with relevant records included and confidential/private/machine-only content excluded. Confirm the required evidence is actually published or included in the zip, not merely present locally. Actual submission and recruiter notification remain separately authorized logistics.

All employer obligations above belong to basic delivery. Reporting, supported preparation and workflow transparency are additional user-approved basic obligations. Only additional transformation semantics/outputs beyond this completed gate are bonuses. Preparing evidence continuously and making final completion contingent on it prevents a feature-only result from being called basic-complete.

## Findings and verdict

No employer requirement is assigned to bonuses or replaced by research/best-practice additions. Native CAP-4, PRD §4.1 and FR-8/FR-9 already require README/reporting/evidence for core completion; AGENTS and completion reminders preserve capture during work.

One presentation ambiguity should be removed: PRD §5 lists “Reusable additional outputs” before “Final evidence and handoff.” Although §4.1 already gates the core on measured reporting and a reproducible README, the stage list could suggest that all documentation waits until after bonuses. State that all six employer README items and current prompt/decision/error evidence are part of basic completion before optional expansion; the later final stage only refreshes/rechecks evidence after any bonus work.

No product implementation, generated-model execution or measured accuracy is delivered yet. Final PRD signoff and native Build preparation remain pending. This audit establishes planned requirement coverage only.

## Finding disposition

Resolved during this audit: PRD §4.1 and repository AGENTS.md now explicitly make all six employer README/evidence obligations part of basic completion. PRD §5 now places measured reports, reproducible instructions and current prompt/decision/error evidence in the core-verification/basic-handoff stage before bonuses. Its later handoff stage only reruns relevant checks and refreshes existing evidence. This clarifies the completion gate; it does not claim those deliverables already exist.
