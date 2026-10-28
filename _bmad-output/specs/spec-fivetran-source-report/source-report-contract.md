# Source report contract

## Entry points and output

- Add `--source-report`. Without `--output`, print the whole-export JSON report to stdout without planning or generating SQL. It accepts the existing `--bindings` file. Reject `--inventory` combined with this option and reject `--target` in report-only mode rather than silently ignore selection.
- With `--output --source-report`, retain normal conversion and add `fivetran-source-report.json` to the atomic output set. Cover the whole export even when `--target` selects fewer outputs or selected transformations fail. Leave invocations without the new option unchanged.
- Use format version 1, input SHA-256, scope `whole_export`, catalogue identity/review date, source definitions, unresolved source uses and concise counts. Stable ordering and no run-time timestamps make identical inputs/configuration deterministic.
- Report-only exit 0 means the report was generated, including unresolved matches. Existing input/configuration errors return 2. Conversion retains exit 0/1/2 independently of report findings. A malformed export remains a fatal input error; no new recovery parser is in scope.

## Inventory and evidence

- Definition identity is the exact repository/folder/source-definition tuple. Do not merge by slug, schema/table, `DBDNAME` or connection name. Retain unused folder-level SOURCE definitions.
- Keep raw `NAME`, `DATABASETYPE`, `OWNERNAME` and `DBDNAME` separately. Missing values stay missing; do not use the emitter's `main` schema fallback in the report. A definition name is an exported table reference, not proof of the actual runtime relation under overrides.
- Each definition lists its exact mapping/source-instance uses. A repeated source is one definition with multiple uses; a missing definition reference is an unresolved use, not a fabricated complete definition.
- Retain reader connection references with repository, folder, workflow/session/task-instance, reader-instance and association provenance. Qualifier INSTANCE/ASSOCIATED_SOURCE_INSTANCE and source-reader SESSIONEXTENSION/DSQINSTNAME supply association evidence. Check identity/type and surface absent, inconsistent or ambiguous associations; retain unassigned evidence rather than silently attach it.
- Include workflow TASKINSTANCE session overrides as distinct contextual evidence. The fixture's reusable staging SESSION reader names `MART_Jaffleshop`; its workflow TASKINSTANCE reader override names `RAW_Jaffleshop`. Preserve both. Do not select an effective runtime connection or treat target WRITER references as source connections.
- Expose incomplete or differing declarations and explicit metadata diagnostics. Do not collect host credentials or attempt to resolve connection objects. The fixture contains no full CONNECTION definitions.

## Bindings and migration state

- Validate exact binding identities and configuration types using the existing configuration contract. Reuse a shared resolver if necessary without changing conversion behavior. Report generation must not require successful target-graph validation or compilation.
- Classify each source use as external/unbound, explicitly bound to a producer, or unresolved. Definition summary can be external, bound, mixed or unused. A STG name alone is not evidence of a binding.
- Keep producer identity and availability separate. Report-only execution says availability is not evaluated. Alongside conversion, record emitted, failed/blocked or unselected based on actual outcomes. A binding is not proof of field compatibility, successful conversion or data availability.
- Do not silently turn a failed bound producer into a new external ingestion requirement. No external extraction is required for a particular use only when its declared producer can supply it; unsuccessful or unchecked producer availability stays visible.

## Connector matching and limits

- Use a small offline catalogue of Oracle, PostgreSQL, MySQL and SQL Server, with source URLs and review date 2026-10-28. Exact trimmed, case-insensitive aliases are allowed; no substring or fuzzy matching. Retain original technology text.
- Official database catalogue: https://fivetran.com/docs/connectors/databases. Oracle evidence: https://fivetran.com/docs/connectors/databases/oracle/oracle-connector. PostgreSQL evidence: https://fivetran.com/docs/connectors/databases/postgresql. MySQL and SQL Server documentation are linked from the official database catalogue. This is a bounded catalogue, not an exhaustive unsupported-source list.
- Recognized means `available`, unrecognized means `no_known_match`, absent means `unknown`; conflicting source type and associated connection subtype require review. Preserve conflicting evidence rather than silently replace the source type.
- Connector matches identify candidate technology only. Client compatibility and existing Fivetran configuration remain `not_verified`. Further checks include database version/service, object types, permissions, networking, replication settings, plan and destination support. Oracle's documented connector supports tables/materialized views and excludes regular views; the export does not verify those conditions for a client.
- Do not count physical connections from definitions, schemas or exported names. Do not certify migration readiness or connector compatibility from a catalogue lookup.

## MVP verification

- Supplied XML: 12 definitions, 28 uses, Oracle candidate matches; repeated uses and failed/unselected paths remain visible.
- Controlled XML/configuration: unused definitions; mixed binding states; unknown or missing technology; inconsistent connection evidence and unresolved associations. Explicit bindings alone change input classification.
- Real CLI: report-only stdout and opt-in conversion artifact; deterministic output; existing output protection and exit behavior. Confirm old conversion output remains unchanged without the flag.
- Run focused report tests, existing CLI/graph tests and the existing independent result checks needed for affected conversion boundaries. Keep existing reference evidence separate; do not claim a reference rerun unless executed. Reuse `reports/test-runs.csv`, `reports/validation.md` and native Build verification notes.
