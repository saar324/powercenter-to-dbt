from collections import Counter
from datetime import datetime
from decimal import Decimal as D
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import duckdb
import pytest

from .conftest import ROOT, RUN
from .helpers import CORE, REQUIRED, STAGING, convert_to, run_dbt

DAYS = {'old': datetime(2098, 1, 2), 'leap': datetime(2000, 2, 29), 'other': datetime(2024, 5, 6), 'last': datetime(2025, 12, 31)}

EXPECTED_TYPES = {
    STAGING + 'STG_CUSTOMERS': ['VARCHAR', 'VARCHAR'],
    STAGING + 'STG_ORDERS': ['VARCHAR', 'VARCHAR', 'VARCHAR', 'TIMESTAMP', 'DOUBLE', 'DOUBLE', 'DECIMAL(12,2)', 'DOUBLE', 'DOUBLE', 'DECIMAL(12,2)'],
    STAGING + 'STG_PRODUCTS': ['VARCHAR', 'VARCHAR', 'VARCHAR', 'DOUBLE', 'DECIMAL(12,2)', 'VARCHAR', 'DECIMAL(1,0)', 'DECIMAL(1,0)'],
    STAGING + 'STG_SUPPLIES': ['VARCHAR', 'VARCHAR', 'DECIMAL(12,2)', 'DECIMAL(12,2)', 'DECIMAL(1,0)', 'VARCHAR'],
    CORE + 'CUSTOMERS': ['VARCHAR', 'VARCHAR', 'DOUBLE', 'TIMESTAMP', 'TIMESTAMP', 'DECIMAL(12,2)', 'DECIMAL(12,2)', 'DECIMAL(12,2)', 'VARCHAR'],
}
EXPECTED_COLUMNS = {
    STAGING + 'STG_CUSTOMERS': ['CUSTOMER_ID', 'CUSTOMER_NAME'],
    STAGING + 'STG_ORDERS': ['ORDER_ID', 'CUSTOMER_ID', 'LOCATION_ID', 'ORDERED_AT_DAY', 'SUBTOTAL_CENTS', 'TAX_PAID_CENTS', 'ORDER_TOTAL_CENTS', 'SUBTOTAL', 'TAX_PAID', 'ORDER_TOTAL'],
    STAGING + 'STG_PRODUCTS': ['PRODUCT_ID', 'PRODUCT_NAME', 'PRODUCT_TYPE', 'PRODUCT_PRICE_CENTS', 'PRODUCT_PRICE', 'PRODUCT_DESCRIPTION', 'IS_FOOD_ITEM', 'IS_DRINK_ITEM'],
    STAGING + 'STG_SUPPLIES': ['SUPPLY_ID', 'SUPPLY_NAME', 'SUPPLY_COST_CENTS', 'SUPPLY_COST', 'IS_PERISHABLE', 'PRODUCT_ID'],
    CORE + 'CUSTOMERS': ['CUSTOMER_ID', 'CUSTOMER_NAME', 'LIFETIME_ORDERS', 'FIRST_ORDER_DATE', 'LAST_ORDER_DATE', 'LIFETIME_SPEND', 'LIFETIME_SPEND_PRETAX', 'LIFETIME_TAX_PAID', 'CUSTOMER_TYPE'],
}



@pytest.fixture(scope='module')
def executed(tmp_path_factory):
    directory = tmp_path_factory.mktemp('actual-dbt')
    project = directory / 'project'
    database = directory / 'controlled.duckdb'
    _, _, artifacts, outcomes, manifest = convert_to(project)
    assert len(artifacts) == 5, [(str(k), o.status, o.reason) for k, o in outcomes.items()]
    loader_spec = importlib.util.spec_from_file_location('demo_loader', ROOT / 'examples/load_demo.py')
    loader = importlib.util.module_from_spec(loader_spec)
    loader_spec.loader.exec_module(loader)
    loader.load(database)
    environment = os.environ | {'PWC_DUCKDB_PATH': str(database), 'DO_NOT_TRACK': '1', 'DBT_SEND_ANONYMOUS_USAGE_STATS': 'false'}
    command = [str(Path(sys.executable).parent / 'dbt'), 'run', '--project-dir', str(project), '--profiles-dir', str(project), '--no-use-colors']
    first = subprocess.run(command, text=True, capture_output=True, env=environment, timeout=120)
    evidence = ROOT / 'reports/evidence' / (RUN + '-dbt-first.txt')
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(first.stdout + first.stderr)
    assert first.returncode == 0, first.stdout + first.stderr
    model_rows = {outcome['target']: outcome for outcome in manifest['outcomes']}
    return project, database, environment, command, first, model_rows


