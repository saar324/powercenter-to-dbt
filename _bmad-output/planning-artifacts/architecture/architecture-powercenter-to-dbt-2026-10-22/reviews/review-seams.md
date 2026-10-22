# Architecture seam review

Adversarial review of the current `ARCHITECTURE-SPINE.md`. No source changes, implementation or new research. Exact Python shapes/signatures are already reserved for one central native Build contract; their absence is not a finding. This review asks whether the current component responsibilities still permit incompatible independently reasonable implementations before that contract is fixed.

## S1 — Relation/artifact identity and preparation lifecycle need one owner

**Affected decisions:** AD-2–AD-4 and AD-7; shared identities and ownership conventions.

**Concrete pair:** SQL-generator unit derives a collision-checked deterministic model identity from the exact mapping/target key and writes `ref()` calls using it. It translates target cleanup into a preparation artifact keyed to the same target. Project-writer unit also uses exact target identity but independently chooses deterministic filenames/model names, schema aliases and table/view materialization while generating project configuration. Each unit respects its local ownership (SQL rules versus files/configuration), exact XML lineage, quoted identifiers and collision rejection. The shared artifact shape can hold both an identity and SQL without specifying which unit owns their resolved database/dbt meaning. Both units compile against that shape, yet the generated `ref()` names can differ from actual dbt model names; preparation can also target a name or relation lifecycle that the writer does not create.

**Why existing rules do not settle it:** deterministic naming does not imply identical naming between components. Physical source metadata is distinguished from XML identity, but no shared owner is named for the generated model identifier, file path, relation/schema alias and materialization/preparation lifecycle. AD-7 demands integrated lifecycle verification, which will detect the disagreement later, but it does not provide a composable upstream contract. A broad runnable-output requirement alone does not choose the producer of these facts.

**Closure needed:** designate one authoritative per-target output/relation plan, resolved before SQL, preparation and project configuration are finalized. Its owner assigns dbt model identity and physical relation/lifecycle policy; SQL, bindings/ref/source rendering, setup steps, writer paths/configuration and inventory consume that plan rather than independently derive names or materialization. Keep preparation as a structured intent until the generated relation/lifecycle is resolved. Central Build defines the exact fields and rendering split; no function signatures or new user approval ceremony are requested here.

**Acceptance at the seam:** one producer/consumer binding with differing XML instance and definition names, a quoted/collision-sensitive generated name, and supported cleanup yields a single consistent model/ref/config/inventory relation. First and repeated dbt runs use the resolved lifecycle, including a target absent on the first run. The test must exercise the assembled generator and writer, not separately chosen expected names.

## S2 — Cross-mapping binding validates object identity but not field compatibility

**Affected decisions:** AD-1 and AD-4; exact identity and checked-plan boundary.

**Concrete pair:** Planner unit validates an explicit source-instance → target-instance binding, resolves the referenced target and recursively includes its producer closure. All referenced object keys exist and are unambiguous. SQL-generator unit preserves the consumer Source Qualifier's exact source-field names and the producer's XML target-column order. If that producer exposes `CUSTOMER_ID` while the bound source expects `ID`, a model-level `ref()` is valid but the consumer references an absent column. A second otherwise plausible generator can use ordinal correspondence instead, producing executable but wrong lineage when columns are reordered. Both variants obey the current stated table-binding format and local connector rules; none of the rules specifies how field compatibility is checked across the new binding edge.

**Why existing rules do not settle it:** field identity is precise inside mappings, but a configuration-created cross-mapping edge has no XML connector defining its column correspondence. Unknown/ambiguous/conflicting binding validation can reasonably be implemented as object-key validation only. Sharing Python dataclasses does not decide whether compatibility is by exact columns, ordinal positions, renaming configuration or coercion.

**Closure needed:** make the planner's checked-boundary contract include schema compatibility for every generated-producer binding. Establish an explicit supported correspondence policy and reject missing/ambiguous/incompatible fields before emission; do not infer correspondence from position or similar names. The smallest scope is exact required source-field → producer-output matching with explicit supported type compatibility, rejecting other bindings. If renaming mappings are later supported, they must be explicit rather than silently assumed. Central Build fixes the precise policy and representation before independent coding.

**Acceptance at the seam:** valid matching schemas retain lineage; a renamed required column, reordered columns and incompatible type each either produce the explicitly declared supported correspondence or a contextual binding diagnostic. Producer existence alone must not count as a checked binding.

## Verdict

Two material composition seams remain: authoritative generated-relation/lifecycle ownership and field compatibility across configured bindings. The existing separation, immutable parsed mapping data, failed-producer closure, independent expected results and centralized future Python-interface authority otherwise constrain the tested attack surface. This review does not demand complete implementation interfaces in the feature-level spine. Close these ownership/validation decisions, then recheck the affected seams before claiming the architecture reviewer gate passes.

## Targeted recheck disposition

Re-read revised AD-4 and AD-7 only against S1/S2. Both findings are **closed at the architecture-contract level**:

- **S1 closed:** planner solely owns the canonical per-target ModelPlan, including target identity, unique dbt model name, alias/schema options and exposed columns/types; downstream stages cannot derive competing names. Project writer solely owns materialization/configuration and preparation-hook rendering; SQL emitter owns SELECT bodies. Setup classification produces typed target-key intents. Original command relations resolve through declared metadata, while generated cleanup uses dbt's resolved `this`. The earlier independent name/materialization reconstructions are now prohibited by the contract.
- **S2 closed:** each consumed bound input field must match an exposed producer column with compatible declared type; incompatible bindings fail rather than assume renames, ordinal correspondence or narrowing. The earlier object-only binding check cannot satisfy revised AD-4.

No remaining counterexample from these two attacks obeys the revised contracts. Exact shared Python shapes, supported type-compatibility rules and integrated dbt lifecycle tests remain centrally specified/verified during Build as already required. This targeted closure does not claim those interfaces exist, tests passed or implementation readiness is complete, and it is not a new broad architecture pass.
