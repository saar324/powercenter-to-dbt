# Original employer requirements reconciliation

Read-only audit of `docs/assignment.md` (original exercise plus preserved recruiter excerpt) against the current `prd.md` and `addendum.md`, 22 October 2026. This assesses requirement preservation in a draft design, not implementation compliance, test success or submission readiness. No removed setup analysis was used.

## Obligation-by-obligation mapping

| Employer obligation or permission | Exact draft location | Design coverage and actual status |
|---|---|---|
| Build a small PowerCenter mapping XML to equivalent dbt model converter. | PRD §1; FR-1–FR-4; §4.1; SM-1 | Covered as design for a proposed bounded subset. Converter implementation and equivalence evidence are pending. |
| Use the supplied sample XML and work out what its mapping does. | PRD FR-1; §4.1; §13; addendum “Supplied export and integrity” and “Semantic acceptance detail” | Covered. Fresh source inspection is recorded; this is source understanding evidence, not completed conversion. Original bytes/hash are preserved. |
| Derive output from XML; do not hard-code Jaffle Shop output. | PRD §1; FR-3; FR-6; §8; SM-2 | Explicitly covered, including mutation cases and exact crossed connectors. Actual general conversion/mutation tests are pending. |
| Any implementation language is allowed. | PRD §10; addendum “Approved stack and considered alternatives” | No conflict. Python is a later user-approved choice, not an employer restriction. Setup approval does not prove installation or execution. |
| Include tests. | PRD FR-6; FR-7; SM-1–SM-3; addendum “Verification and report contract” | Covered and expanded into independent result, mutation, edge, negative and dbt execution checks. No converter tests have run. |
| Jaffle Shop may be run/read and used to check output. | PRD FR-6; §11; addendum “Reference boundaries and future work” | Preserved as an optional reference method. Matching inputs/rules are required for meaningful comparison. Neither running the entire reference nor reproducing every model is mandatory in the brief. No reference execution is claimed. |
| Handle what is reasonable in the time; reasoning matters more than full coverage. | PRD §0–§1; §4; §5; §8; SM-C2 | Explicitly covered. Five-target core and bonuses are agent proposals, not an invented employer full-coverage requirement. The proposed scope still needs approval and feasibility review. |
| Approximately four hours; do not over-invest. | PRD §5; §10; SM-C2 | Covered by the stricter later user time box, 16:34–20:30 Sofia inclusive of learning/review/build/test/docs. Passed checkpoint is explicitly marked historical. Rebaseline remains pending; no time extension is silently assumed. |
| Expect coding-agent use and show how it is used. | PRD FR-9; addendum “Process evidence and privacy” | Covered. Agent-assisted preparation is documented; agent-assisted solution implementation has not begun. |
| If no coding-tool access, tell the company; access/refund may be available. | PRD FR-9; addendum tools/access record | Conditional offer, not a new product requirement. Saar reports tool access, so this condition is not active. No contact action is needed or authorized. |
| Submit GitHub repository, public or private with reviewer access, OR zipped folder. | PRD FR-8; §6 item 5; §8; §13 adopting assignment | Covered through the adopted assignment and reviewer/zip references, but a final handoff checklist should restate the alternatives explicitly. Actual reviewer handles remain a placeholder. No publication, access grant or submission has occurred. |
| README: how to run it. | PRD FR-8; SM-3 | Explicit design coverage. Actual converter commands and clean-checkout proof are pending. Setup commands alone do not satisfy this item. |
| README: assumptions and deliberately unsupported cases. | PRD FR-8; §4; §8; §12; FR-5/FR-7 | Explicit coverage. Final README must reflect approved and implemented behavior rather than draft claims. |
| README: where wrong output is most likely. | PRD FR-8; §11; FR-7; addendum semantic detail/report | Explicit coverage. Source risks and possible boundaries are recorded; actual converter failure evidence remains pending. |
| README: genuine coding-agent mistake and how candidate caught it. | PRD FR-8/FR-9; addendum “Process evidence and privacy” | Covered. Real setup scope error already exists in README; U25–U27 misunderstanding has detection/correction evidence. No invented implementation defect is required. |
| Prompts from initial prompt onward; if supported, ALSO include full agent conversation export as a repository file. | PRD FR-8/FR-9; addendum “Process evidence and privacy” | Covered in the addendum. Curated exact available prompts exist; missing history/export limitations are disclosed. Main FR-8’s “prompts ... or a full export” wording should be clarified to match the original conditional addition. Export availability is not fully established. |
| README: short outline of process followed with agent. | PRD FR-8/FR-9; addendum process evidence | Explicit coverage; current process is preparation only. Final account must describe actual implementation and checks once they occur. |
| Understand and explain any submitted code. | PRD §1–§2; FR-8; SM-3 | Covered through explainability and column/XML/code tracing. Actual understanding of product code cannot be confirmed before that code exists and Saar reviews it. |
| Sensible conversion and clear view of where it breaks. | PRD FR-3/FR-5/FR-6/FR-7; §11 | Covered. Unknown semantics are gated; unsupported and unverified conditions are distinct. Actual behavior remains pending. |
| Clear reasoning in a short README. | PRD FR-8; FR-7; §10 | Covered; supporting detail lives in linked records so it need not overload the README. Final readability/reproducibility review is pending. |
| External deadline: brief says one week; recruiter excerpt specifies 23 October 2026. | PRD §13; adopted `docs/assignment.md` | Specific recruiter date is preserved, without inventing a submission hour. The internal 20:30 stop is a separate user constraint. Submission remains pending. |
| Submit by provided link or email; notify recruiter after submission. | PRD FR-8; §8; §13 adopting assignment | Source is preserved, but a later submission checklist should explicitly carry the route options and post-submission notification. Current preparation correctly prohibits sending/submitting without authorization; this is a later obligation, not permission to act now. |
| Contact Chau for questions. | PRD §13 adopting assignment | Informational contact route remains in the source. No mandatory question or current external message is implied. |