def check_result(executed, target, columns, rows):
    _, database, _, _, _, model_rows = executed
    name = model_rows[target]['alias']
    with duckdb.connect(str(database)) as db:
        cursor = db.execute(f'SELECT * FROM converted."{name}"')
        assert [column[0] for column in cursor.description] == columns
        assert [str(column[1]) for column in cursor.description] == EXPECTED_TYPES[target]
        assert Counter(cursor.fetchall()) == Counter(rows)


@pytest.mark.result(target=STAGING + 'STG_CUSTOMERS')
def test_complete_staging_customers(executed):
    check_result(executed, STAGING + 'STG_CUSTOMERS', ['CUSTOMER_ID', 'CUSTOMER_NAME'],
                 [('c1', 'Aster'), ('c1', 'Aster'), ('c2', 'Birch'), ('idle', 'No orders'), (None, 'Null key'), (None, None), ('space', '   ')])


@pytest.mark.result(target=STAGING + 'STG_ORDERS')
def test_complete_staging_orders(executed):
    # XML connects each scaled output to the cents target and vice versa.
    check_result(executed, STAGING + 'STG_ORDERS',
                 ['ORDER_ID', 'CUSTOMER_ID', 'LOCATION_ID', 'ORDERED_AT_DAY', 'SUBTOTAL_CENTS', 'TAX_PAID_CENTS', 'ORDER_TOTAL_CENTS', 'SUBTOTAL', 'TAX_PAID', 'ORDER_TOTAL'],
                 [('o1', 'c1', 'l1', DAYS['old'], 1.25, 0.25, D('1.51'), 125.0, 25.0, D('151.00')),
                  ('o2', 'c1', 'l1', DAYS['leap'], -0.05, -0.01, D('-0.07'), -5.0, -1.0, D('-7.00')),
                  ('o2', 'c1', 'l1', DAYS['leap'], -0.05, -0.01, D('-0.07'), -5.0, -1.0, D('-7.00')),
                  ('o3', 'missing', 'l2', DAYS['other'], None, None, None, None, None, None),
                  (None, None, None, None, 0.0, 0.0, D('0.00'), 0.0, 0.0, D('0.00')),
                  ('o4', 'c2', 'l2', DAYS['last'], 0.01, -0.01, D('0.01'), 1.0, -1.0, D('1.00'))])


@pytest.mark.result(target=STAGING + 'STG_PRODUCTS')
def test_complete_staging_products(executed):
    # The XML deliberately connects the two price outputs to crossed targets.
    check_result(executed, STAGING + 'STG_PRODUCTS',
                 ['PRODUCT_ID', 'PRODUCT_NAME', 'PRODUCT_TYPE', 'PRODUCT_PRICE_CENTS', 'PRODUCT_PRICE', 'PRODUCT_DESCRIPTION', 'IS_FOOD_ITEM', 'IS_DRINK_ITEM'],
                 [('p1', 'Jaffle', ' jaffle ', 1.25, D('125.00'), None, D('1'), D('0')),
                  ('p1', 'Jaffle duplicate', 'BEVERAGE', -0.05, D('-5.00'), 'cold', D('0'), D('1')),
                  ('p2', 'No type', None, None, None, '   ', D('0'), D('0')),
                  (None, 'No SKU', None, 0.01, D('1.00'), None, D('0'), D('0'))])


@pytest.mark.result(target=STAGING + 'STG_SUPPLIES')
def test_complete_staging_supplies(executed):
    check_result(executed, STAGING + 'STG_SUPPLIES',
                 ['SUPPLY_ID', 'SUPPLY_NAME', 'SUPPLY_COST_CENTS', 'SUPPLY_COST', 'IS_PERISHABLE', 'PRODUCT_ID'],
                 [('s1', 'Flour', D('250.00'), D('2.50'), D('1'), 'p1'),
                  ('s1', 'Flour', D('250.00'), D('2.50'), D('1'), 'p1'),
                  ('s2', 'Null cost', None, None, D('1'), 'p1'),
                  ('s2', 'Null cost', None, None, D('1'), 'p1'),
                  ('s5', 'Spaces', D('-5.00'), D('-0.05'), D('0'), 'p2')])


