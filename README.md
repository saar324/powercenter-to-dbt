# PowerCenter to dbt

A deterministic Python CLI converts supported PowerCenter XML paths into a runnable DuckDB dbt project. It derives expressions, joins, aggregates, types, target column order and wiring from the XML. It inventories all 16 targets in the supplied export and keeps complete independent outputs when other targets fail.

The five required paths have actual dbt execution and independent complete-result checks. [Measured validation](reports/validation.md) separates test outcomes, result comparisons and fixture coverage. This is a bounded converter; there is no executed PowerCenter oracle or universal equivalence claim.

## Run it

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run from the repository root. `uv` restores the locked Python 3.13 environment.

```sh
uv sync --locked
uv run pytest -q
uv run pwc-to-dbt --help
```

Convert the five required targets into a fresh destination:

```sh
uv run pwc-to-dbt fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml \
  --bindings examples/sample-bindings.json \
  --output .generated/demo \
  --target REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/m_FL_JS_STAGING_FULL/STG_CUSTOMERS \
  --target REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/m_FL_JS_STAGING_FULL/STG_ORDERS \
  --target REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/m_FL_JS_STAGING_FULL/STG_PRODUCTS \
  --target REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/m_FL_JS_STAGING_FULL/STG_SUPPLIES \
  --target REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/m_FL_JS_MARTS_CORE/CUSTOMERS
uv run python examples/load_demo.py .generated/demo/converter.duckdb
PWC_DUCKDB_PATH="$PWD/.generated/demo/converter.duckdb" \
  uv run dbt run --project-dir .generated/demo --profiles-dir .generated/demo
```

The loader creates synthetic data, including duplicate, null, unmatched and numeric/date boundary rows. It refuses to replace an existing database. Use a different fresh directory to repeat the conversion; the CLI also refuses nonempty destinations. Run the last dbt command again to exercise existing-table cleanup. `uv run pytest -q` performs the independent comparisons and stale-row lifecycle checks automatically.

Use `--inventory` to list exact target identities. Repeat `--target` to select outputs; bound producers are included automatically. Omit `--target` to attempt all targets. Unsupported/blocked paths produce exit 1 and remain visible in `conversion-manifest.json`; fatal input/configuration errors produce exit 2. Emission is not result verification.

`examples/sample-bindings.json` explicitly connects exact source instances to generated targets. It also declares original target schemas absent from target definitions, checked against the cleanup relation. These declarations are example configuration, not relation-name inference. Unbound inputs become declared dbt sources and must be supplied separately.

## Assumptions and omissions

- Supported relational steps are single-stream Source Qualifiers with empty overrides, pure Expressions, ordinary equality/boolean Joiner conditions for normal and master-outer joins, grouped Aggregators, and Sorters. Supported expression functions and arities are explicit in `expressions.py`. Stateful local variables, Routers, Custom Transformations, arbitrary SQL and session overrides are rejected on affected paths.
- The bounded storage policy handles Oracle strings and exported numeric metadata: empty strings become null at source/target storage boundaries; intermediate empty strings remain distinct. Bare `NUMBER` and `double` use double precision under the export's recorded high-precision-NO sessions. Declared decimal precision/scale are rounded then cast at separate boundaries. Tests verify the declared policy, not every Oracle/PowerCenter rounding mode.
- YY dates resolve in the DuckDB runtime's current century, with midnight for this format. Tests also inject century contexts, including invalid leap days and the reached NULL error default. No production year is fixed in the converter.
- ASCII string comparisons/case conversion and the tested null/sort rules are verified. Other code pages, non-ASCII collation, time zones, large numeric accumulation, and source-runtime row rejection/recovery are unverified. ERROR-default failures stop the query; they do not reproduce PowerCenter bad-row files.
- Only target-bound `TRUNCATE TABLE` preparation with an explicitly resolved original relation is translated. The writer generates guarded `delete from {{ this }}` hooks for table models. Conversion never opens a database or executes imported SQL. Workflow commands remain reported as unconverted. XML entities/internal DTD subsets and imported dbt template delimiters are rejected; external DTDs are not fetched.

