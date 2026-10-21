# Prepared first BMAD prompt

**Status: prepared during setup; not yet executed.**

Invoke the installed `bmad-spec` skill in an interactive coding chat opened at this repository. Use the following prompt as input:

```text
Use BMAD 6.12.4 to prepare the specification for this Infinite Lambda take-home exercise.

Read AGENTS.md, docs/assignment.md, docs/sample-findings.md,
docs/evidence/sample-inventory.json, docs/open-decisions.md, and the original
fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml. Inspect the source definitions,
instances, field connections, and expressions before proposing support.

The task is a small PowerCenter XML-to-dbt converter. Derive output from the XML;
do not hard-code Jaffle Shop SQL. Plan for approximately four hours of exercise
work. Propose a small, useful supported subset, with explicit exclusions and
observable acceptance criteria. Do not expand into a general migration platform.

The linked DuckDB reference has a different schema from the XML. Treat the XML
as the source of conversion meaning. Plan independent semantic tests and
changed-name / changed-expression tests, plus relevant failure cases.

Use short, clear English. Define unfamiliar technical terms. Surface unresolved
choices and assumptions. Keep the process visible in the repository, including
the specification, decisions, prompts, verification evidence, and actual agent
mistakes and corrections.

Create the specification through bmad-spec. Review it with me before converter
implementation. Do not run Build, publish the repository, submit the assignment,
or contact the recruiter as part of this specification step.
```

When this prompt is actually used, append the invocation, date, resulting artifact paths, and relevant human decisions to `prompts.md` and `work-log.md`.
