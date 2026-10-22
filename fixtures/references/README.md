# Pinned reference snapshots and harness

`provenance.json` records source repositories, full revisions, per-file SHA-256 and license status. `tests/reference_support.py::verify_pins` checks every retained byte before execution. No model SQL, macro or original seed has been edited. The original PowerCenter fixture remains separate and unchanged.

- **Classic:** `dbt-labs/jaffle_shop_duckdb@8d715f309a837287cc427f76157688e558bbbcae`, the assignment-linked project before the XML timestamp. All upstream models, model metadata, original three seeds, project/profile configuration, README, requirements and Apache-2.0 LICENSE are retained. The original-seed baseline runs its original `dbt_project.yml`, `dbt seed`, and every SQL model with a local profile. It uses this repository's locked runtime, not the old upstream requirements lock.
- **Modern:** `dbt-labs/jaffle-shop@f8f89f8d8af66ce3dd20844d41836cd5deac3f1c`, the historical candidate identified in [the correlation research](../../research/07-reference-version-correlation.md). Retained unchanged SQL comprises staging customers/orders/products/supplies/order_items and marts customers/orders/order_items, the source YAML and cents macro. The original project/package YAML and README are retained as provenance. There is **no LICENSE file at this revision**; no license grant is asserted. No publication is part of this work.
- **dbt_utils:** upstream `1.1.1`, full commit `74a661ca00452da7d2b2811ff1e5a37f152c3ee2`. Only the unchanged project YAML, Apache-2.0 LICENSE and surrogate-key macro required by modern supplies are retained. This bounded local package is resolved with `dbt deps`; it needs no remote package fetch. It is not a run of the whole dbt_utils project/test suite.

## Runtime configuration and source inputs

The modern run is a **bounded eight-model dbt harness**, not a full upstream-project run. It replaces project/profile/package configuration in a temporary copy, uses schema `modern`, and replaces the unused upstream package list (including mutable audit-helper main) with the bounded local dbt_utils package. The eight retained SQL files run unchanged, including the original orders/order_items logic. Other marts, MetricFlow, project tests, dbt_date/audit-helper and cloud configuration are outside scope. The source YAML and cents/surrogate macros remain unchanged.

Both reference families run beside the generated five-model project in the same temporary DuckDB database. Generated outputs use schema `converted`; raw inputs use `RAW`; classic outputs/seeds use `classic`. Profiles use one local thread and disable telemetry. Manifests, run_results, console output, canonical input manifests/hashes for both sides, comparison queries, physical schemas/types and both complete/projected result rows are retained under `reports/evidence/` and linked from `reports/test-runs.csv`.

Three controlled inputs are shared with generated models:

| Dataset | Data and adaptation |
|---|---|
| `ordinary` | Two customers/orders, one product/supply, and one supplemental raw item. Clean nonempty strings, lowercase product type, Y perishable, current-century dates and whole cents. Values are declared in `_load_inputs`; reference money/flag rules are not substituted. |
| `empty` | Typed raw tables with zero rows, including raw items. dbt still runs and schema checks still apply. A missing execution/schema is never an empty match. |
| `edge` | Exact synthetic rows from `examples/load_demo.py`: null/empty/space strings and keys, duplicate/unmatched keys, negative/null/fractional amounts, mixed-case/padded product types, Y/1/y/null flags and 1998/2000/2024/2025 dates. Supplemental raw items are empty. The 1998 date exposes XML YY century behavior. All mismatch rows remain in comparisons. |

Modern reads the exact `RAW` customer/order/product/supply rows consumed by generated models. Raw numeric/date types use the declared loader schema (DOUBLE, DECIMAL(12,2), TIMESTAMP), not automatic modern seed inference. Supplemental `RAW_ITEMS` exists only to execute the upstream orders dependency closure; selected customer summary fields originate in staging orders, and upstream left joins remain intact. Stores and locations are not dependencies of these eight models.