The XML crosses both product-price and order cents/dollars target connectors. The converter preserves those connections. The master-outer customer join preserves grouped-order detail rows, including unmatched groups with null master customer fields; it does not add idle customers. These differences make a conventional Jaffle Shop model an unsuitable oracle without matched rules and inputs.

## Where wrong output is most likely

The main risks are untested source-runtime behavior at binary-floating rounding boundaries, non-ASCII/collation rules, session/runtime options absent from the tested subset, and row-error recovery. Related Informatica documentation supports the chosen bounded rules; the export does not establish a PowerCenter product-release compatibility range. [Source compatibility](./_bmad-output/specs/spec-powercenter-to-dbt/source-compatibility.md), [semantic research](research/06-core-semantics-check.md) and [validation/next work](reports/validation.md) explain evidence limits and concrete follow-up tests. Unsupported paths are not silently approximated.

## Agent errors and detection

Actual dbt execution caught an invalid first implementation of error defaults: DuckDB rejects TRY around volatile `error()` calls. Boundary tests then caught a decimal cast that rejected a representable value before rounding. An independent audit caught projection of an unused, unvalidated bound-source field and a double-default guard that let an error escape TRY. The [native implementation record](./_bmad-output/implementation-artifacts/spec-powercenter-basic-conversion.md#implementation-notes) records detection and corrections; regression tests cover them. Earlier failed runs remain in [the CSV](reports/test-runs.csv).

### Agent error caught during setup

During setup, the coding agent added analysis and proposed implementation choices when I had asked only for repository preparation. I caught this by reviewing the repository files and questioning what had already been added. I asked the agent to remove those additions and the converter-specific scaffolding, keeping the supplied materials and BMAD setup. The cleanup is recorded in commit `270a3d8`. This occurred before converter implementation.

## Prompts and actual process

The [available actual prompt record](docs/agent-prompts.md) starts with the initial prompt and distinguishes user and delegated-agent wording. It states missing history and redactions. A supported full conversation export was not available through the tools used; this curated record is not presented as a full export. Confidential third-party context, personal contact details and the private submission URL are excluded.

Saar used his personal Codex 20× plan with GPT Sol 6.1, high thinking and fast execution, as he reported. The prompt log records these settings; runtime model metadata was not available.

The work used Codex desktop and project-local BMAD Method 6.12.4: preserve the supplied material; research the XML and source semantics; reconcile and approve the native requirements and architecture; prepare and approve the distinct Build spec; implement the shared contracts and separate pipeline stages; execute dbt and independent tests; correct observed failures and audit findings; prepare this reproducible handoff. Actual native review status is retained in the Build record. No submission or employer message is performed by these commands.

Read the code in data-flow order: `mapping.py` → `xml_reader.py` → `dependencies.py` → `expressions.py`/`sql.py` → `project.py`; `cli.py` coordinates them. Tests own synthetic input and expected results independently of the converter.

- [Assignment](docs/assignment.md), [supplied XML](fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml), [provenance/hashes](fixtures/powercenter/provenance.json)
- [Canonical SPEC and companions](./_bmad-output/specs/spec-powercenter-to-dbt/SPEC.md), [architecture](./_bmad-output/planning-artifacts/architecture/architecture-powercenter-to-dbt-2026-10-22/ARCHITECTURE-SPINE.md), [Build implementation/review record](./_bmad-output/implementation-artifacts/spec-powercenter-basic-conversion.md)
- [Actual run CSV](reports/test-runs.csv), [validation summary](reports/validation.md), [CI](.github/workflows/tests.yml), [third-party notices](THIRD_PARTY_NOTICES.md)

The repository includes native BMAD/research/prompt evidence and dependency lockfiles. Installed dependencies, caches, credentials and generated local databases are excluded. `npm ci --ignore-scripts` restores the existing pinned BMAD installer dependencies if needed; it is separate from the Python converter environment. No model/settings claim is inferred from the user's subscription description.
