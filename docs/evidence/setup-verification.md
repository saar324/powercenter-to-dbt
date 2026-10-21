# Setup verification

Date: 21 October 2026. These checks verify repository preparation and tooling. They do not establish converter correctness.

| Check | Actual result |
| --- | --- |
| BMAD installer | Core and BMM 6.12.4 installed successfully; Codex integration contains 29 skills. |
| Dependency reproducibility | `npm install --ignore-scripts` and `uv sync --locked --all-groups` completed. Both lockfiles are committed. |
| BMAD config resolver | Both the official `uv run _bmad/scripts/resolve_config.py --project-root ...` invocation and the corrected locked-project Python invocation completed. Project name and the Saar user-name override were checked. |
| BMAD Build instruction renderer | Rendered a local workflow snapshot; verified each output hash against its manifest and checked that workflow placeholders were resolved. This did not execute Build. |
| Supplied file integrity | XML and upstream README SHA-256 values match `fixtures/powercenter/provenance.json`; files were copied unchanged. |
| XML inventory | Parsed successfully; three mappings and 16 target definitions confirmed. |
| Reference checkout | Local ignored checkout is at `20cc904370818ceab08cf19f8fd196e9e81def88`. |
| Python tools | Python 3.13.16, pytest 9.1.1, and Ruff 0.17.1 are available. |
| dbt tools | dbt Core 1.12.6 and DuckDB adapter 1.11.0 are available. |
| DuckDB execution | A local in-memory decimal arithmetic query completed with the expected value. This is an environment smoke check only. |
| Ruff | `uv run --locked --all-groups ruff check .` completed. There is no converter source yet; vendor workflow files are excluded. |
| CI configuration | Workflow YAML parsed; push and pull-request triggers, locked dependencies, and explicit no-product-tests notice confirmed. Actual remote run results are recorded by GitHub Actions. |
| npm dependency audit | Initial install reported the csv-parse advisory. After a pinned 7.0.2 override, npm audit reported zero vulnerabilities. A clean BMAD install in ignored scratch space succeeded with the override. |
| Private-data check | Project files were checked for the local absolute workspace path, private submission identifier, personal email, and common credential prefixes. No matches were found outside ignored local files. |
| Ignore rules | Local environments, node_modules, work checkouts, and rendered BMAD snapshot caches are ignored. Plans and development evidence remain tracked. |

## Setup corrections

The initial locked uv helper invocation failed because uv selected script-lock mode. The corrected invocation uses `uv run --locked --all-groups python ...`. See `docs/agent/mistakes.md`.

The initial snapshot-check harness expected a bare output path. The renderer actually returns a `read and follow` instruction with a nested snapshot path. The harness was corrected and all snapshot hashes then verified. The renderer itself succeeded on its first run.

The installer's central configuration retained a default user name despite the CLI answer. A durable `_bmad/custom/config.toml` override was added and verified through the config resolver.

## Product checks still pending

- No converter has been implemented or executed.
- No product pytest suite exists or has passed.
- No dbt model has been generated, compiled, or compared against reference results.
- No BMAD specification, story, or retrospective has been completed.
- The assignment has not been submitted and no recruiter message has been sent.
