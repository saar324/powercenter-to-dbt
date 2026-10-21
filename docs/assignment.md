# Take-home exercise: Informatica PowerCenter to dbt converter

The text below is transcribed from the supplied assignment description. The recruiter email excerpt is separate at the end. No analysis or implementation guidance has been added.

This exercise is part of our interview process for the Product Engineer role. Plan for about four hours of work. You have one week from receipt to return it.

## What we are asking

Build a small tool that converts an Informatica PowerCenter mapping into an equivalent dbt model. We have attached one sample PowerCenter mapping file in XML to work from. Download the demo XML workflow here:

https://github.com/infinitelambda/flowline-pwc-demo

The mapping mirrors the dbt jaffle shop demo project, which is public. You can use that project as a reference target: run it, look at its models, and check your converter's output against it. Build a converter that derives the dbt model from the XML. Do not hard-code the jaffle shop output, because we are assessing the conversion logic, not the final SQL. You are not expected to know either tool in advance. Part of what we want to see is how you get up to speed on an unfamiliar system, so the reading below is enough to start.

## Background

Informatica PowerCenter is an ETL tool. A mapping describes how data moves from source tables to target tables through a chain of transformations (filters, joins, lookups, aggregations, and so on). Mappings can be exported as XML, which is the format we have given you.

- Mappings overview: https://docs.informatica.com/data-integration/powercenter/10-5/designer-guide/mappings/mappings-overview.html
- Transformation guide: https://docs.informatica.com/data-integration/powercenter/10-5/transformation-guide/preface.html

dbt transforms data already in a warehouse using SQL. A dbt model is a single SQL select statement in a .sql file that dbt turns into a table or view. Models can reference each other, and you can attach tests and documentation.

- What is dbt: https://docs.getdbt.com/docs/introduction
- About dbt models: https://docs.getdbt.com/docs/build/models
- SQL models: https://docs.getdbt.com/docs/build/sql-models
- Quickstart guides: https://docs.getdbt.com/guides
- Jaffle shop reference project (runs locally with DuckDB in about a minute): https://github.com/dbt-labs/jaffle_shop_duckdb

## The task

- Read the sample PowerCenter XML and work out what the mapping does.
- Build a converter, in any language you choose, that reads a PowerCenter mapping XML and produces an equivalent dbt model.
- Include tests. You can check your output against the jaffle shop reference project.
- Handle what you reasonably can in the time. We care more about how you reason about the problem than about full coverage.

## Using coding agents

We expect you to use coding agents such as Claude Code or Cursor. This is how the team works day to day, and we want to see how you use them. If you do not have access to a tool, tell us and we may be able to provide access or refund you for your spend.

## What to submit

A GitHub repository (public, or private with access granted to [GitHub handles]) or a zipped folder, with a short README that covers:

- How to run it.
- What you assumed, and what you chose not to handle.
- Where the converter is most likely to produce wrong output.
- Where a coding agent got something wrong, and how you caught it.
- The prompts you gave the coding agent, starting with your initial prompt. If your tool can export the full agent conversation, include it as a file in the repository.
- A short outline of the process you followed with the agent to build the solution.

## What we are looking for

- You understand the code you submit and can explain any part of it.
- Sensible handling of the conversion, with a clear view of where it breaks.
- Clear reasoning in the README.

## Logistics

- Effort: about 04 hours. Please do not over-invest.
- Deadline: one week from receipt.
- Questions: contact Chau.

## Recruiter email excerpt — 20 October 2026

- Estimated effort: approximately 4 hours. Please do not over-invest.
- Deadline: Oct 23, 2026.
- Submit your Github repository or a zipped folder using the provided link or by email.

Please notify me once you have submitted it.

Personal contact details and the private submission URL are omitted from this repository copy.
