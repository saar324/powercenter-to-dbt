# Third-party material

## BMAD Method

The installed files in `.agents/skills/` and `_bmad/` originate from BMAD Method 6.12.4, package `bmad-method`, by BMad Code contributors.

- Upstream: https://github.com/bmad-code-org/BMAD-METHOD
- License: MIT. See `licenses/BMAD-METHOD-MIT.txt` for the upstream notice bundled with the installed npm package.
- Project configuration and project-specific overrides are identified separately from vendor skill sources.

## PowerCenter sample

`fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml` and `UPSTREAM_README.md` are supplied exercise materials from Infinite Lambda's public `flowline-pwc-demo` repository. The XML is preserved unchanged.

- Upstream: https://github.com/infinitelambda/flowline-pwc-demo
- Revision and checksums: `fixtures/powercenter/provenance.json`.
- No license file was present in the inspected sample repository. This notice attributes the material and does not assign it a new license.

## Jaffle Shop reference

The ignored local reference checkout originates from `dbt-labs/jaffle_shop_duckdb`. It is not vendored into this repository. Its upstream repository contains an Apache-2.0 license. The inspected revision is recorded in `references/README.md`.
