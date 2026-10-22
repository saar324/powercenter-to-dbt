# Assignment scope review

22 October 2026. Independent review of `docs/assignment.md`, the current `prd.md` and `addendum.md`. Preparation only: the PRD remains unapproved; no converter implementation, tests or measured results are claimed.

**Verdict: aligned with the written exercise, subject to explicit acceptance of the proposed boundaries.** No requirement was found to support every target, retain Oracle as the output dialect, run PowerCenter, reproduce its workflow, or use the linked Jaffle Shop project as the only test oracle. The brief expressly allows reasonable incomplete coverage and says the reference *can* be used. The five-target subset is meaningful: it includes expressions, joins and aggregation rather than only renaming fields.

| Proposal | Assessment against the assignment |
|---|---|
| Five complete incoming target graphs | Permitted coverage limit. Count five of sixteen target paths, not three fully supported mappings or a universally supported transformation type. Selected graph completeness does not prove arbitrary input support. |
| DuckDB SQL/dbt-duckdb | Compatible with producing dbt models and using a local reference database. Still translate source semantics deliberately; a different output dialect is not permission to alter dates, nulls or precision. |
| Query-only boundary; no imported pre/post SQL or workflow execution | Reasonable explicitly declared omission for a model converter. The PRD's A5 correctly requires reporting the runtime commands and separates dbt materialization. Do not describe this as full PowerCenter workflow or runtime equivalence. |
| Independent controlled tests where the reference differs | Permitted and preferable to an invalid comparison. Show independent expected results and input mutations; do not claim a PowerCenter-runtime or full Jaffle Shop comparison that did not run. |
| Follow exact XML wiring, including crossed product-price ports | Required for deriving behaviour from the source. Silently correcting surprising wiring to match familiar Jaffle Shop SQL would defeat the conversion task. Report the discrepancy separately. |
| BMAD, research notes and CSV/Markdown reporting | User-requested additions, not original exercise requirements. They support transparent reasoning only while the runnable converter, tests, short README and Saar's understanding remain the priority. |

## Material risks and necessary handling

1. **Equivalence can be weakened by ambiguous labels.** Retain the explicit query-only boundary in README and final evidence. Use wording such as “selected mapping row transformations within the documented semantic/input boundary.” Excluding runtime effects is an omission to disclose, not proof they were reproduced. A target with unknown required row semantics remains unsupported/unverified, not a successfully converted path.

2. **Semantic gates remain unresolved.** Join preservation, two-digit-year evaluation, numeric conversion and null/default rules need evidence or a clearly accepted bounded input assumption before implementation/support claims. Approval of a five-name list alone does not resolve those rules. Do not make expected tests agree with a guessed implementation and call that equivalence.

3. **Preparation threatens the four-hour objective.** The PRD records that its 18:30 checkpoint has already passed, with the 20:30 stop unchanged. Rebaseline the remaining work before accepting its dated milestones; trim optional work first. No further framework/research expansion should displace core implementation and verification unless Saar explicitly changes that priority. If the five-target core cannot fit, seek a concrete scope/time decision rather than silently lowering correctness or omitting required README evidence.

No expansion to a universal converter, full sixteen-target coverage, an Oracle runtime or a mandatory unmatched-reference comparison is needed to repair alignment. The current PRD already records the main boundaries; the remaining decision is whether Saar accepts them and the remaining delivery scope/time.

## Later correction — U43

The fixed 20:30 stop described in this earlier review is superseded. Saar clarified that the goal is about four hours of total effort, with 20:30 as a flexible target; 20:40 is acceptable, and work in progress can be finished when needed. Current wording is in PRD §§5, 9, 10 and 12. Earlier checkpoint proposals still require rebaselining.
