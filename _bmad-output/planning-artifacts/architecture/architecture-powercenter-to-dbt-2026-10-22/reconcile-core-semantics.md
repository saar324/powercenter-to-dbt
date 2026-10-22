# Core-semantics reconciliation

## Verdict

No material contradiction or unsupported runtime-equivalence claim found between `ARCHITECTURE-SPINE.md` and `research/06-core-semantics-check.md`. AD-6 explicitly incorporates the bounded research rules and requires verification before support claims. This is a source reconciliation, not a semantic test result or implementation-readiness verdict.

## Preserved boundaries

| Source condition | Architecture treatment |
|---|---|
| Master outer preserves detail/grouped orders, normal join matches equality rows; exact input/port identity matters | AD-1, AD-3 and AD-6 retain exact identities, connected values and master-outer roles, and incorporate the research rule. No customer-preserving rewrite is specified. |
| Pure reached three-argument IIF has null-condition false behavior; arbitrary branch/error evaluation is not proved | AD-6 requires structural parsing and bounded null-sensitive rules, contextual rejection and verification before support. No general IIF-equivalence promise is made. |
| Oracle storage normalization differs from intermediate PowerCenter empty strings | AD-6 explicitly preserves storage/intermediate distinctions. |
| Source, intermediate and target numeric metadata differ; output defaults handle errors rather than every null | AD-3 separates the three metadata layers; AD-6 preserves type/default metadata and incorporates double/decimal/target conversion rules. It does not prescribe a blanket null replacement or integer conversion of double scale 0. |
| Export sessions record high precision NO, without proving original runtime state | AD-6 says the setting is recorded as NO. It does not claim observed PowerCenter execution. |
| YY reconstructs the evaluation century; invalid-date/default interaction needs a declared rule | AD-6 incorporates the research's current-century and default boundaries, with controlled test context and no fixed production year. No generic `%y` pivot, source-century date cast or unconditional invalid-date normalization is specified. |
| Related-product joins, older-version function documentation and actual DuckDB casts have evidence limits | AD-6 requires verification before support; Stack expressly disclaims dependency/runtime compatibility execution. AD-8 separates generated SQL from independently checked results. |

## Required Build carry-forward

These are existing incorporated conditions, not added architecture scope:

- Preserve unmatched detail metrics with null master customer fields; do not coalesce the detail identifier into the connected master output. Verify duplicate and null-key behavior.
- Implement declared source/port/target conversion boundaries, including the decimal cents scale and crossed-price target scale. Check rounding and overflow; `double(15,0)` is not an integer.
- Treat output `0`, `NULL` and `ERROR(...)` defaults as distinct error policies; do not replace ordinary null inputs merely because the output error default is zero. Whole-query failure is not per-row rejection equivalence.
- Verify runtime-century, null, midnight and invalid reconstructed leap-day behavior using controlled test context. Guarded NULL fallback remains bounded to the reached NULL-default policy, not arbitrary ERROR-default ports.
- Retain character/collation and documentation-version limits in verification/reporting; finite independent examples do not establish full source-runtime equivalence.

No additional research, package installation, converter implementation or test execution was performed for this reconciliation.