## Additions and their authority

**Later user additions:** open BMAD development evidence; understand terms before scope/implementation; approved Python stack; complete tested core before bonuses; inclusive fixed working time box; five-to-ten relevant specialist agents; minimal measured CSV/reporting; strengths/weaknesses and practical acceptance-tested next work; product/version extension research; continuous prompt/decision capture; tools/access documentation. These supplement the exercise rather than replace XML conversion, tests or handoff evidence.

**Agent-developed proposals and practices:** the exact five-target core/bonus order, DuckDB output-dialect assumption, query-only pre/post-SQL boundary, unordered-result comparison, checkpoint snapshot, detailed CSV schema, independent mutation/edge case matrix and graph/component organization. PRD labels scope/semantic assumptions as proposed and requires owner review. Mature-tool research does not require adding Calcite, SQLGlot, a server, a full optimizer, universal adapters or a runtime scheduler.

**Mandatory versus optional:** tests and XML-derived conversion are mandatory; Jaffle Shop comparison is optional. Reasonable explicit exclusions are allowed; all sixteen targets, arbitrary XML and every PowerCenter operation are not required. A full conversation export is conditional on support, whereas preserving prompts is required. Public repository, accessible private repository and zip are alternative submission forms. The added reports/BMAD process do not excuse any of the six README requirements.

## Verdict and necessary clarifications

No material employer conversion/test/explainability requirement is omitted from the draft design. Actual delivery compliance is pending, not achieved. The design must still be approved and executed within a feasible subset/time box.

Two handoff clarifications remain:

1. Main FR-8 should say preserve prompts and include a full conversation export if supported, matching the addendum; avoid wording that can make these seem competing choices.
2. Carry a concise later submission checklist with public/private-with-access/zip alternatives, supplied-link/email routes, unresolved reviewer handles, external deadline and notification after submission. Do not interpret that checklist as authorization to publish, grant access, submit or send now.

Source compatibility, query-only runtime exclusions and bounded semantic assumptions still require explicit approval/evidence. They are permissible scope proposals under the reasonable-coverage instruction, not employer-approved guarantees of equivalence.

## Later correction — U43

The fixed 20:30 stop described in this earlier review is superseded. Saar clarified that the goal is about four hours of total effort, with 20:30 as a flexible target; 20:40 is acceptable, and work in progress can be finished when needed. Current wording is in PRD §§5, 9, 10 and 12. Earlier checkpoint proposals still require rebaselining.
