# Converter tests

No converter tests exist yet. This directory does not constitute passing product verification.

During implementation, add tests for the agreed conversion rules, independent SQL result comparisons on synthetic data, changed XML names and expressions, and relevant invalid or unsupported input. Use separate fixtures; preserve the original supplied XML.

Run the future suite with:

```sh
uv run --locked --all-groups pytest
```

The CI workflow runs pytest once Python test files exist. Until then, its test step explicitly reports that product verification is pending.
