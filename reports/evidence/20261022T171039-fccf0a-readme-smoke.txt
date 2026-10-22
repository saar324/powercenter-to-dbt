Actual fresh-destination README smoke run
revision: 9369d443d9d6bdef7a5a552d4747950e045d21c9+code-sha256:9455f781c9c3612d381030cbf1fb2d4e2dbecbd6ab133b060dc177d0fbfc10d3
2026-10-22T17:11:18.182870+00:00
command: uv sync --locked
exit: 0
Resolved 65 packages in 4ms
Checked 64 packages in 1ms

2026-10-22T17:11:18.248909+00:00
command: uv run pwc-to-dbt --help
exit: 0
usage: pwc-to-dbt [-h] [--output OUTPUT] [--bindings BINDINGS]
                  [--target TARGET] [--inventory]
                  xml

Convert supported PowerCenter mapping paths into a local DuckDB dbt project

positional arguments:
  xml                  PowerCenter export XML

options:
  -h, --help           show this help message and exit
  --output, -o OUTPUT  Absent or empty destination directory
  --bindings BINDINGS  JSON with exact bindings and original target_relations
  --target TARGET      Full target identity; repeat to select several;
                       default: all
  --inventory          Print exact target identities without conversion

2026-10-22T17:11:18.329482+00:00
command: uv run pwc-to-dbt fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml --bindings examples/sample-bindings.json --output .generated/demo --target REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/m_FL_JS_STAGING_FULL/STG_CUSTOMERS --target REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/m_FL_JS_STAGING_FULL/STG_ORDERS --target REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/m_FL_JS_STAGING_FULL/STG_PRODUCTS --target REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/m_FL_JS_STAGING_FULL/STG_SUPPLIES --target REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/m_FL_JS_MARTS_CORE/CUSTOMERS
exit: 0
emitted: REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/m_FL_JS_MARTS_CORE/CUSTOMERS: SQL generated; result verification is separate
emitted: REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/m_FL_JS_STAGING_FULL/STG_CUSTOMERS: SQL generated; result verification is separate
emitted: REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/m_FL_JS_STAGING_FULL/STG_ORDERS: SQL generated; result verification is separate
emitted: REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/m_FL_JS_STAGING_FULL/STG_PRODUCTS: SQL generated; result verification is separate
emitted: REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/m_FL_JS_STAGING_FULL/STG_SUPPLIES: SQL generated; result verification is separate

2026-10-22T17:11:18.425511+00:00
command: uv run python examples/load_demo.py .generated/demo/converter.duckdb
exit: 0

2026-10-22T17:11:20.500287+00:00
command: uv run dbt run --project-dir .generated/demo --profiles-dir .generated/demo
exit: 0
[0m17:11:19  Running with dbt=1.12.6
[0m17:11:19  Registered adapter: duckdb=1.10.1
[0m17:11:19  Unable to do partial parsing because saved manifest not found. Starting full parse.
[0m17:11:20  Found 5 models, 5 sources, 488 macros
[0m17:11:20  
[0m17:11:20  Concurrency: 1 threads (target='local')
[0m17:11:20  
[0m17:11:20  1 of 5 START sql table model converted.repo_jaffleshop__flowline_demo_jaffleshop__m_fl_js_staging_full__stg_customers  [RUN]
[0m17:11:20  PWC_CLEAR "converter"."converted"."repo_jaffleshop__flowline_demo_jaffleshop__m_fl_js_staging_full__stg_customers" action=absent
[0m17:11:20  1 of 5 OK created sql table model converted.repo_jaffleshop__flowline_demo_jaffleshop__m_fl_js_staging_full__stg_customers  [[32mOK[0m in 0.04s]
[0m17:11:20  2 of 5 START sql table model converted.repo_jaffleshop__flowline_demo_jaffleshop__m_fl_js_staging_full__stg_orders  [RUN]
[0m17:11:20  PWC_CLEAR "converter"."converted"."repo_jaffleshop__flowline_demo_jaffleshop__m_fl_js_staging_full__stg_orders" action=absent
[0m17:11:20  2 of 5 OK created sql table model converted.repo_jaffleshop__flowline_demo_jaffleshop__m_fl_js_staging_full__stg_orders  [[32mOK[0m in 0.02s]
[0m17:11:20  3 of 5 START sql table model converted.repo_jaffleshop__flowline_demo_jaffleshop__m_fl_js_staging_full__stg_products  [RUN]
[0m17:11:20  PWC_CLEAR "converter"."converted"."repo_jaffleshop__flowline_demo_jaffleshop__m_fl_js_staging_full__stg_products" action=absent
[0m17:11:20  3 of 5 OK created sql table model converted.repo_jaffleshop__flowline_demo_jaffleshop__m_fl_js_staging_full__stg_products  [[32mOK[0m in 0.02s]
[0m17:11:20  4 of 5 START sql table model converted.repo_jaffleshop__flowline_demo_jaffleshop__m_fl_js_staging_full__stg_supplies  [RUN]
[0m17:11:20  PWC_CLEAR "converter"."converted"."repo_jaffleshop__flowline_demo_jaffleshop__m_fl_js_staging_full__stg_supplies" action=absent
[0m17:11:20  4 of 5 OK created sql table model converted.repo_jaffleshop__flowline_demo_jaffleshop__m_fl_js_staging_full__stg_supplies  [[32mOK[0m in 0.02s]
[0m17:11:20  5 of 5 START sql table model converted.repo_jaffleshop__flowline_demo_jaffleshop__m_fl_js_marts_core__customers  [RUN]
[0m17:11:20  PWC_CLEAR "converter"."converted"."repo_jaffleshop__flowline_demo_jaffleshop__m_fl_js_marts_core__customers" action=absent
[0m17:11:20  5 of 5 OK created sql table model converted.repo_jaffleshop__flowline_demo_jaffleshop__m_fl_js_marts_core__customers  [[32mOK[0m in 0.02s]
[0m17:11:20  
[0m17:11:20  Finished running 5 table models in 0 hours 0 minutes and 0.19 seconds (0.19s).
[0m17:11:20  
[0m17:11:20  [32mCompleted successfully[0m
[0m17:11:20  
[0m17:11:20  Done. PASS=5 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=5

