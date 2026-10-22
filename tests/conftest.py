"""Actual pytest outcomes; append all invocations, including failed reruns."""
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import uuid

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUN = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:6]
ROWS = []
COLLECTION_FAILURES = []
RUN_FAILURES = []
COLLECTION_ROOT = ROOT


def fingerprint():
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    digest = hashlib.sha256()
    paths = [*ROOT.glob('src/**/*.py'), *ROOT.glob('tests/**/*.py'), *ROOT.glob('examples/*'),
             *ROOT.glob('scripts/*.py'), *ROOT.glob('fixtures/references/**/*'),
             ROOT / 'pyproject.toml', ROOT / 'uv.lock', *ROOT.glob('.github/workflows/*')]
    for path in sorted(p for p in paths if p.is_file()):
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(path.read_bytes())
    return revision + '+code-sha256:' + digest.hexdigest()


REVISION = fingerprint()
FIXTURE_HASH = hashlib.sha256((ROOT / 'fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml').read_bytes()).hexdigest()
ENVIRONMENT = ';'.join([f'Python={platform.python_version()}', f'platform={platform.system()}-{platform.machine()}',
                        *[f'{p}={importlib.metadata.version(p)}' for p in ['pytest', 'duckdb', 'dbt-core', 'dbt-duckdb']]])


def pytest_configure(config):
    global COLLECTION_ROOT
    COLLECTION_ROOT = config.rootpath
    config.addinivalue_line('markers', 'result(target): complete independent result comparison')
    config.addinivalue_line('markers', 'lifecycle: actual dbt preparation lifecycle')
    config.addinivalue_line('markers', 'mutation: changed supported XML behavior')
    config.addinivalue_line('markers', 'negative: explicit rejected input')
    config.addinivalue_line('markers', 'boundary: controlled semantic boundary')
    config.addinivalue_line('markers', 'reference: executed pinned reference comparison; test pass is not agreement')
    config.addinivalue_line('markers', 'reference_execution: original reference project execution')


@pytest.fixture(autouse=True)
def input_identity(request):
    if request.node.path.name == 'test_semantics.py':
        source_hash = hashlib.sha256(Path(str(request.node.path)).read_bytes()).hexdigest()
        request.node.actual_input_id = 'inline-scalar:' + request.node.nodeid + ':test-source-sha256:' + source_hash
    elif request.node.name == 'test_installed_cli_help':
        request.node.actual_input_id = 'no-XML:installed-CLI-help'
    elif hasattr(request.node, 'callspec') and 'payload' in request.node.callspec.params:
        payload = request.node.callspec.params['payload']
        request.node.actual_input_id = 'inline-XML:sha256:' + hashlib.sha256(payload).hexdigest()


def _reference_metadata(item, detail):
    reference = getattr(item, 'reference_comparison', None)
    execution = getattr(item, 'reference_execution', None)
    marker = item.get_closest_marker('reference')
    baseline = item.get_closest_marker('reference_execution')
    if reference is None and marker:
        parameters = item.callspec.params
        from .reference_support import PINS
        reference = {key: parameters[key] for key in ['reference', 'dataset', 'target', 'aspect', 'scope']}
        reference.update(reference_revision=PINS[parameters['reference']]['revision'],
                         comparison_status='error', row_agreement_pct=None,
                         overlap_rows=None, max_rows=None, reason=detail,
                         effect_scope='end-to-end combined effects',
                         aspect_note='Preparation failed; no operator accuracy is measured')
    if execution is None and baseline:
        from .reference_support import PINS
        name = baseline.kwargs.get('reference', 'classic')
        execution = {'reference': name, 'reference_revision': PINS[name]['revision'],
                     'dataset': baseline.kwargs.get('dataset', 'original-seeds'),
                     'execution_status': 'error', 'reason': detail}
    return reference, execution


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()
    if not (report.when == 'call' or (report.when == 'setup' and report.outcome != 'passed')
            or (report.when == 'teardown' and report.failed)):
        return
    marker = item.get_closest_marker('result')
    category = 'result' if marker else next((name for name in ['lifecycle', 'mutation', 'negative', 'boundary'] if item.get_closest_marker(name)), 'unit')
    status = 'error' if report.when != 'call' and report.failed else {'passed': 'passed', 'failed': 'failed', 'skipped': 'skipped'}[report.outcome]
    detail = 'Complete expected columns, values and duplicate counts match' if marker and report.passed else report.outcome
    if report.failed or report.skipped:
        detail = str(report.longrepr).splitlines()[-1][:500]
    reference, execution = _reference_metadata(item, detail)
    record = reference if reference is not None else execution
    case_id = report.nodeid
    target = marker.kwargs.get('target', '') if marker else ''
    evidence_path = f'reports/evidence/{RUN}.txt'
    if report.when == 'teardown':
        # A teardown error is an additional lifecycle event, never a second
        # measurement. Keep the original call/setup evidence file immutable.
        category = 'lifecycle-error'
        case_id += '::teardown'
        record = {key: record[key] for key in ['reference', 'reference_revision', 'dataset', 'target', 'aspect', 'scope'] if record and key in record}
        record.update(phase='teardown', reason=detail)
    elif record is not None:
        category = 'reference-comparison' if reference is not None else 'reference-execution'
    if record is not None:
        record = dict(record)
        target = record.get('target', '')
        identity = hashlib.sha256(case_id.encode()).hexdigest()[:16]
        evidence_path = f'reports/evidence/{RUN}-{category}-{identity}.json'
        record.update(run_id=RUN, revision=REVISION, environment=ENVIRONMENT,
                      case_id=case_id, phase=report.when, status=status,
                      input_id=getattr(item, 'actual_input_id', 'unavailable:preparation-failed'))
        destination = ROOT / evidence_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(record, indent=2, default=str) + '\n')
        detail = json.dumps({key: value for key, value in record.items()
                             if key not in ['reference_output', 'generated_output']}, default=str)
    ROWS.append({'run_id': RUN, 'utc': datetime.now(timezone.utc).isoformat(), 'revision': REVISION,
                 'stage': 'reference-validation' if reference is not None or execution is not None else 'basic-build',
                 'environment': ENVIRONMENT, 'case_id': case_id, 'test_type': category,
                 'input_id': getattr(item, 'actual_input_id', 'unavailable:preparation-failed' if record is not None else 'FLOWLINE_DEMO_JAFFLESHOP.xml:sha256:' + FIXTURE_HASH),
                 'target': target, 'status': status, 'detail': detail, 'evidence': evidence_path})
    evidence = ROOT / 'reports/evidence' / (RUN + '.txt')
    evidence.parent.mkdir(parents=True, exist_ok=True)
    with evidence.open('a') as stream:
        stream.write(f'{case_id} [{report.when}]: {status}\n')
        if report.failed or report.skipped:
            stream.write(str(report.longrepr) + '\n')


