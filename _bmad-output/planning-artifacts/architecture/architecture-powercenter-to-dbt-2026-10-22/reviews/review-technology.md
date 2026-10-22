# Architecture review — technology and evidence

## Verdict

Pass for the architecture technology/evidence lens. No material findings. The spine's committed boundaries have primary-document or inspected-fixture support; its listed tooling versions are present. Exact converter-test dependency compatibility remains explicitly deferred to the central Build lock/smoke check, without an installation or execution claim.

Findings by severity: critical 0; high 0; medium 0; low 0.

## Decision evidence

| Decisions | Evidence and limit |
|---|---|
| AD-1/AD-2: XML facts, checked graph and separate stages | Existing primary-source checks in architecture memory and research/02 cover Python ElementTree and graphlib. Source inspection establishes that XML tree containment and connector dependencies are different structures. Python shared objects and separated responsibilities do not require another framework or library. No graph/runtime test is claimed. |
| AD-3: target models, internal CTEs and typed lineage | Approved model granularity plus the inspected target/connector metadata support the choice. Existing dbt SQL-model/reference research demonstrates the output mechanism, not source-semantic equivalence. |
| AD-4: generated project, source declarations, local profile and explicit bindings | Official [dbt project documentation](https://docs.getdbt.com/reference/dbt_project.yml) confirms the required project file. The maintained [dbt-duckdb adapter](https://github.com/duckdb/dbt-duckdb) documents local file profiles and source/model operation. Cross-mapping binding is grounded in missing XML cross-mapping connectors and owner approval; recursive producer closure is a checked dependency rule, not an unsupported adapter feature claim. |
| AD-5: current-run artifacts, diagnostics and explicit partial outcomes | Ordinary filesystem/control-flow design, supported by inspected source identities and the approved failure contract. It introduces no unverified external service or specialized technology. Execution is deferred. |
| AD-6: bounded source semantics | Research/06 and its reconciliation preserve related-version/product evidence limits, high-precision metadata, port/target type conversion, output-default distinctions and dynamic evaluation-century behavior. The spine requires verification before support claims. |
| AD-7: preparation effects | Official [dbt pre/post-hook documentation](https://docs.getdbt.com/reference/resource-configs/pre-hook-post-hook) establishes supported before/after SQL mechanisms. This is technology-fit evidence, not proof that blind TRUNCATE hooks preserve first-run or repeated-run materialization behavior; those checks remain mandatory in the spine. |
| AD-8: actual execution and evidence | Existing primary dbt/DuckDB/pytest research supports controlled local execution and independent assertions. The architecture distinguishes generated artifacts, executed models and verified results; no measured accuracy is asserted. |

## Versions and deferred compatibility

Read-only checks during this gate confirmed `uv --version` reports 0.13.4; `uv python list --only-installed` lists CPython 3.13.16; `package-lock.json` records BMAD Method 6.12.4. These match the spine. Other installed Python releases were not mistaken for the chosen runtime.

No product starter is selected or used. The structural seed is expressly proposed code organization, and the scoped file inventory found no product source, test tree, pyproject or uv lockfile. Existing npm tooling remains BMAD setup, not a converter-language requirement.

Build must resolve and commit compatible pytest/dbt-duckdb/DuckDB dependencies in one environment, record the actual resolved versions and smoke-check real dbt execution before claiming compatibility. Mutable current documentation and the existence of a Python runtime do not establish that combination. This remaining gate is explicit, so it is not a technology finding against this draft architecture.

No dependency installation, starter generation, converter code, source-runtime execution or product tests were performed by this review. This pass does not establish implementation readiness or semantic equivalence.
