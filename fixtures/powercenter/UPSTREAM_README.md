# Flowline PowerCenter Demo — Jaffle Shop

A single Informatica PowerCenter repository export (`FLOWLINE_DEMO_JAFFLESHOP.xml`) that reimplements the dbt [Jaffle Shop](https://github.com/dbt-labs/jaffle-shop) demo project as a PowerCenter pipeline. Used for demo purposes only.

## Contents

The export contains one repository (`REPO_Jaffleshop`) and folder (`FLOWLINE_DEMO_JAFFLESHOP`) targeting Oracle, with:

- **Sources** — `RAW_*` tables (customers, orders, items, products, supplies, stores) plus staged `STG_*` tables.
- **Targets** — staging tables (`STG_*`), core marts (`CUSTOMERS`, `ORDERS`, `ORDER_ITEMS`, `PRODUCTS`, `SUPPLIES`), and enriched marts (`CUSTOMER_360`, `ORDER_FINANCIALS`, `ORDER_ITEM_ENRICHED`, `PRODUCT_DAILY_PERFORMANCE`, `STORE_DAILY_KPIS`).
- **Mappings** — `m_FL_JS_STAGING_FULL`, `m_FL_JS_MARTS_CORE`, `m_FL_JS_MARTS_ENRICHED`.
- **Workflow** — `wf_FL_JAFFLESHOP_DEMO`, running the three mappings via sessions `s_FL_JS_STAGING_FULL`, `s_FL_JS_MARTS_CORE`, `s_FL_JS_MARTS_ENRICHED`.

The pipeline flows RAW → staging → core marts → enriched marts.

## Usage

Import `FLOWLINE_DEMO_JAFFLESHOP.xml` into a PowerCenter repository via the Repository Manager or `pmrep`.
