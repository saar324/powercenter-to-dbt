"""Pinned reference execution and duplicate-aware comparisons; no converter rules.

SQL snapshots are immutable. Harness changes concern local profiles, inputs and
selected dependency closure only. Every comparison retains both actual outputs.
"""
from collections import Counter
from datetime import date, datetime
from decimal import Decimal
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import duckdb
import yaml

from .helpers import CORE, ROOT, STAGING, convert_to

REFERENCES = ROOT / 'fixtures/references'
PINS = json.loads((REFERENCES / 'provenance.json').read_text())
TARGETS = ['STG_CUSTOMERS', 'STG_ORDERS', 'STG_PRODUCTS', 'STG_SUPPLIES', 'CUSTOMERS']
DATASETS = ['ordinary', 'empty', 'edge']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins():
    for name, reference in PINS.items():
        for relative, expected in reference['files'].items():
            path = REFERENCES / name / relative
            if not path.is_file() or digest(path) != expected:
                raise ValueError(f'Pinned source missing or changed: {name}/{relative}')


def _command(project, database, name, command):
    from .conftest import RUN
    destination = ROOT / 'reports/evidence' / f'{RUN}-{name}'
    destination.mkdir(parents=True, exist_ok=True)
    args = [str(Path(sys.executable).parent / 'dbt'), command, '--project-dir', str(project),
            '--profiles-dir', str(project), '--no-use-colors']
    env = os.environ | {'PWC_DUCKDB_PATH': str(database), 'DO_NOT_TRACK': '1',
                        'DBT_SEND_ANONYMOUS_USAGE_STATS': 'false'}
    try:
        result = subprocess.run(args, capture_output=True, text=True, env=env, timeout=120)
        output = result.stdout + result.stderr
        error = None if result.returncode == 0 else f'dbt {command} exit={result.returncode}'
    except (OSError, subprocess.TimeoutExpired) as exc:
        output, error = str(exc), str(exc)
    (destination / 'console.txt').write_text('command: ' + ' '.join(args) + '\n' + output)
    for filename in ['manifest.json', 'run_results.json']:
        artifact = project / 'target' / filename
        if artifact.exists():
            shutil.copyfile(artifact, destination / filename)
    return error, str(destination.relative_to(ROOT))


def _profile(project, database, profile, schema):
    (project / 'profiles.yml').write_text(f'''{profile}:
  target: local
  outputs:
    local:
      type: duckdb
      path: '{database}'
      schema: {schema}
      threads: 1
''')