@pytest.mark.result(target=CORE + 'CUSTOMERS')
def test_complete_core_customers(executed):
    check_result(executed, CORE + 'CUSTOMERS',
                 ['CUSTOMER_ID', 'CUSTOMER_NAME', 'LIFETIME_ORDERS', 'FIRST_ORDER_DATE', 'LAST_ORDER_DATE', 'LIFETIME_SPEND', 'LIFETIME_SPEND_PRETAX', 'LIFETIME_TAX_PAID', 'CUSTOMER_TYPE'],
                 [('c1', 'Aster', 3.0, DAYS['leap'], DAYS['old'], D('137.00'), D('115.00'), D('23.00'), 'returning'),
                  ('c1', 'Aster', 3.0, DAYS['leap'], DAYS['old'], D('137.00'), D('115.00'), D('23.00'), 'returning'),
                  ('c2', 'Birch', 1.0, DAYS['last'], DAYS['last'], D('1.00'), D('1.00'), D('-1.00'), 'new'),
                  (None, None, 1.0, DAYS['other'], DAYS['other'], D('0.00'), D('0.00'), D('0.00'), 'new'),
                  (None, None, 0.0, None, None, D('0.00'), D('0.00'), D('0.00'), 'new')])


@pytest.mark.lifecycle
def test_first_repeat_cleanup_stale_rows_and_order(executed):
    project, database, environment, command, first, models = executed
    assert first.stdout.count('action=absent') == 5
    target = models[STAGING + 'STG_CUSTOMERS']['alias']
    with duckdb.connect(str(database)) as db:
        db.execute(f'INSERT INTO converted."{target}" VALUES (\'stale\', \'Removed\')')
    second = subprocess.run(command, text=True, capture_output=True, env=environment, timeout=120)
    (ROOT / 'reports/evidence' / (RUN + '-dbt-repeat.txt')).write_text(second.stdout + second.stderr)
    assert second.returncode == 0, second.stdout + second.stderr
    assert second.stdout.count('action=delete') == 5
    # Adapter logs capture the actual hook query before CREATE TABLE, not just
    # the final replacement result (which a table materialization could mask).
    log = (project / 'logs/dbt.log').read_text()
    delete = log.rfind(f'delete from "controlled"."converted"."{target}"')
    assert delete >= 0, 'actual cleanup query absent from dbt debug log'
    # Exact adapter whitespace can vary; the SQL log still proves hook order.
    subsequent = log[delete:]
    assert '__dbt_tmp' in subsequent and 'create' in subsequent.lower()
    (ROOT / 'reports/evidence' / (RUN + '-cleanup-order.txt')).write_text(subsequent[:5000])
    with duckdb.connect(str(database)) as db:
        assert db.execute(f'SELECT count(*) FROM converted."{target}" WHERE CUSTOMER_ID=\'stale\'').fetchone() == (0,)
        assert db.execute(f'SELECT count(*) FROM converted."{target}"').fetchone() == (7,)


@pytest.mark.boundary
def test_mapping_sort_is_explicit_and_observed(executed):
    project, database, _, _, _, models = executed
    model = models[STAGING + 'STG_ORDERS']
    sql = (project / 'models' / (model['model_name'] + '.sql')).read_text()
    assert sql.count('ORDER BY') == 2
    assert 'NULLS LAST' in sql
    with duckdb.connect(str(database)) as db:
        rows = db.execute(f'SELECT ORDER_ID FROM converted."{model["alias"]}"').fetchall()
    assert rows == [('o1',), ('o2',), ('o2',), ('o3',), ('o4',), (None,)]


@pytest.fixture(scope='module')
def empty_executed(tmp_path_factory):
    directory = tmp_path_factory.mktemp('empty-dbt')
    project = directory / 'project'
    database = directory / 'empty.duckdb'
    _, _, artifacts, outcomes, manifest = convert_to(project)
    loader_spec = importlib.util.spec_from_file_location('empty_demo_loader', ROOT / 'examples/load_demo.py')
    loader = importlib.util.module_from_spec(loader_spec)
    loader_spec.loader.exec_module(loader)
    loader.load(database)
    with duckdb.connect(str(database)) as db:
        for table in ['RAW_CUSTOMERS', 'RAW_ORDERS', 'RAW_PRODUCTS', 'RAW_SUPPLIES']:
            db.execute(f'DELETE FROM RAW.{table}')
    result = run_dbt(project, database, 'empty-inputs')
    models = {outcome['target']: outcome for outcome in manifest['outcomes']}
    return project, database, None, None, result, models


@pytest.mark.parametrize('target', [pytest.param(key, marks=pytest.mark.result(target=key + ':empty-input')) for key in REQUIRED])
def test_complete_empty_inputs(empty_executed, target, request):
    request.node.actual_input_id = 'controlled-empty-tables:RAW_CUSTOMERS,RAW_ORDERS,RAW_PRODUCTS,RAW_SUPPLIES;fixture-XML-sha256:' + __import__('hashlib').sha256((ROOT / 'fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml').read_bytes()).hexdigest()
    check_result(empty_executed, target, EXPECTED_COLUMNS[target], [])
