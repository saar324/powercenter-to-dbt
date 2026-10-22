"""Independent arithmetic/reporting checks, not external equivalence claims."""
import importlib.util
import json

from .conftest import ROOT
from .reference_support import compare, measure

spec = importlib.util.spec_from_file_location('summarize_accuracy', ROOT / 'scripts/summarize_accuracy.py')
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)


def row(status, overlap=None, maximum=None, *, aspect='joins', scope='complete', dataset='edge'):
    return {'run_id': 'unit-run', 'test_type': 'reference-comparison', 'revision': 'unit-snapshot',
            'environment': 'unit', 'evidence': 'unit-only', 'status': 'passed',
            'detail': json.dumps({'reference': 'unit', 'reference_revision': 'pin', 'dataset': dataset,
                                 'aspect': aspect, 'scope': scope, 'comparison_status': status,
                                 'overlap_rows': overlap, 'max_rows': maximum})}


def result(rows, types=None):
    return {'columns': ['ID'], 'types': types or ['VARCHAR'], 'rows': rows}


def test_duplicate_overlap_uses_multisets_and_maximum_per_case():
    measured = compare(result([('a',), ('a',), ('b',)]), result([('a',), ('b',), ('b',), ('b',)]))
    assert measured['comparison_status'] == 'different'
    assert measured['overlap_rows'] == 2 and measured['max_rows'] == 4
    assert measured['row_agreement_pct'] == 50


def test_schema_and_type_mismatch_are_not_empty_agreement():
    measured = compare(result([], ['INTEGER']), result([], ['VARCHAR']))
    assert measured['comparison_status'] == 'different'
    assert measured['row_agreement_pct'] is None
    assert compare(result([]), result([]))['row_agreement_pct'] == 100


def test_case_denominator_includes_errors_but_exposes_exclusions():
    measured = summary.aggregate([row('matched', 2, 2), row('different', 1, 3), row('error'),
                                  row('unsupported'), row('non_comparable')])[0]
    assert measured['compared_cases'] == 3
    assert measured['matched'] == measured['different'] == measured['errors'] == 1
    assert measured['unsupported'] == measured['non_comparable'] == 1
    assert measured['case_agreement_pct'] == 100 / 3
    assert measured['row_agreement_pct'] == 60
    assert measured['overlap_rows'] == 3 and measured['maximum_rows'] == 5
    assert measured['row_cases'] == 2


def test_no_rate_for_zero_denominator_or_execution_error():
    excluded = summary.aggregate([row('unsupported'), row('non_comparable')])[0]
    assert excluded['compared_cases'] == 0 and excluded['case_agreement_pct'] == ''
    assert excluded['row_agreement_pct'] == ''
    error = summary.aggregate([row('error')])[0]
    assert error['case_agreement_pct'] == 0 and error['row_agreement_pct'] == ''
    empty = summary.aggregate([row('matched', 0, 0)])[0]
    assert empty['case_agreement_pct'] == 100 and empty['row_agreement_pct'] == ''


def test_overlapping_aspects_scopes_and_datasets_are_never_one_score():
    records = [row('matched', 1, 1), row('different', 0, 1, aspect='arithmetic'),
               row('matched', 1, 1, scope='projection'), row('matched', 1, 1, dataset='ordinary')]
    assert len(summary.aggregate(records)) == 4
    assert summary.aggregate(records, 'another-run') == []
    assert summary.aggregate([records[0] | {'test_type': 'unit'}]) == []


def test_complete_type_equality_is_separate_from_normalized_projection():
    left, right = result([(1,)], ['BIGINT']), result([(1.0,)], ['DOUBLE'])
    assert compare(left, right)['comparison_status'] == 'different'
    projected = compare(left, right, normalized=True)
    assert projected['comparison_status'] == 'matched' and not projected['physical_types_equal']


