# XML input handling and reproducible conversion

Researched 22 October 2026. Recommendations for the approved Python CLI stack; no implementation, package installation or security test has occurred.

## Parse the document as XML

ElementTree represents XML elements, attributes and nesting. Use a real parser to read that structure; conversion still needs separate logic to interpret PowerCenter objects and links. [Python 3.13 ElementTree documentation](https://docs.python.org/3.13/library/xml.etree.elementtree.html).

**Verified fixture facts:** the supplied file declares Windows-1252 encoding and an external `powrmart.dtd`. Preserve the original bytes and checksum. Passing the file to the XML parser lets its encoding declaration be handled; blindly decoding it as UTF-8 can corrupt or reject characters. A DOCTYPE declaration is not permission to fetch a remote DTD or execute instructions.

**Recommendation:** keep parsing, object/reference validation and expression interpretation separate. Never use Python `eval` to execute expression strings from the export. A syntactically valid XML document can still contain unsupported or inconsistent mapping logic.

## Use bounded, explicit input behavior

Python documents XML entity/resource risks and notes that Expat's behavior depends on its installed version; a Python version alone is not a complete parser-security claim. Expat does not normally create network connections or access files by itself. [Python XML security guidance](https://docs.python.org/3.13/library/xml.html#xml-security).

**Recommendations for later setup:** record the actual parser/runtime version, preserve non-fetching behavior and add focused malformed/entity-input checks. Do not call the CLI safe for arbitrary hostile uploads from a successful parse of this supplied export. If service-style hostile-input support becomes a requirement, evaluate resource limits and a hardened parser as a separate scope change. No blanket ban on the supplied DOCTYPE is proposed.

The export also contains runtime SQL, including a target's pre-SQL TRUNCATE statement. Treat it as source metadata to classify and report; the converter must not execute database commands from XML while reading it. Query conversion and PowerCenter session side effects are different support boundaries.

## Keep identities and outputs explicit

PowerCenter object names and instance aliases are data. Resolve exact identities before translating them into database identifiers, dbt model names or filesystem paths. Recommendations: quote identifiers through defined SQL rules, detect name collisions, restrict generated files to the chosen output directory and report unsupported names rather than silently alter their meaning.

A failed run must not leave an old model looking like fresh success. Choose a documented clean-directory/staged-write policy and include it in CLI acceptance tests. This is a design recommendation; no file-emission policy has been implemented.

## Lock the environment and preserve provenance

uv distinguishes resolving a lockfile from syncing an environment. Use a committed project definition and lockfile, then verify the declared environment can reproduce the documented commands. A lockfile does not establish semantic correctness. [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/).

Keep the supplied input unchanged and identify source, revision, configuration and installed versions in real verification records. SQL determinism is separate from timestamped run reports. Compare generated SQL/model artifacts for repeatability; do not demand identical timestamps from separate executions.

## Appropriate scope

These practices concern the local converter and its generated files. They do not require a web server, production credentials or a running database for translation. Database execution belongs in the controlled validation step. See the [native verification contract](../_bmad-output/specs/spec-powercenter-to-dbt/validation-and-reporting.md) for the authoritative reporting requirements.

The documentation pages were read in relevant sections; runtime/parser behavior and proposed safeguards were not tested. Validate them during native Build if included in the approved scope.