For the classic synthetic runs, raw ID/customer/date fields are copied to classic seed inputs. After `dbt seed` creates typed tables and before unchanged model SQL runs, a source-only `INSERT SELECT` bridge restores the exact typed RAW values into classic customer/order seed tables. This is necessary because Python CSV serialization alone collapses NULL and empty strings. Both values now remain distinct in classic inputs and reference staging, including the empty-ID/empty-name edge row. The original-seed baseline never receives this restoration. The full XML NAME occupies classic `first_name`; `last_name` and status are NULL. Explicit local seed column types preserve null IDs and allow typed empty seeds. Payments are empty because the XML inputs do not establish an equivalent payment stream. Product/supply comparisons remain non-comparable. These generated temporary seed/configuration files do not alter the pinned original files.

A separate `original-seeds` baseline uses the unchanged original classic seeds. Its generated-input bridge casts numeric IDs to VARCHAR, joins first and last names with one space, casts order dates to TIMESTAMP and leaves absent XML location/amount inputs NULL; product/supply inputs are empty. Original classic payment rows remain untouched and are not mapped to invented XML amounts. Only the explicitly shared fields are compared as projections.

## Comparison rules

Every existing counterpart has a `complete` check: all columns in order, physical DuckDB types, values and duplicate multiplicity. SQL identifier case is folded for name comparison; other names/order/types are preserved. Full outputs can differ even when a selected field subset matches.

`projection-normalized-values` selects the exact columns and aliases in `MODERN_PROJECTIONS`/`CLASSIC_PROJECTIONS`, without filtering rows, swapping money columns or changing joins/formulas. It bridges the documented date/count names, casts classic identifiers to VARCHAR and casts modern/generated food/drink flags to INTEGER for that projection. Numeric Python representations compare as exact Decimal keys, without context-based rounding; signed zeros compare numerically equal; DATE/TIMESTAMP representations compare at day level because the source date rule is day-based. The original projected physical types and `physical_types_equal` remain in evidence, so normalized agreement does not claim physical equality. Supply perishable text is not converted to Y/N or boolean: its actual difference stays visible.

The derived CSV groups by run, reference/pin, code revision, dataset, aspect, scope, environment and explicit `effect_scope`. All these measures describe **end-to-end combined effects**, not isolated operator accuracy. In particular, customer aggregation includes upstream money wiring and join/storage behavior; join projections also include upstream values. `aspect_note` preserves this interpretation in evidence and the CSV. Unequal outputs are labelled `observed_unresolved_reference_difference`; static rule evidence is retained as a candidate explanation, not automatically certified as the cause. Case agreement is `matched/(matched+different+error)`; unsupported/non-comparable counts are outside that denominator. Row overlap uses Counters, divided by each case's maximum row count and summed within a group. Execution errors have no row rate. Both-empty case rates are 100% only after successful schema checks; aggregate zero row denominators have blank rates. Overlapping aspects/scopes are never combined into an overall accuracy percentage.

Run from the project root:

```sh
uv run pytest -q tests/test_reference_results.py tests/test_reference_reporting.py
uv run python scripts/summarize_accuracy.py
# To reproduce a particular run's aggregate:
uv run python scripts/summarize_accuracy.py --run-id RUN_ID
```

The default aggregate selects the latest **successful complete 88-case reference matrix**, including a passed original-classic baseline and invocation. Later unrelated, partial or failed runs do not displace it. Every selected comparison/baseline JSON must match its history context and measured details; output counts/rates and successful input-manifest hashes are checked before atomic output replacement. Missing or contradictory evidence rejects the export and preserves the previous CSV. Older pre-review JSON without history context cannot be re-exported as newly validated evidence; its original CSV/history remains historical.

An explicit `--run-id` may select a partial/failed run, with `run_completeness`, `expected_cases`, `actual_cases`, `missing_cases`, `invocation_status`, `baseline_status` and `lifecycle_errors` visible in every output group. Measurement and pytest lifecycle outcome remain separate: a failed teardown writes a distinct lifecycle-error JSON/history row and never duplicates or overwrites the comparison. Setup failures retain reference/pin/dataset metadata, including the original baseline.

Input identity hashes both sides' actual consumed source tables, ordered columns, physical types and canonical duplicate-preserving rows. Row display order does not change identity; duplicate count, schema or classic payment changes do. The retained input manifest records adaptations and is linked from every measured comparison. The full suite also runs all these checks.