def _load_inputs(database, dataset):
    spec = importlib.util.spec_from_file_location('reference_input_loader', ROOT / 'examples/load_demo.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    loader.load(database)
    with duckdb.connect(str(database)) as db:
        if dataset != 'edge':
            for table in ['CUSTOMERS', 'ORDERS', 'PRODUCTS', 'SUPPLIES']:
                db.execute(f'DELETE FROM RAW.RAW_{table}')
        if dataset == 'ordinary':
            db.execute("INSERT INTO RAW.RAW_CUSTOMERS VALUES ('c1', 'Aster'), ('c2', 'Birch')")
            db.execute("INSERT INTO RAW.RAW_ORDERS VALUES ('o1', 'c1', '2025-01-02 15:30:00', 'l1', 125, 25, 150), ('o2', 'c2', '2025-05-03', 'l1', 200, 40, 240)")
            db.execute("INSERT INTO RAW.RAW_PRODUCTS VALUES ('p1', 'Jaffle', 'jaffle', 125, 'Warm')")
            db.execute("INSERT INTO RAW.RAW_SUPPLIES VALUES ('s1', 'Flour', 250, 'Y', 'p1')")
        # Supplemental upstream dependency, not a replacement for any core input.
        db.execute('CREATE TABLE RAW.RAW_ITEMS (ID VARCHAR, ORDER_ID VARCHAR, SKU VARCHAR)')
        if dataset == 'ordinary':
            db.execute("INSERT INTO RAW.RAW_ITEMS VALUES ('i1', 'o1', 'p1')")


def _csv_query(db, query, path, header):
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(db.execute(query).fetchall())


def _classic_inputs(project, database):
    # One full XML NAME is placed in classic first_name; last_name is absent.
    # Date/ID fields are copied, with no money or status equivalence claimed.
    with duckdb.connect(str(database)) as db:
        _csv_query(db, 'SELECT ID, NAME, NULL FROM RAW.RAW_CUSTOMERS', project / 'seeds/raw_customers.csv', ['id', 'first_name', 'last_name'])
        _csv_query(db, 'SELECT ID, CUSTOMER, CAST(ORDERED_AT AS DATE), NULL FROM RAW.RAW_ORDERS', project / 'seeds/raw_orders.csv', ['id', 'user_id', 'order_date', 'status'])
    (project / 'seeds/raw_payments.csv').write_text('id,order_id,payment_method,amount\n')


def _restore_classic_inputs(database):
    """Restore typed source values after CSV creates tables, before model SQL.

    CSV's absent-field encoding collapses None and ''. INSERT SELECT preserves
    both and uses the original typed inputs, without changing reference models.
    This bridge is never applied to the original-seed baseline.
    """
    with duckdb.connect(str(database)) as db:
        db.execute('DELETE FROM classic.raw_customers')
        db.execute('INSERT INTO classic.raw_customers SELECT ID, NAME, NULL FROM RAW.RAW_CUSTOMERS')
        db.execute('DELETE FROM classic.raw_orders')
        db.execute('INSERT INTO classic.raw_orders SELECT ID, CUSTOMER, CAST(ORDERED_AT AS DATE), NULL FROM RAW.RAW_ORDERS')


def _seed_generated_classic(database):
    """Original classic seeds -> declared XML input bridge; no inferred prices."""
    with duckdb.connect(str(database)) as db:
        for table in ['CUSTOMERS', 'ORDERS', 'PRODUCTS', 'SUPPLIES']:
            db.execute(f'DELETE FROM RAW.RAW_{table}')
        db.execute("INSERT INTO RAW.RAW_CUSTOMERS SELECT CAST(id AS VARCHAR), first_name || ' ' || last_name FROM classic.raw_customers")
        db.execute('INSERT INTO RAW.RAW_ORDERS SELECT CAST(id AS VARCHAR), CAST(user_id AS VARCHAR), CAST(order_date AS TIMESTAMP), NULL, NULL, NULL, NULL FROM classic.raw_orders')


def execute_dataset(directory, reference, dataset):
    verify_pins()
    directory.mkdir(parents=True)
    database = directory / 'reference.duckdb'
    _load_inputs(database, 'empty' if dataset == 'original-seeds' else dataset)
    project = directory / reference
    shutil.copytree(REFERENCES / reference, project)
    artifacts = []
    error = None
    if reference == 'classic':
        _profile(project, database, 'jaffle_shop', 'classic')
        if dataset != 'original-seeds':
            _classic_inputs(project, database)
            # Stable physical input types, including empty datasets and null IDs.
            configuration = yaml.safe_load((project / 'dbt_project.yml').read_text())
            configuration['seeds']['jaffle_shop'] = {
                'raw_customers': {'+column_types': {'id': 'varchar', 'first_name': 'varchar', 'last_name': 'varchar'}},
                'raw_orders': {'+column_types': {'id': 'varchar', 'user_id': 'varchar', 'order_date': 'date', 'status': 'varchar'}},
                'raw_payments': {'+column_types': {'id': 'varchar', 'order_id': 'varchar', 'payment_method': 'varchar', 'amount': 'double'}}}
            (project / 'dbt_project.yml').write_text(yaml.safe_dump(configuration))
        error, evidence = _command(project, database, f'reference-classic-{dataset}-seed', 'seed')
        artifacts.append(evidence)
        if error is None:
            if dataset != 'original-seeds':
                _restore_classic_inputs(database)
            error, evidence = _command(project, database, f'reference-classic-{dataset}-run', 'run')
            artifacts.append(evidence)
        if error is None and dataset == 'original-seeds':
            _seed_generated_classic(database)
    else:
        # Bounded dependency closure; no upstream project/package-wide run claim.
        (project / 'dbt_project.yml').write_text('''name: reference_modern
version: '1.0'
config-version: 2
profile: reference_modern
model-paths: [models]
macro-paths: [macros]
models:
  reference_modern:
    +materialized: table
''')
        (project / 'packages.yml').write_text("packages:\n  - local: '../dbt_utils'\n")
        shutil.copytree(REFERENCES / 'dbt_utils', directory / 'dbt_utils')
        _profile(project, database, 'reference_modern', 'modern')
        error, evidence = _command(project, database, f'reference-modern-{dataset}-deps', 'deps')
        artifacts.append(evidence)
        if error is None:
            error, evidence = _command(project, database, f'reference-modern-{dataset}-run', 'run')
            artifacts.append(evidence)
    generated = directory / 'generated'
    _, _, _, _, manifest = convert_to(generated)
    generated_error, evidence = _command(generated, database, f'generated-{reference}-{dataset}', 'run')
    artifacts.append(evidence)
    aliases = {entry['target'].split('/')[-1]: entry['alias'] for entry in manifest['outcomes']}
    input_id, input_manifest = retain_inputs(database, reference, dataset)
    return {'database': database, 'reference': reference, 'dataset': dataset, 'aliases': aliases,
            'reference_error': error, 'generated_error': generated_error, 'artifacts': artifacts,
            'input_id': input_id, 'input_manifest': input_manifest}


def output(db, sql):
    cursor = db.execute(sql)
    return {'columns': [str(column[0]) for column in cursor.description],
            'types': [str(column[1]) for column in cursor.description], 'rows': cursor.fetchall()}


def canonical_table(table):
    """Order-independent input identity, retaining duplicates and physical schema."""
    rows = Counter(json.dumps([_value(value, False) for value in row], separators=(',', ':'))
                   for row in table['rows'])
    return {'columns': table['columns'], 'types': table['types'],
            'rows': [{'values': json.loads(row), 'count': count} for row, count in sorted(rows.items())]}


def retain_inputs(database, reference, dataset):
    from .conftest import RUN
    generated = ['RAW.RAW_' + name for name in ['CUSTOMERS', 'ORDERS', 'PRODUCTS', 'SUPPLIES']]
    consumed = (['classic.raw_' + name for name in ['customers', 'orders', 'payments']]
                if reference == 'classic' else generated + ['RAW.RAW_ITEMS'])
    with duckdb.connect(str(database)) as db:
        sides = {side: {name: canonical_table(output(db, 'SELECT * FROM ' + name)) for name in names}
                 for side, names in [('generated', generated), ('reference', consumed)]}
    content = {'reference': reference, 'dataset': dataset, 'sides': sides,
               'adaptations': ('original classic seeds; generated ID/name/date bridge; no inferred payment amounts'
                               if dataset == 'original-seeds' else
                               'typed post-seed classic source restoration; NAME->first_name; day-level order_date; empty payments'
                               if reference == 'classic' else
                               'shared typed RAW inputs; supplemental RAW_ITEMS; bounded upstream dependency closure')}
    input_hash = hashlib.sha256(json.dumps(content, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    identity = f'{reference}:{dataset}:consumed-inputs-sha256:{input_hash}'
    destination = ROOT / 'reports/evidence' / f'{RUN}-inputs-{reference}-{dataset}.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(content | {'input_id': identity}, indent=2) + '\n')
    return identity, str(destination.relative_to(ROOT))


def _value(value, normalize):
    if normalize and isinstance(value, (int, float, Decimal)) and not isinstance(value, bool):
        # Decimal keys compare exactly, without context-dependent normalize()
        # rounding. Decimal also treats numerically equal signed zeros equally.
        return ('number', Decimal(str(value)))
    if normalize and isinstance(value, (date, datetime)):
        return ('date', str(value.date() if isinstance(value, datetime) else value))
    return (type(value).__name__, str(value))


def compare(reference, generated, *, normalized=False):
    """No set conversion: duplicate multiplicity contributes to overlap and rates."""
    names_equal = [x.upper() for x in reference['columns']] == [x.upper() for x in generated['columns']]
    types_equal = reference['types'] == generated['types']
    compatible = names_equal and (normalized or types_equal)
    left = Counter(tuple(_value(value, normalized) for value in row) for row in reference['rows'])
    right = Counter(tuple(_value(value, normalized) for value in row) for row in generated['rows'])
    overlap = sum((left & right).values()) if compatible else 0
    maximum = max(len(reference['rows']), len(generated['rows']))
    matched = compatible and left == right
    return {'comparison_status': 'matched' if matched else 'different', 'overlap_rows': overlap,
            'max_rows': maximum, 'reference_rows': len(reference['rows']), 'generated_rows': len(generated['rows']),
            'schema_compatible': compatible, 'physical_types_equal': types_equal,
            'row_agreement_pct': 100 * overlap / maximum if maximum else (100.0 if compatible else None)}


# Queries name only explicit shared fields; no swapping money columns or filtering.
MODERN_PROJECTIONS = {
    ('STG_CUSTOMERS', 'field_mapping'): ('customer_id, customer_name', 'CUSTOMER_ID, CUSTOMER_NAME'),
    ('STG_ORDERS', 'field_mapping'): ('order_id, customer_id, location_id', 'ORDER_ID, CUSTOMER_ID, LOCATION_ID'),
    ('STG_ORDERS', 'arithmetic'): ('order_id, subtotal, tax_paid, order_total', 'ORDER_ID, SUBTOTAL, TAX_PAID, ORDER_TOTAL'),
    ('STG_ORDERS', 'dates'): ('order_id, ordered_at AS ORDERED_AT_DAY', 'ORDER_ID, ORDERED_AT_DAY'),
    ('STG_PRODUCTS', 'arithmetic'): ('product_id, product_price', 'PRODUCT_ID, PRODUCT_PRICE'),
    ('STG_PRODUCTS', 'text_conditions'): ('product_id, CAST(is_food_item AS INTEGER) AS IS_FOOD_ITEM, CAST(is_drink_item AS INTEGER) AS IS_DRINK_ITEM', 'PRODUCT_ID, CAST(IS_FOOD_ITEM AS INTEGER) AS IS_FOOD_ITEM, CAST(IS_DRINK_ITEM AS INTEGER) AS IS_DRINK_ITEM'),
    ('STG_SUPPLIES', 'joins'): ('supply_id, product_id, supply_name, supply_cost', 'SUPPLY_ID, PRODUCT_ID, SUPPLY_NAME, SUPPLY_COST'),
    ('STG_SUPPLIES', 'text_conditions'): ('supply_id, is_perishable_supply AS IS_PERISHABLE', 'SUPPLY_ID, IS_PERISHABLE'),
    ('CUSTOMERS', 'joins'): ('customer_id, customer_name', 'CUSTOMER_ID, CUSTOMER_NAME'),
    ('CUSTOMERS', 'aggregation'): ('customer_id, count_lifetime_orders AS LIFETIME_ORDERS, lifetime_spend', 'CUSTOMER_ID, LIFETIME_ORDERS, LIFETIME_SPEND'),
    ('CUSTOMERS', 'dates'): ('customer_id, first_ordered_at AS FIRST_ORDER_DATE, last_ordered_at AS LAST_ORDER_DATE', 'CUSTOMER_ID, FIRST_ORDER_DATE, LAST_ORDER_DATE'),
}
CLASSIC_PROJECTIONS = {
    ('STG_CUSTOMERS', 'field_mapping'): ('CAST(customer_id AS VARCHAR) AS CUSTOMER_ID, first_name AS CUSTOMER_NAME', 'CUSTOMER_ID, CUSTOMER_NAME'),
    ('STG_ORDERS', 'field_mapping'): ('CAST(order_id AS VARCHAR) AS ORDER_ID, CAST(customer_id AS VARCHAR) AS CUSTOMER_ID', 'ORDER_ID, CUSTOMER_ID'),
    ('STG_ORDERS', 'dates'): ('CAST(order_id AS VARCHAR) AS ORDER_ID, order_date AS ORDERED_AT_DAY', 'ORDER_ID, ORDERED_AT_DAY'),
    ('CUSTOMERS', 'joins'): ('CAST(customer_id AS VARCHAR) AS CUSTOMER_ID', 'CUSTOMER_ID'),
    ('CUSTOMERS', 'aggregation'): ('CAST(customer_id AS VARCHAR) AS CUSTOMER_ID, number_of_orders AS LIFETIME_ORDERS', 'CUSTOMER_ID, LIFETIME_ORDERS'),
}

RULE_DIFFERENCES = {
    'STG_CUSTOMERS': 'XML Oracle storage boundaries convert empty strings to NULL; modern SQL passes raw NAME/ID. Classic has separate first_name/last_name columns.',
    'STG_ORDERS': 'XML connectors cross cents/dollar outputs; DD-MM-YY round trip uses current century. Modern keeps source cents and truncates original date. Classic has order_date/status and no equivalent amounts/location.',
    'STG_PRODUCTS': 'XML crosses price connectors, adds cents, trims/uppercases type and writes numeric flags; modern has one scaled price and literal lowercase boolean flags.',
    'STG_SUPPLIES': 'XML inner-joins products (drops unmatched/multiplies duplicate keys), adds cost cents and maps Y/1 to numeric flags; modern has no product join, adds supply_uuid and passes through perishable.',
    'CUSTOMERS': 'XML preserves grouped-order detail, counts nonnull order IDs and replaces null metrics with zero; modern preserves customer rows and counts distinct IDs; classic also preserves customers. XML money/date staging differences propagate.',
}


def comparison_cases():
    cases = []
    for reference in ['modern', 'classic']:
        for dataset in DATASETS + (['original-seeds'] if reference == 'classic' else []):
            for target in TARGETS:
                cases.append((reference, dataset, target, 'complete_target', 'complete'))
            for target, aspect in (MODERN_PROJECTIONS if reference == 'modern' else CLASSIC_PROJECTIONS):
                cases.append((reference, dataset, target, aspect, 'projection-normalized-values'))
    return cases


def measure(execution, target, aspect, scope):
    reference = execution['reference']
    dataset = execution['dataset']
    classification = 'execution_error'
    record = {'reference': reference, 'reference_revision': PINS[reference]['revision'], 'dataset': dataset,
              'target': (CORE if target == 'CUSTOMERS' else STAGING) + target, 'aspect': aspect, 'scope': scope,
              'artifacts': execution['artifacts'], 'classification': classification,
              'input_manifest': execution.get('input_manifest'),
              'effect_scope': 'end-to-end combined effects',
              'aspect_note': ('Customer counts/spend include upstream money wiring, source storage and join effects; not isolated aggregation accuracy'
                              if target == 'CUSTOMERS' and aspect == 'aggregation' else
                              'Join projection includes upstream values/storage and row multiplicity; not isolated join accuracy'
                              if aspect == 'joins' else
                              'Complete pipeline output on the declared fields/scope; not isolated operator accuracy'),
              'source_evidence': ['fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml',
                                  'research/07-reference-version-correlation.md'],
              'candidate_rule_evidence': RULE_DIFFERENCES[target],
              'comparison_status': 'error', 'row_agreement_pct': None, 'overlap_rows': None, 'max_rows': None}
    if reference == 'classic' and target in ['STG_PRODUCTS', 'STG_SUPPLIES']:
        return record | {'comparison_status': 'non_comparable', 'classification': 'missing_reference_counterpart',
                         'reason': 'Classic has no products/supplies model or input schema'}
    if reference == 'classic' and dataset == 'original-seeds' and target == 'STG_CUSTOMERS' and scope != 'complete':
        # Only this seed bridge combines first and last name; generated raw data
        # uses that exact combined value. The source SQL remains unchanged.
        projection = ('CAST(customer_id AS VARCHAR) AS CUSTOMER_ID, first_name || \' \' || last_name AS CUSTOMER_NAME', 'CUSTOMER_ID, CUSTOMER_NAME')
    else:
        projection = (MODERN_PROJECTIONS if reference == 'modern' else CLASSIC_PROJECTIONS).get((target, aspect))
    if execution['reference_error'] or execution['generated_error']:
        return record | {'reason': f'reference={execution["reference_error"]}; generated={execution["generated_error"]}'}
    rrelation = f'{reference}.{target.lower()}'
    grelation = f'converted."{execution["aliases"][target]}"'
    rsql, gsql = f'SELECT * FROM {rrelation}', f'SELECT * FROM {grelation}'
    if scope != 'complete':
        rsql, gsql = f'SELECT {projection[0]} FROM {rrelation}', f'SELECT {projection[1]} FROM {grelation}'
    try:
        with duckdb.connect(str(execution['database'])) as db:
            left, right = output(db, rsql), output(db, gsql)
    except duckdb.Error as exc:
        return record | {'reason': str(exc), 'reference_query': rsql, 'generated_query': gsql}
    result = compare(left, right, normalized=scope != 'complete')
    return record | result | {'classification': 'agreement_on_declared_scope' if result['comparison_status'] == 'matched' else 'observed_unresolved_reference_difference',
                             'reference_query': rsql, 'generated_query': gsql,
                             'reference_output': left, 'generated_output': right}
