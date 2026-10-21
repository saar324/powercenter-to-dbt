# Assignment requirements

This is a requirements summary of the supplied take-home brief. It is not a copy of recruiter correspondence and is not yet a BMAD specification.

## Objective

Build a small tool that reads an Informatica PowerCenter mapping XML file and produces an equivalent dbt model. Any implementation language is allowed. The supplied XML is the starting input. Conversion logic must derive the output from the XML, not reproduce hard-coded Jaffle Shop SQL.

PowerCenter represents data movement and transformations as mappings. dbt expresses warehouse transformations as SQL models. The task is to understand the former and generate the latter with sensible, documented limits.

## Required work

1. Inspect the sample XML and explain what its mapping does.
2. Implement a converter that derives equivalent dbt SQL from the XML.
3. Include tests. The linked Jaffle Shop project can be used as a reference where applicable.
4. Handle a reasonable subset within the time available. Full PowerCenter coverage is not expected.

## Coding-agent use

The brief explicitly expects coding-agent use. The submission must include:

- The prompts used, starting with the initial prompt.
- A full conversation export if the coding tool supports it and it can be shared without unrelated private content.
- A short account of the process followed with the agent.
- An actual example of something the agent got wrong, plus how it was caught.

BMAD was selected by the candidate as the development method. It is not a requirement from Infinite Lambda.

## Submission

Submit a GitHub repository or a zipped folder. A private repository needs access for the reviewers. The brief contains a placeholder for reviewer GitHub handles; actual handles are not available in the supplied material.

The short README must cover:

- How to run the tool.
- Assumptions and deliberately unsupported cases.
- Where the converter is most likely to produce incorrect output.
- An observed agent mistake and its detection.
- Agent prompts and the process used.

Assessment focuses on understanding the submitted code, explaining conversion choices and failure modes, and clear reasoning in the README.

## Time and deadline

- Expected effort: approximately four hours. The brief asks candidates not to over-invest.
- The recruiter email specifies **23 October 2026**. The assignment page separately says one week from receipt. Use the earlier, explicit email date unless clarified.
- No deadline time or timezone is specified.
- Submission and the requested recruiter notification are separate, later actions. Neither has been performed.

## Supplied public resources

- Sample XML: https://github.com/infinitelambda/flowline-pwc-demo
- DuckDB Jaffle Shop reference: https://github.com/dbt-labs/jaffle_shop_duckdb
- PowerCenter mappings: https://docs.informatica.com/data-integration/powercenter/10-5/designer-guide/mappings/mappings-overview.html
- PowerCenter transformations: https://docs.informatica.com/data-integration/powercenter/10-5/transformation-guide/preface.html
- dbt introduction: https://docs.getdbt.com/docs/introduction
- dbt models: https://docs.getdbt.com/docs/build/models
- SQL models: https://docs.getdbt.com/docs/build/sql-models
- dbt guides: https://docs.getdbt.com/guides

The private assignment/submission URL and personal contact information are intentionally not included.
