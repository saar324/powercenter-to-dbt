# Jaffle Shop reference

Public upstream: https://github.com/dbt-labs/jaffle_shop_duckdb

Inspected revision: `20cc904370818ceab08cf19f8fd196e9e81def88`.

The local setup includes an ignored checkout under `work/jaffle_shop_duckdb`. To recreate it from a clean clone:

```sh
git clone https://github.com/dbt-labs/jaffle_shop_duckdb.git work/jaffle_shop_duckdb
git -C work/jaffle_shop_duckdb checkout --detach 20cc904370818ceab08cf19f8fd196e9e81def88
```

This is reference material, not converter code. Do not execute its original dbt profile against an external warehouse. Use a local DuckDB profile and disable anonymous usage statistics for local runs.

At this revision, its seeds are customers, orders, and payments. The supplied PowerCenter XML has a different schema and additional entities. See `docs/sample-findings.md` before selecting comparison cases.

Reference-model execution has not been used as product acceptance evidence during setup. No complete equivalent-output claim is made.
