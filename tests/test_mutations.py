from collections import Counter
import json
from decimal import Decimal as D

import duckdb
import pytest

from .helpers import STAGING, config, convert_to, mutated, run_dbt


@pytest.mark.mutation
@pytest.mark.parametrize('change_type', ['expression', 'wiring', 'source_and_target_names', 'new_target_instance'])
def test_xml_mutations_change_actual_dbt_results(tmp_path, request, change_type):
    configuration = config()
    selection = STAGING + ('STG_PRODUCTS' if change_type in {'expression', 'wiring'} else 'STG_CUSTOMERS')
    expected_columns = ['PRODUCT_ID', 'PRODUCT_NAME', 'PRODUCT_TYPE', 'PRODUCT_PRICE_CENTS', 'PRODUCT_PRICE', 'PRODUCT_DESCRIPTION', 'IS_FOOD_ITEM', 'IS_DRINK_ITEM']
    expected_rows = [('p1', 'Test', 'JAFFLE', 12.5 if change_type == 'expression' else 125.0, D('125.00') if change_type == 'expression' else D('1.25'), None, D('1'), D('0'))]

    def change(root):
        mapping = root.find(".//MAPPING[@NAME='m_FL_JS_STAGING_FULL']")
        if change_type == 'expression':
            mapping.find("TRANSFORMATION[@NAME='EXP_PRODUCTS']/TRANSFORMFIELD[@NAME='PRODUCT_PRICE']").set('EXPRESSION', 'PRICE/10')
        elif change_type == 'wiring':
            mapping.find("CONNECTOR[@TOINSTANCE='STG_PRODUCTS'][@TOFIELD='PRODUCT_PRICE_CENTS']").set('FROMFIELD', 'PRODUCT_PRICE_CENTS')
            mapping.find("CONNECTOR[@TOINSTANCE='STG_PRODUCTS'][@TOFIELD='PRODUCT_PRICE']").set('FROMFIELD', 'PRODUCT_PRICE')
        elif change_type == 'source_and_target_names':
            root.find(".//SOURCE[@NAME='RAW_CUSTOMERS']/SOURCEFIELD[@NAME='ID']").set('NAME', 'CLIENT_KEY')
            mapping.find("CONNECTOR[@FROMINSTANCE='RAW_CUSTOMERS'][@FROMFIELD='ID']").set('FROMFIELD', 'CLIENT_KEY')
            root.find(".//TARGET[@NAME='STG_CUSTOMERS']/TARGETFIELD[@NAME='CUSTOMER_ID']").set('NAME', 'CLIENT_ID')
            mapping.find("CONNECTOR[@TOINSTANCE='STG_CUSTOMERS'][@TOFIELD='CUSTOMER_ID']").set('TOFIELD', 'CLIENT_ID')
        else:
            mapping.find("INSTANCE[@NAME='STG_CUSTOMERS']").set('NAME', 'REVIEW_CLIENTS')
            for link in mapping.findall("CONNECTOR[@TOINSTANCE='STG_CUSTOMERS']"):
                link.set('TOINSTANCE', 'REVIEW_CLIENTS')
    xml = mutated(tmp_path, request, change)
    if change_type == 'new_target_instance':
        selection = STAGING + 'REVIEW_CLIENTS'
        configuration['bindings'] = {key: target for key, target in configuration['bindings'].items() if target != STAGING + 'STG_CUSTOMERS'}
        configuration['target_relations'][selection] = configuration['target_relations'].pop(STAGING + 'STG_CUSTOMERS')
    project = tmp_path / 'project'
    _, _, artifacts, outcomes, manifest = convert_to(project, xml=xml, selected=[selection], configuration=configuration)
    assert len(artifacts) == 1, [(v.status, v.reason) for v in outcomes.values()]
    database = tmp_path / 'mutation.duckdb'
    with duckdb.connect(str(database)) as db:
        db.execute('CREATE SCHEMA RAW')
        if change_type in {'expression', 'wiring'}:
            db.execute('CREATE TABLE RAW.RAW_PRODUCTS (SKU VARCHAR, NAME VARCHAR, TYPE VARCHAR, PRICE DOUBLE, DESCRIPTION VARCHAR)')
            db.execute("INSERT INTO RAW.RAW_PRODUCTS VALUES ('p1', 'Test', 'JAFFLE', 125, '')")
        else:
            source_key = 'CLIENT_KEY' if change_type == 'source_and_target_names' else 'ID'
            db.execute(f'CREATE TABLE RAW.RAW_CUSTOMERS ({source_key} VARCHAR, NAME VARCHAR)')
            db.execute("INSERT INTO RAW.RAW_CUSTOMERS VALUES ('c1', 'Test'), ('c1', 'Test'), ('', '   ')")
            expected_columns = ['CLIENT_ID' if change_type == 'source_and_target_names' else 'CUSTOMER_ID', 'CUSTOMER_NAME']
            expected_rows = [('c1', 'Test'), ('c1', 'Test'), (None, '   ')]
    run_dbt(project, database, change_type)
    model = next(iter(artifacts.values())).plan
    with duckdb.connect(str(database)) as db:
        cursor = db.execute(f'SELECT * FROM converted."{model.alias}"')
        assert [column[0] for column in cursor.description] == expected_columns
        assert Counter(cursor.fetchall()) == Counter(expected_rows)


