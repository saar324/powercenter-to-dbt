# Assignment and user source reconciliation

This is a source extract for PRD preparation, not an approved PRD, an implementation plan or evidence that a converter exists. Read on 22 October 2026. Sources: `docs/assignment.md`; `docs/agent-prompts.md` U01–U28 and D01–D05; `README.md`; `AGENTS.md`; `_bmad-output/specs/spec-powercenter-to-dbt/SPEC.md`, `.memlog.md`, `source-compatibility.md` and `validation-and-reporting.md`. The supplied assignment and user prompts take precedence over an agent's interpretation. Removed setup analysis and unavailable assistant history were not consulted or reconstructed.

## Original assignment requirements

- Build a small, explainable converter from Informatica PowerCenter mapping XML to equivalent dbt models. Read the supplied sample and establish what its mappings do. Derive output from the XML; fixed Jaffle Shop output is prohibited. Any implementation language is permitted by the brief.
- Include tests. The public Jaffle Shop DuckDB project is an available reference, not a requirement to reproduce an unrelated schema or every reference model. Handle a reasonable subset in approximately four hours; reasoned limits matter more than complete operation coverage.
- Use coding agents as part of development. The candidate must understand and be able to explain any submitted code. Show sensible conversion handling, clear boundaries and clear reasoning in the README.
- Original public source: `https://github.com/infinitelambda/flowline-pwc-demo`. Original reference: `https://github.com/dbt-labs/jaffle_shop_duckdb`. Original source/reference links and background reading remain in `docs/assignment.md`.
- Logistics: approximately four hours, do not over-invest; assignment says one week from receipt. Preserved recruiter excerpt specifies 23 October 2026. This external deadline differs from the user's internal working stop. Questions may be directed to Chau; the preserved excerpt asks notification after submission. Neither instruction authorizes this agent to submit or message anyone now.

### Exact submission checklist

Submit a GitHub repository, public or private with access granted to the stated reviewer handles, or a zipped folder. The source uses `[GitHub handles]` as an unresolved placeholder; actual reviewer access details are not established. Include a short README covering:

1. How to run it.
2. What was assumed and deliberately not handled.
3. Where the converter is most likely to produce wrong output.
4. Where a coding agent got something wrong and how the candidate caught it.
5. Prompts given to the agent, beginning with the initial prompt; include a full conversation export if the tool supports export.
6. A short outline of the process followed with the agent.

## Later user directions and approved decisions

- U01/U03/U04/U14: use official project-local BMAD openly in the repository; explain unfamiliar terms in simple English; retain development, test and process evidence. Reuse native BMAD records rather than duplicate logs.
- U05–U09: final project location is `/Users/saarreshef/job-hunt-assessments/powercenter-to-dbt`. Location changes are setup history, not converter functionality.
- U10–U13: start fresh from original materials after the agent added unrequested analysis and choices. Remove premature solution scaffolding; retain an honest short account of that setup mistake. The authoritative incident is `README.md#agent-error-caught-during-setup`, with cleanup commit `270a3d8`. Removed proposals do not become requirements.
- U16/U17/U19–U22: understand the assignment and tools before choosing implementation scope. Explain the PowerCenter export, schema versus data, dbt model/output execution, complete source-to-target paths, Jaffle Shop variants, DuckDB and independent expected-result tests. A general instruction to begin did not approve the agent's earlier specific scope proposal.
- U22: work 16:34–20:30 Europe/Sofia on 22 October 2026, including learning, planning, coordination, implementation, tests and documentation. Define a fully working tested minimum before bonuses; optional coverage must not displace the core. The exact core and revised remaining-time checkpoints are not yet approved.
- U23: consider the company ambition, reported by Saar, for conversion across products and versions. Research official export structures and semantic/version differences and preserve practical extension work. This is not a brief requirement or an approved promise to convert arbitrary XML. Eight layouts across fifty products was a hypothetical example, not a researched taxonomy.
- U23: use five to ten useful specialist subagents. Four concurrent agents including the coordinator is an operational limit, so use successive groups. Five preparation specialists are already recorded; this is not proof of implementation progress or guaranteed throughput.
- U23/U24: document the tools and Saar's personal Codex 20× access. Codex desktop and BMAD 6.12.4 are recorded. GPT5.6/high-thinking/fast settings are user-described context, not independently captured runtime metadata; the subscription label is not a model identifier.
- U25–U27: the SQL/Python discussion concerned the converter implementation, not a request for Python dbt model output. Saar caught and requested correction of the agent's incorrect interpretation. Preserve original prompts plus the correction; SQL output remains understood. Prefer one converter language unless another adds justified value.
- U28: approve Python 3.13, uv with locked isolated dependencies, ElementTree XML parsing, typed dataclasses/type hints, argparse CLI and explicit SQL emission; pytest, DuckDB and dbt-duckdb validation; CSV/Markdown reporting. Additional parser/emitter libraries require a demonstrated need. This does not approve exact supported operations, broader SQL dialect coverage or installation/test claims.

