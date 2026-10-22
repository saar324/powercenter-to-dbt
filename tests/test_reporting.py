"""Run-level reporting regression; execute a real isolated collection failure."""
import csv
import hashlib
from pathlib import Path
import subprocess
import sys

from .conftest import ROOT


def test_collection_failure_records_run_outcome_without_test_cases(tmp_path, request):
    broken = tmp_path / 'test_broken.py'
    payload = b'import missing_module_for_collection_regression\n'
    broken.write_bytes(payload)
    request.node.actual_input_id = 'inline-collection-module:sha256:' + hashlib.sha256(payload).hexdigest()
    report = ROOT / 'reports/test-runs.csv'
    previous_runs = {row['run_id'] for row in csv.DictReader(report.open())} if report.exists() else set()
    result = subprocess.run([sys.executable, '-m', 'pytest', '--noconftest', '-p', 'tests.conftest', '-q', str(broken)],
                            cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 2, result.stdout + result.stderr
    rows = [row for row in csv.DictReader(report.open()) if row['run_id'] not in previous_runs]
    assert len(rows) == 1, rows
    row = rows[0]
    assert row['test_type'] == 'run' and row['case_id'] == '__pytest_invocation__'
    assert row['status'] == 'error'
    assert 'test_case_records=0' in row['detail'] and 'collection_failures=1' in row['detail']
    assert hashlib.sha256(payload).hexdigest() in row['input_id']
    evidence = (ROOT / row['evidence']).read_text()
    assert 'missing_module_for_collection_regression' in evidence
    assert 'exit status: 2' in evidence