@pytest.mark.mutation
def test_sort_direction_null_and_case_settings_follow_xml(tmp_path, request):
    def change(root):
        sorter = root.find(".//MAPPING[@NAME='m_FL_JS_STAGING_FULL']/TRANSFORMATION[@NAME='SRT_ORDERS']")
        sorter.find("TABLEATTRIBUTE[@NAME='Case Sensitive']").set('VALUE', 'NO')
        sorter.find("TABLEATTRIBUTE[@NAME='Null Treated Low']").set('VALUE', 'YES')
        sorter.find("TRANSFORMFIELD[@NAME='ORDER_ID']").set('SORTDIRECTION', 'DESCENDING')
    xml = mutated(tmp_path, request, change)
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'project', xml=xml, selected=[STAGING + 'STG_ORDERS'])
    assert len(artifacts) == 1
    sql = next(iter(artifacts.values())).sql
    assert 'lower("ORDER_ID") DESC NULLS LAST' in sql
    database = tmp_path / 'sort.duckdb'
    with duckdb.connect(str(database)) as db:
        db.execute('CREATE SCHEMA RAW')
        db.execute('CREATE TABLE RAW.RAW_ORDERS (ID VARCHAR, CUSTOMER VARCHAR, ORDERED_AT TIMESTAMP, STORE_ID VARCHAR, SUBTOTAL DOUBLE, TAX_PAID DOUBLE, ORDER_TOTAL DECIMAL(12,2))')
        db.execute("INSERT INTO RAW.RAW_ORDERS VALUES ('a','c',NULL,'l',0,0,0),('B','c',NULL,'l',0,0,0),(NULL,'c',NULL,'l',0,0,0)")
    run_dbt(tmp_path / 'project', database, 'sort-mutation')
    alias = next(iter(artifacts.values())).plan.alias
    with duckdb.connect(str(database)) as db:
        assert db.execute(f'SELECT ORDER_ID FROM converted."{alias}"').fetchall() == [('B',), ('a',), (None,)]


@pytest.mark.mutation
@pytest.mark.parametrize('operation', ['join', 'aggregate', 'unused-bound-source-port'])
def test_join_aggregate_and_bound_projection_mutations(tmp_path, request, operation):
    import importlib.util
    import xml.etree.ElementTree as ET
    from .conftest import ROOT
    from .helpers import CORE
    from .test_dbt_results import DAYS, EXPECTED_COLUMNS, EXPECTED_TYPES

    def change(root):
        mapping = root.find(".//MAPPING[@NAME='m_FL_JS_MARTS_CORE']")
        if operation == 'join':
            mapping.find("TRANSFORMATION[@NAME='JNR_CUSTOMERS_ORDERS']/TABLEATTRIBUTE[@NAME='Join Condition']").set('VALUE', "CUSTOMER_ID = CUSTOMER_ID1 AND CUSTOMER_ID = 'c2'")
        elif operation == 'aggregate':
            mapping.find("TRANSFORMATION[@NAME='AGG_ORDERS_BY_CUSTOMER']/TRANSFORMFIELD[@NAME='LIFETIME_SPEND']").set('EXPRESSION', 'MAX(ORDER_TOTAL)')
        else:
            ET.SubElement(root.find(".//SOURCE[@NAME='STG_CUSTOMERS']"), 'SOURCEFIELD', NAME='UNUSED_COLUMN', DATATYPE='varchar2', PRECISION='50', SCALE='0', FIELDNUMBER='3')
    xml = mutated(tmp_path, request, change)
    project = tmp_path / 'project'
    _, _, artifacts, outcomes, _ = convert_to(project, xml=xml, selected=[CORE + 'CUSTOMERS'])
    assert len(artifacts) == 3, [(o.status, o.reason) for o in outcomes.values()]
    database = tmp_path / 'operation.duckdb'
    loader_spec = importlib.util.spec_from_file_location('operation_loader', ROOT / 'examples/load_demo.py')
    loader = importlib.util.module_from_spec(loader_spec)
    loader_spec.loader.exec_module(loader)
    loader.load(database)
    run_dbt(project, database, operation)
    alias = next(artifact.plan.alias for key, artifact in artifacts.items() if key.instance == 'CUSTOMERS')
    spend = D('151.00') if operation == 'aggregate' else D('137.00')
    customer_one = ('c1', 'Aster', 3.0, DAYS['leap'], DAYS['old'], spend, D('115.00'), D('23.00'), 'returning')
    rows = [customer_one, customer_one,
            ('c2', 'Birch', 1.0, DAYS['last'], DAYS['last'], D('1.00'), D('1.00'), D('-1.00'), 'new'),
            (None, None, 1.0, DAYS['other'], DAYS['other'], D('0.00'), D('0.00'), D('0.00'), 'new'),
            (None, None, 0.0, None, None, D('0.00'), D('0.00'), D('0.00'), 'new')]
    if operation == 'join':
        rows = [(None, None, *customer_one[2:]), *rows[2:]]
    with duckdb.connect(str(database)) as db:
        cursor = db.execute(f'SELECT * FROM converted."{alias}"')
        assert [column[0] for column in cursor.description] == EXPECTED_COLUMNS[CORE + 'CUSTOMERS']
        assert [str(column[1]) for column in cursor.description] == EXPECTED_TYPES[CORE + 'CUSTOMERS']
        assert Counter(cursor.fetchall()) == Counter(rows)


