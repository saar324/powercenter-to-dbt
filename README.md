# Infinite Lambda take-home exercise

This repository contains the supplied assignment materials and BMAD tooling.

- [Assignment instructions](docs/assignment.md)
- [Original supplied XML](fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml)
- [Original upstream README](fixtures/powercenter/UPSTREAM_README.md)
- [Source provenance and checksums](fixtures/powercenter/provenance.json)

No solution language, design, supported subset, implementation plan, or test approach has been selected. Start fresh from the original assignment.

## BMAD setup

BMAD Method 6.12.4 is installed for Codex in `.agents/skills/` and `_bmad/`.
The `_bmad-output/` directory is empty.

To restore the pinned installer dependencies:

```sh
npm ci --ignore-scripts
```

To reinstall BMAD if needed:

```sh
npm run setup:bmad
```

Open this repository as the coding tool's project root. BMAD's own help is available through the installed `bmad-help` skill.

The repository setup check verifies tooling configuration and unchanged supplied files only.

## Agent error caught during setup

During setup, the coding agent added analysis and proposed implementation choices when I had asked only for repository preparation. I caught this by reviewing the repository files and questioning what had already been added. I asked the agent to remove those additions and the converter-specific scaffolding, keeping the supplied materials and BMAD setup. The cleanup is recorded in commit `270a3d8`. This occurred before converter implementation.

See [third-party notices](THIRD_PARTY_NOTICES.md).
