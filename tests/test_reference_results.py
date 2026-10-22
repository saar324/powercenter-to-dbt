"""Actual dbt reference results, including deliberately observed differences."""
import csv
import json

import duckdb
import pytest

from .conftest import ROOT, RUN
from .reference_support import (PINS, REFERENCES, comparison_cases, execute_dataset,
                                measure, verify_pins)


@pytest.fixture(scope='module')
def reference_executions(tmp_path_factory):
    directory = tmp_path_factory.mktemp('pinned-references')
    cache = {}

    def get(reference, dataset):
        key = (reference, dataset)
        if key not in cache:
            cache[key] = execute_dataset(directory / f'{reference}-{dataset}', reference, dataset)
        return cache[key]
    return get


def test_reference_pins_are_unchanged():
    verify_pins()
    assert PINS['modern']['revision'] == 'f8f89f8d8af66ce3dd20844d41836cd5deac3f1c'
    assert 'No LICENSE' in PINS['modern']['license']


@pytest.mark.reference_execution(reference='classic', dataset='original-seeds')
def test_classic_original_project_seed_baseline(reference_executions, request):
    execution = reference_executions('classic', 'original-seeds')
    request.node.actual_input_id = execution['input_id']
    request.node.reference_execution = {'reference': 'classic', 'dataset': 'original-seeds',
                                        'reference_revision': PINS['classic']['revision'],
                                        'input_manifest': execution['input_manifest'],
                                        'artifacts': execution['artifacts']}
    assert execution['reference_error'] is None, execution
    assert execution['generated_error'] is None, execution
    # Check original seed cardinalities independently of the reference models.
    with duckdb.connect(str(execution['database'])) as db:
        for name in ['customers', 'orders', 'payments']:
            with (REFERENCES / f'classic/seeds/raw_{name}.csv').open() as stream:
                expected = len(list(csv.DictReader(stream)))
            assert db.execute(f'SELECT COUNT(*) FROM classic.raw_{name}').fetchone()[0] == expected
        assert db.execute('SELECT COUNT(*) FROM classic.customers').fetchone()[0] == 100


def expected_disposition(reference, dataset, target, aspect, scope):
    """Independent rule-derived matrix, never inferred from the observed result.

    Complete shapes/types differ except modern clean customer staging. Empty
    projections share schema. Edge XML storage turns '' into NULL while each
    reference now receives the actual typed raw ''. Classic order ID/customer
    fields contain no empty strings and still match; modern also compares the
    empty location ID, which differs after XML storage conversion.
    Modern ordinary differences follow crossed money connectors and Y/text flags;
    customer spend includes those upstream effects. Classic original idle-customer
    preservation differs from XML order-detail preservation.
    """
    if reference == 'classic' and target in ['STG_PRODUCTS', 'STG_SUPPLIES']:
        return 'non_comparable'
    if scope == 'complete':
        return 'matched' if reference == 'modern' and target == 'STG_CUSTOMERS' and dataset != 'edge' else 'different'
    if dataset == 'empty':
        return 'matched'
    if dataset == 'edge':
        return 'matched' if reference == 'classic' and target == 'STG_ORDERS' and aspect == 'field_mapping' else 'different'
    if reference == 'classic':
        return 'different' if dataset == 'original-seeds' and target == 'CUSTOMERS' else 'matched'
    different = {('STG_ORDERS', 'arithmetic'), ('STG_PRODUCTS', 'arithmetic'),
                 ('STG_SUPPLIES', 'text_conditions'), ('CUSTOMERS', 'aggregation')}
    return 'different' if (target, aspect) in different else 'matched'


def test_classic_typed_bridge_preserves_null_and_empty(reference_executions):
    execution = reference_executions('classic', 'edge')
    with duckdb.connect(str(execution['database'])) as db:
        assert db.execute("SELECT COUNT(*) FROM classic.raw_customers WHERE id = '' AND first_name = ''").fetchone() == (1,)
        assert db.execute('SELECT COUNT(*) FROM classic.raw_customers WHERE id IS NULL').fetchone() == (1,)
        assert db.execute("SELECT COUNT(*) FROM classic.raw_orders WHERE id IS NULL AND user_id IS NULL").fetchone() == (1,)
        assert db.execute("SELECT COUNT(*) FROM classic.stg_customers WHERE customer_id = '' AND first_name = ''").fetchone() == (1,)


@pytest.mark.parametrize('reference,dataset,target,aspect,scope', comparison_cases(), ids=lambda x: x)
@pytest.mark.reference
def test_executed_reference_comparison(reference_executions, request, reference, dataset, target, aspect, scope):
    execution = reference_executions(reference, dataset)
    request.node.actual_input_id = execution['input_id']
    record = measure(execution, target, aspect, scope)
    request.node.reference_comparison = record
    assert record['comparison_status'] == expected_disposition(reference, dataset, target, aspect, scope), record
    if record['comparison_status'] in ['matched', 'different']:
        assert 'reference_output' in record and 'generated_output' in record
        assert record['overlap_rows'] <= record['max_rows']