@pytest.mark.mutation
def test_double_error_default_runs_through_generated_dbt(tmp_path, request):
    def change(root):
        root.find(".//MAPPING[@NAME='m_FL_JS_STAGING_FULL']/TRANSFORMATION[@NAME='EXP_SUPPLIES']/TRANSFORMFIELD[@NAME='SUPPLY_COST']").set('EXPRESSION', 'COST/0')
    xml = mutated(tmp_path, request, change)
    project = tmp_path / 'project'
    _, _, artifacts, outcomes, _ = convert_to(project, xml=xml, selected=[STAGING + 'STG_SUPPLIES'])
    assert len(artifacts) == 1
    database = tmp_path / 'default.duckdb'
    with duckdb.connect(str(database)) as db:
        db.execute('CREATE SCHEMA RAW')
        db.execute('CREATE TABLE RAW.RAW_PRODUCTS (SKU VARCHAR, NAME VARCHAR, TYPE VARCHAR, PRICE DOUBLE, DESCRIPTION VARCHAR)')
        db.execute("INSERT INTO RAW.RAW_PRODUCTS VALUES ('p1','Test','JAFFLE',125,'')")
        db.execute('CREATE TABLE RAW.RAW_SUPPLIES (ID VARCHAR, NAME VARCHAR, COST DOUBLE, PERISHABLE VARCHAR, SKU VARCHAR)')
        db.execute("INSERT INTO RAW.RAW_SUPPLIES VALUES ('s1','Test',250,'Y','p1'),('s2','Null cost',NULL,'Y','p1')")
    run_dbt(project, database, 'double-error-default')
    alias = next(iter(artifacts.values())).plan.alias
    with duckdb.connect(str(database)) as db:
        cursor = db.execute(f'SELECT * FROM converted."{alias}"')
        assert [column[0] for column in cursor.description] == ['SUPPLY_ID', 'SUPPLY_NAME', 'SUPPLY_COST_CENTS', 'SUPPLY_COST', 'IS_PERISHABLE', 'PRODUCT_ID']
        assert Counter(cursor.fetchall()) == Counter([('s1', 'Test', D('250.00'), D('0.00'), D('1'), 'p1'),
                                                    ('s2', 'Null cost', None, None, D('1'), 'p1')])


@pytest.mark.mutation
def test_target_fieldnumber_overrides_physical_xml_order(tmp_path, request):
    from .test_dbt_results import EXPECTED_COLUMNS, EXPECTED_TYPES
    def change(root):
        target = root.find(".//TARGET[@NAME='STG_CUSTOMERS']")
        fields = target.findall('TARGETFIELD')
        for field in fields:
            target.remove(field)
        target.extend(reversed(fields))
    xml = mutated(tmp_path, request, change)
    project = tmp_path / 'project'
    _, _, artifacts, outcomes, _ = convert_to(project, xml=xml, selected=[STAGING + 'STG_CUSTOMERS'])
    assert len(artifacts) == 1
    database = tmp_path / 'ordinals.duckdb'
    with duckdb.connect(str(database)) as db:
        db.execute('CREATE SCHEMA RAW')
        db.execute('CREATE TABLE RAW.RAW_CUSTOMERS (ID VARCHAR, NAME VARCHAR)')
        db.execute("INSERT INTO RAW.RAW_CUSTOMERS VALUES ('c1','Test'),('c1','Test'),('', '   ')")
    run_dbt(project, database, 'target-fieldnumber-order')
    alias = next(iter(artifacts.values())).plan.alias
    with duckdb.connect(str(database)) as db:
        cursor = db.execute(f'SELECT * FROM converted."{alias}"')
        assert [column[0] for column in cursor.description] == EXPECTED_COLUMNS[STAGING + 'STG_CUSTOMERS']
        assert [str(column[1]) for column in cursor.description] == EXPECTED_TYPES[STAGING + 'STG_CUSTOMERS']
        assert Counter(cursor.fetchall()) == Counter([('c1', 'Test'), ('c1', 'Test'), (None, '   ')])