def pytest_collectreport(report):
    if report.failed:
        node_path = Path(report.nodeid.split("::")[0])
        if not node_path.is_absolute():
            node_path = COLLECTION_ROOT / node_path
        identity = 'collection:' + report.nodeid
        if node_path.is_file():
            identity += ':sha256:' + hashlib.sha256(node_path.read_bytes()).hexdigest()
        COLLECTION_FAILURES.append(identity)
        evidence = ROOT / 'reports/evidence' / (RUN + '.txt')
        evidence.parent.mkdir(parents=True, exist_ok=True)
        with evidence.open('a') as stream:
            stream.write(f'{report.nodeid} [collection]: error\n{report.longrepr}\n')


def pytest_internalerror(excrepr):
    RUN_FAILURES.append(str(excrepr))


def pytest_sessionfinish(session, exitstatus):
    path = ROOT / 'reports/test-runs.csv'
    fields = ['run_id', 'utc', 'revision', 'stage', 'environment', 'case_id', 'test_type', 'input_id', 'target', 'status', 'detail', 'evidence']
    # Invocation records are explicitly separate from individual test cases.
    # A collection failure can otherwise produce a header with zero outcomes.
    case_records = sum(row['test_type'] != 'lifecycle-error' for row in ROWS)
    ROWS.append({'run_id': RUN, 'utc': datetime.now(timezone.utc).isoformat(), 'revision': REVISION,
                 'stage': 'basic-build', 'environment': ENVIRONMENT, 'case_id': '__pytest_invocation__',
                 'test_type': 'run', 'input_id': ';'.join(COLLECTION_FAILURES) or 'pytest-invocation',
                 'target': '', 'status': 'passed' if int(exitstatus) == 0 else 'error',
                 'detail': f'exit_status={int(exitstatus)}; collected={session.testscollected}; test_case_records={case_records}; collection_failures={len(COLLECTION_FAILURES)}; internal_errors={len(RUN_FAILURES)}; lifecycle_errors={sum(row["test_type"] == "lifecycle-error" for row in ROWS)}',
                 'evidence': f'reports/evidence/{RUN}.txt'})
    exists = path.exists()
    with path.open('a', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerows(ROWS)
    evidence = ROOT / 'reports/evidence' / (RUN + '.txt')
    evidence.parent.mkdir(parents=True, exist_ok=True)
    with evidence.open('a') as stream:
        for failure in RUN_FAILURES:
            stream.write(f'[internal error]: {failure}\n')
        stream.write(f'command: uv run pytest {" ".join(session.config.invocation_params.args)}\nrevision: {REVISION}\nenvironment: {ENVIRONMENT}\nexit status: {exitstatus}\n')


@pytest.fixture(scope='session')
def root():
    return ROOT