def test_failed_execution_cannot_be_an_empty_match():
    execution = {'reference': 'modern', 'dataset': 'empty', 'reference_error': 'runtime unavailable',
                 'generated_error': None, 'artifacts': []}
    measured = measure(execution, 'STG_CUSTOMERS', 'complete_target', 'complete')
    assert measured['comparison_status'] == 'error'
    assert measured['row_agreement_pct'] is None and measured['max_rows'] is None


def test_missing_relation_records_schema_execution_error(tmp_path):
    execution = {'reference': 'modern', 'dataset': 'empty', 'reference_error': None,
                 'generated_error': None, 'artifacts': [], 'database': tmp_path / 'missing.duckdb',
                 'aliases': {'STG_CUSTOMERS': 'missing'}}
    measured = measure(execution, 'STG_CUSTOMERS', 'complete_target', 'complete')
    assert measured['comparison_status'] == 'error'
    assert measured['row_agreement_pct'] is None and 'reason' in measured


def test_exact_high_precision_keys_and_signed_zeros():
    from decimal import Decimal
    for left, right in [('12345678901234567890123456781', '12345678901234567890123456782'),
                        ('12345678901234567890123456789012345671', '12345678901234567890123456789012345672')]:
        measured = compare(result([(Decimal(left),)], ['DECIMAL(38,0)']),
                           result([(Decimal(right),)], ['DECIMAL(38,0)']), normalized=True)
        assert measured['comparison_status'] == 'different' and measured['overlap_rows'] == 0
    for left, right in [('0', '-0'), ('-0.000', '0.0')]:
        assert compare(result([(Decimal(left),)]), result([(Decimal(right),)]), normalized=True)['comparison_status'] == 'matched'


def test_canonical_input_rows_preserve_duplicates_and_schema():
    from .reference_support import canonical_table
    first = canonical_table(result([('b',), ('a',), ('a',)]))
    assert first == canonical_table(result([('a',), ('b',), ('a',)]))
    assert first != canonical_table(result([('a',), ('b',)]))
    assert first != canonical_table(result([('b',), ('a',), ('a',)], ['TEXT']))
    renamed = result([('b',), ('a',), ('a',)]) | {'columns': ['OTHER']}
    assert first != canonical_table(renamed)
    assert canonical_table(result([(None,), ('',)])) != canonical_table(result([(None,), (None,)]))


def test_input_manifest_includes_classic_payments_and_both_schemas(tmp_path, monkeypatch):
    import duckdb
    from . import reference_support as support
    monkeypatch.setattr(support, 'ROOT', tmp_path)
    database = tmp_path / 'inputs.duckdb'
    with duckdb.connect(str(database)) as db:
        db.execute('CREATE SCHEMA RAW; CREATE SCHEMA classic')
        for name in ['CUSTOMERS', 'ORDERS', 'PRODUCTS', 'SUPPLIES']:
            db.execute(f'CREATE TABLE RAW.RAW_{name} (ID VARCHAR)')
        for name in ['customers', 'orders', 'payments']:
            db.execute(f'CREATE TABLE classic.raw_{name} (ID VARCHAR)')
        db.execute("INSERT INTO classic.raw_payments VALUES ('p1')")
    first, location = support.retain_inputs(database, 'classic', 'edge')
    manifest = json.loads((tmp_path / location).read_text())
    assert 'classic.raw_payments' in manifest['sides']['reference']
    assert 'RAW.RAW_CUSTOMERS' in manifest['sides']['generated']
    with duckdb.connect(str(database)) as db:
        db.execute("INSERT INTO classic.raw_payments VALUES ('p1')")
    assert support.retain_inputs(database, 'classic', 'edge')[0] != first