## User-added reporting and documentation obligations

U23 requests minimal, useful evidence segmented by actual test type, input, realistic condition, environment and stage; show strengths, weaknesses, unresolved issues and concrete next work with acceptance tests. No decorative dashboard or extra spreadsheet is required.

The native reporting companion concretizes this direction as planned `reports/test-runs.csv` and `reports/validation.md`. These filenames/schema are agent-developed contract details, not verbatim user choices. One row per real execution; retain rerun history. Planned fields: `run_id,utc,revision,stage,environment,case_id,test_type,input_id,target,status,detail,evidence`. Actual revision/input/environment and evidence must be identifiable. No mock passing rows or invented accuracy scores.

Keep test outcomes, complete-result checks and fixture-path support coverage separate with explicit denominators. Distinguish emitted, executable and independently verified paths; rejection can pass a negative test without adding support. Mark unsupported versus untested behavior. Show evidence → practical change → acceptance test for each material gap. Relevant result checks include values, columns, duplicate counts, nulls and numeric/date semantics. Reference comparison requires matched inputs/rules. The report design proposes mutation, negative, deterministic-generation and local dbt execution checks; selected operator-specific cases depend on agreed core scope.

`AGENTS.md` requires continuous actual-prompt capture with authorship and available dates; native requirement/implementation/review records remain authoritative. Record actual commands/results and genuine mistakes with detection/correction evidence. Do not invent completion, errors, missing prompts or unavailable dates. The curated prompt record states its omissions and is not a full export. Available tools lacked a file-export tool; that is not proof the desktop UI has no export feature. Exclude credentials, private submission details, unrelated context and wrong-chat content; identify relevant redactions. Keep the README concise and link evidence.

## Remaining boundaries for PRD review

1. Exact complete mapping paths/operations and minimum-versus-bonus coverage remain unresolved. A01's source/expression/join/aggregation proposal was not approved by U28's stack approval.
2. DuckDB is selected for local validation; broader target SQL dialect support is unresolved. Product/version compatibility requires representative evidence, not XML filename or similar tags. A shared representation and source-specific adapters remain a design consideration, not an approved architecture.
3. Supplied XML and classic DuckDB reference use related but different Jaffle Shop variants. A complete path needs matched data/rules or independently specified expected results; mismatch is not itself a converter defect.
4. Current records contain requirements and preparation checks only: no product code, converter tests, measured accuracy, Build execution or submission. The current SPEC explicitly says it is not implementation-ready. The new consolidation request is preparation for user review/approval, not permission to infer approval of unresolved scope.
5. No UI, cloud service, live PowerCenter integration, continuous synchronization or universal multi-product converter is required or approved. Future work should be concise, practical and tested rather than silently added to the core.

## Draft reconciliation

Compared `prd.md` and `addendum.md` with the sources listed above after both draft files were written. This checks preservation of inputs, not implementation correctness or approval.

**Preserved:** the exercise's XML-derived conversion, no hard-coded Jaffle Shop output, reasonable four-hour subset, tests, explainable code and all six submission/README obligations; external 23 October deadline versus internal 16:34–20:30 Sofia time box; core before bonuses; source integrity; open BMAD; actual prompts/error/process evidence and transcript/privacy limits; U28's entire approved Python/uv/ElementTree/dataclass/argparse/emitter/pytest/DuckDB/dbt-duckdb/CSV/Markdown stack; corrected U25–U27 interpretation; measured reporting with separate denominators and practical acceptance-tested next work; product/version and Jaffle Shop boundaries. The draft labels the five targets, initial dialect, semantic assumptions and checkpoints as unapproved proposals. No current implementation, measurements or universal coverage are claimed. No direct conflict with approved inputs was found in those areas.

**Necessary source-preservation follow-ups:**

1. PRD §8 says useful specialist agents in successive groups but drops U23's explicit five-to-ten range. Restore the requested range, keeping the four-active-agent limit and distinguishing the five already-recorded preparation specialists from future implementation assignments. Existing linked SPEC evidence preserves the count, but the full review document should carry this working constraint directly.
2. Saar's latest confirmation that there are no additional company instructions is not explicit in either draft. Record that confirmation and its provenance alongside the source list/prompt record; do not present it as a new recruiter statement or invent missing wording. The new request is one full PRD for review/approval before continuation; the drafts correctly gate continuation, and the addendum must remain a supporting sidecar rather than a separate approval scope.

The proposed five-path core, dialect/order assumptions, semantic evidence gates, revised checkpoints and unresolved reviewer handles remain visible for review. Their presence as open proposals is intentional, not missing source extraction.

## Later correction — U43

The fixed 20:30 stop described in this earlier review is superseded. Saar clarified that the goal is about four hours of total effort, with 20:30 as a flexible target; 20:40 is acceptable, and work in progress can be finished when needed. Current wording is in PRD §§5, 9, 10 and 12. Earlier checkpoint proposals still require rebaselining.
