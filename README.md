# PowerCenter to dbt converter

Infinite Lambda Product Engineer take-home exercise.

**Status: repository and development environment prepared. Converter implementation has not started.**

The goal is to derive dbt SQL models from an Informatica PowerCenter XML export. The converter must use the XML's transformation logic; it must not hard-code Jaffle Shop SQL. The exercise asks for about four hours of work and a clear account of limitations and coding-agent use.

## Start here

1. Read [the assignment requirements](docs/assignment.md).
2. Read [the sample findings](docs/sample-findings.md), including the reference-project mismatch.
3. Read [the development process](docs/development-process.md).
4. Open this repository as the coding tool's project root. Read [AGENTS.md](AGENTS.md).
5. Start the BMAD specification workflow with [the prepared starting prompt](docs/agent/starting-prompt.md). That prompt has not been executed.

## Development setup

Requirements: Git, Node.js 20.12 or later, and [uv](https://docs.astral.sh/uv/getting-started/installation/). Python 3.13 is selected by `.python-version`; uv can install it.

```sh
npm ci --ignore-scripts
uv sync --locked --all-groups
```

BMAD **6.12.4** is already installed and committed under `.agents/skills/` and `_bmad/`. Node.js is used for BMAD tooling. The proposed converter language is Python. The lockfiles record the exact development dependencies.

To reinstall the pinned BMAD tooling, if necessary:

```sh
npm run setup:bmad
```

Reinstallation can regenerate vendor configuration. Review its diff. Preserve project overrides under `_bmad/custom/`. Do not migrate to the v7 preview during the exercise.

In a coding chat opened at this repository, invoke `bmad-help` for orientation or `bmad-spec` to start the specification. Use the skill prefix that the host tool supports. A chat opened above this repository may need to be reopened here before it discovers the local skills.

## Supplied files and references

- [Original sample XML](fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml).
- [Original upstream README](fixtures/powercenter/UPSTREAM_README.md).
- [Source URLs, commits, and checksums](fixtures/powercenter/provenance.json).
- [Machine-readable XML inventory](docs/evidence/sample-inventory.json).
- [Reference project instructions](references/README.md).

The linked DuckDB Jaffle Shop project has different input tables from this XML. It is a reference, not a complete expected-output oracle.

## Verification

The environment includes pytest, Ruff, dbt Core, and the DuckDB adapter. Local dbt use is configured to disable anonymous usage statistics. No warehouse credentials are required.

No converter command, supported-transformation list, or passing product tests exist yet. Add the runnable command and verification instructions when implementation begins. Do not treat an empty test suite as a passing gate.

## Development record and submission

- [User prompt log](docs/agent/prompts.md), starting with the initial request.
- [Work log](docs/agent/work-log.md).
- [Agent mistakes and corrections](docs/agent/mistakes.md).
- [Open decisions](docs/open-decisions.md).
- BMAD plans, specifications, reviews, and retrospectives will be kept in `_bmad-output/`.

Before submission, this README must state the actual run command, assumptions, exclusions, likely incorrect-output cases, an observed agent error and its detection, the prompts used, and the actual development process. The repository is prepared for that evidence; it does not claim those steps are complete.

Third-party material is identified in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Recruiter correspondence, private submission links, credentials, and unrelated personal context are excluded.