def _cli_history(tmp_path):
    """Synthetic isolated CLI inputs; never appended as real reference runs."""
    import csv
    import hashlib
    from .reference_support import PINS, comparison_cases
    fields = ['run_id', 'utc', 'revision', 'stage', 'environment', 'case_id', 'test_type', 'input_id', 'target', 'status', 'detail', 'evidence']
    history = tmp_path / 'history.csv'
    records = []

    def add(run, cases=None, *, invocation='passed', comparison_status='matched'):
        cases = comparison_cases() if cases is None else cases
        for index, (reference, dataset, target, aspect, scope) in enumerate(cases):
            content = {'reference': reference, 'dataset': dataset,
                       'sides': {'generated': {}, 'reference': {}}, 'adaptations': 'isolated CLI regression fixture'}
            digest = hashlib.sha256(json.dumps(content, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            identity = 'isolated-cli:sha256:' + digest
            manifest = tmp_path / f'{run}-{reference}-{dataset}-inputs.json'
            manifest.write_text(json.dumps(content | {'input_id': identity}))
            rowdata = {'run_id': run, 'utc': run, 'revision': 'isolated-snapshot', 'stage': 'unit-fixture',
                       'environment': 'isolated', 'case_id': f'{run}-case-{index}', 'test_type': 'reference-comparison',
                       'input_id': identity, 'target': target, 'status': 'passed'}
            record = {key: rowdata[key] for key in ['run_id', 'revision', 'environment', 'case_id', 'input_id', 'status']}
            record.update(reference=reference, reference_revision=PINS[reference]['revision'], dataset=dataset,
                          target=target, aspect=aspect, scope=scope, phase='call', input_manifest=str(manifest),
                          effect_scope='end-to-end combined effects', aspect_note='Not isolated operator accuracy',
                          comparison_status=comparison_status, overlap_rows=1 if comparison_status == 'matched' else None,
                          max_rows=1 if comparison_status == 'matched' else None,
                          row_agreement_pct=100 if comparison_status == 'matched' else None)
            if comparison_status == 'matched':
                record.update(reference_rows=1, generated_rows=1, schema_compatible=True, physical_types_equal=True,
                              reference_output=result([('a',)]), generated_output=result([('a',)]))
            evidence = tmp_path / f'{run}-case-{index}.json'
            evidence.write_text(json.dumps(record))
            records.append(rowdata | {'detail': json.dumps({key: value for key, value in record.items() if key not in ['reference_output', 'generated_output']}), 'evidence': str(evidence)})
        baseline = {'run_id': run, 'utc': run, 'revision': 'isolated-snapshot', 'stage': 'unit-fixture',
                    'environment': 'isolated', 'case_id': run + '-baseline', 'test_type': 'reference-execution',
                    'input_id': 'isolated', 'target': '', 'status': 'passed'}
        record = {key: baseline[key] for key in ['run_id', 'revision', 'environment', 'case_id', 'input_id', 'status']}
        record.update(reference='classic', reference_revision=PINS['classic']['revision'], dataset='original-seeds', phase='call')
        evidence = tmp_path / (run + '-baseline.json'); evidence.write_text(json.dumps(record))
        records.append(baseline | {'detail': json.dumps(record), 'evidence': str(evidence)})
        records.append(baseline | {'case_id': '__pytest_invocation__', 'test_type': 'run', 'status': invocation, 'detail': 'isolated invocation', 'evidence': 'unit-only'})
        with history.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader(); writer.writerows(records)
    return history, records, add


def _cli(history, output, *extra):
    import subprocess
    import sys
    return subprocess.run([sys.executable, str(ROOT / 'scripts/summarize_accuracy.py'),
                           '--input', str(history), '--output', str(output), *extra],
                          cwd=ROOT, capture_output=True, text=True, timeout=30)


def test_cli_selects_latest_successful_complete_run_and_explicit_partial(tmp_path):
    import csv
    from .reference_support import comparison_cases
    history, records, add = _cli_history(tmp_path)
    add('complete-1'); add('complete-2')
    add('later-unrelated', [])
    add('later-partial', comparison_cases()[:1])
    add('later-error', comparison_cases()[:1], invocation='error', comparison_status='error')
    destination = tmp_path / 'accuracy.csv'
    executed = _cli(history, destination)
    assert executed.returncode == 0, executed.stderr
    assert 'complete-2: complete-successful' in executed.stdout
    rows = list(csv.DictReader(destination.open()))
    assert {row['run_id'] for row in rows} == {'complete-2'}
    assert {row['actual_cases'] for row in rows} == {'88'}
    explicit = _cli(history, destination, '--run-id', 'complete-1')
    assert explicit.returncode == 0 and 'complete-1: complete-successful' in explicit.stdout
    partial = _cli(history, destination, '--run-id', 'later-partial')
    assert partial.returncode == 0 and 'partial-or-failed' in partial.stdout and '1/88' in partial.stdout
    rows = list(csv.DictReader(destination.open()))
    assert rows[0]['expected_cases'] == '88' and rows[0]['actual_cases'] == '1' and rows[0]['missing_cases'] == '87'
    error = _cli(history, destination, '--run-id', 'later-error')
    assert error.returncode == 0 and 'partial-or-failed' in error.stdout
    assert list(csv.DictReader(destination.open()))[0]['row_agreement_pct'] == ''


def test_cli_rejects_missing_contradictory_or_absent_evidence_without_overwrite(tmp_path):
    from .reference_support import comparison_cases
    history, records, add = _cli_history(tmp_path)
    add('only-partial', comparison_cases()[:1])
    destination = tmp_path / 'accuracy.csv'; destination.write_text('previous report\n')
    assert _cli(history, destination).returncode != 0
    assert destination.read_text() == 'previous report\n'
    evidence = __import__('pathlib').Path(records[0]['evidence'])
    original = evidence.read_text(); altered = json.loads(original); altered['overlap_rows'] = 0
    evidence.write_text(json.dumps(altered))
    assert _cli(history, destination, '--run-id', 'only-partial').returncode != 0
    assert destination.read_text() == 'previous report\n'
    evidence.unlink()
    assert _cli(history, destination, '--run-id', 'only-partial').returncode != 0
    assert destination.read_text() == 'previous report\n'
    assert _cli(history, destination, '--run-id', 'missing-run').returncode != 0
    assert destination.read_text() == 'previous report\n'


def test_real_pytest_reference_success_setup_and_teardown_are_distinct(tmp_path, request):
    import csv
    import hashlib
    import subprocess
    import sys
    module = tmp_path / 'test_reference_reporting_probe.py'
    module.write_text('''import pytest
from tests.reference_support import PINS

@pytest.fixture
def setup_error():
    raise RuntimeError('isolated reference setup failure')

@pytest.fixture
def teardown_error():
    yield
    raise RuntimeError('isolated reference teardown failure')

@pytest.mark.reference_execution(reference='classic', dataset='original-seeds')
def test_baseline_success(request):
    request.node.actual_input_id = 'isolated-baseline-input'
    request.node.reference_execution = {'reference': 'classic', 'dataset': 'original-seeds', 'reference_revision': PINS['classic']['revision']}

@pytest.mark.reference_execution(reference='classic', dataset='original-seeds')
def test_baseline_setup_failure(setup_error):
    pass

def record(request):
    request.node.actual_input_id = 'isolated-comparison-input'
    request.node.reference_comparison = {
        'reference': 'modern', 'reference_revision': PINS['modern']['revision'],
        'dataset': 'ordinary', 'target': 'STG_CUSTOMERS', 'aspect': 'field_mapping',
        'scope': 'projection-normalized-values', 'comparison_status': 'matched',
        'row_agreement_pct': 100, 'overlap_rows': 1, 'max_rows': 1,
        'reference_rows': 1, 'generated_rows': 1, 'schema_compatible': True,
        'physical_types_equal': True, 'effect_scope': 'end-to-end combined effects',
        'reference_output': {'columns': ['ID'], 'types': ['VARCHAR'], 'rows': [('a',)]},
        'generated_output': {'columns': ['ID'], 'types': ['VARCHAR'], 'rows': [('a',)]}}

parameters = pytest.mark.parametrize('reference,dataset,target,aspect,scope', [
    ('modern', 'ordinary', 'STG_CUSTOMERS', 'field_mapping', 'projection-normalized-values')])

@parameters
@pytest.mark.reference
def test_comparison_success(request, reference, dataset, target, aspect, scope):
    record(request)

@parameters
@pytest.mark.reference
def test_comparison_teardown(request, reference, dataset, target, aspect, scope, teardown_error):
    record(request)

@parameters
@pytest.mark.reference
def test_comparison_setup(reference, dataset, target, aspect, scope, setup_error):
    pass
''')
    request.node.actual_input_id = 'isolated-reference-reporting:sha256:' + hashlib.sha256(module.read_bytes()).hexdigest()
    report = ROOT / 'reports/test-runs.csv'
    before = {row['run_id'] for row in csv.DictReader(report.open())}
    result = subprocess.run([sys.executable, '-m', 'pytest', '--noconftest', '-p', 'tests.conftest', '-q', str(module)],
                            cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 1, result.stdout + result.stderr
    rows = [row for row in csv.DictReader(report.open()) if row['run_id'] not in before]
    assert len({row['run_id'] for row in rows}) == 1
    measurements = [row for row in rows if row['test_type'] == 'reference-comparison']
    assert len(measurements) == 3 and len({row['case_id'] for row in measurements}) == 3
    baseline_failure = next(row for row in rows if 'test_baseline_setup_failure' in row['case_id'])
    assert baseline_failure['test_type'] == 'reference-execution' and baseline_failure['status'] == 'error'
    metadata = json.loads((ROOT / baseline_failure['evidence']).read_text())
    assert metadata['reference'] == 'classic' and metadata['dataset'] == 'original-seeds'
    assert metadata['reference_revision'] and metadata['phase'] == 'setup'
    setup = next(row for row in measurements if 'test_comparison_setup' in row['case_id'])
    assert setup['status'] == 'error' and json.loads(setup['detail'])['comparison_status'] == 'error'
    teardown_measurement = next(row for row in measurements if 'test_comparison_teardown' in row['case_id'])
    assert teardown_measurement['status'] == 'passed'
    measured = json.loads((ROOT / teardown_measurement['evidence']).read_text())
    assert measured['comparison_status'] == 'matched' and measured['phase'] == 'call'
    assert measured['reference_output']['rows'] == [['a']]
    lifecycle = [row for row in rows if row['test_type'] == 'lifecycle-error']
    assert len(lifecycle) == 1 and lifecycle[0]['status'] == 'error'
    assert lifecycle[0]['case_id'].endswith('::teardown')
    assert lifecycle[0]['evidence'] != teardown_measurement['evidence']
    assert json.loads((ROOT / lifecycle[0]['evidence']).read_text())['phase'] == 'teardown'
    assert next(row for row in rows if row['test_type'] == 'run')['status'] == 'error'


def test_unequal_outputs_keep_cause_unresolved_and_label_combined_effects(tmp_path, monkeypatch):
    from . import reference_support as support
    outputs = iter([result([('a',)]), result([('b',)])])
    monkeypatch.setattr(support, 'output', lambda db, sql: next(outputs))
    execution = {'reference': 'modern', 'dataset': 'ordinary', 'reference_error': None,
                 'generated_error': None, 'artifacts': [], 'database': tmp_path / 'probe.duckdb',
                 'aliases': {'CUSTOMERS': 'customers'}}
    measured = support.measure(execution, 'CUSTOMERS', 'aggregation', 'projection-normalized-values')
    assert measured['comparison_status'] == 'different'
    assert measured['classification'] == 'observed_unresolved_reference_difference'
    assert measured['candidate_rule_evidence'] and measured['source_evidence']
    assert measured['effect_scope'] == 'end-to-end combined effects'
    assert 'upstream money' in measured['aspect_note'] and 'not isolated' in measured['aspect_note']


def test_cli_default_rejects_missing_complete_baseline_evidence(tmp_path):
    from pathlib import Path
    history, records, add = _cli_history(tmp_path)
    add('complete')
    Path(next(row['evidence'] for row in records if row['test_type'] == 'reference-execution')).unlink()
    destination = tmp_path / 'accuracy.csv'; destination.write_text('previous report\n')
    rejected = _cli(history, destination)
    assert rejected.returncode != 0 and destination.read_text() == 'previous report\n'
