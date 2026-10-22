"""Derive reference accuracy groups from actual pytest run records only."""
import argparse
from collections import defaultdict
import csv
import json
import math
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUP = ['run_id', 'reference', 'reference_revision', 'revision', 'dataset', 'aspect', 'scope', 'environment', 'effect_scope']
FIELDS = GROUP + ['matched', 'different', 'errors', 'unsupported', 'non_comparable', 'compared_cases',
                  'case_agreement_pct', 'overlap_rows', 'maximum_rows', 'row_cases', 'row_agreement_pct', 'aspect_note', 'run_completeness', 'expected_cases', 'actual_cases', 'missing_cases', 'invocation_status', 'baseline_status', 'lifecycle_errors', 'evidence']


def aggregate(rows, run_id=None):
    groups = defaultdict(list)
    for row in rows:
        if row['test_type'] != 'reference-comparison' or (run_id and row['run_id'] != run_id):
            continue
        detail = json.loads(row['detail'])
        detail.setdefault('effect_scope', 'end-to-end combined effects')
        key = tuple((row | detail)[field] for field in GROUP)
        groups[key].append((row, detail))
    result = []
    for key, cases in sorted(groups.items()):
        counts = {status: 0 for status in ['matched', 'different', 'error', 'unsupported', 'non_comparable']}
        overlap = maximum = row_cases = 0
        evidence = set()
        for row, case in cases:
            counts[case['comparison_status']] += 1
            evidence.add(row['evidence'])
            if case['comparison_status'] in ['matched', 'different'] and case.get('max_rows') is not None:
                overlap += case['overlap_rows']
                maximum += case['max_rows']
                row_cases += 1
        denominator = counts['matched'] + counts['different'] + counts['error']
        result.append(dict(zip(GROUP, key)) | {
            'matched': counts['matched'], 'different': counts['different'], 'errors': counts['error'],
            'unsupported': counts['unsupported'], 'non_comparable': counts['non_comparable'],
            'compared_cases': denominator,
            'case_agreement_pct': 100 * counts['matched'] / denominator if denominator else '',
            'overlap_rows': overlap, 'maximum_rows': maximum, 'row_cases': row_cases,
            'row_agreement_pct': 100 * overlap / maximum if maximum else '',
            'aspect_note': '; '.join(sorted({case.get('aspect_note', 'End-to-end combined effects; not isolated operator accuracy') for _, case in cases})),
            'evidence': ';'.join(sorted(evidence))})
    return result


def matrix_keys():
    # One source owns the executed matrix; importing it does not execute dbt or
    # initialize the pytest reporting plugin.
    sys.path.insert(0, str(ROOT))
    from tests.reference_support import comparison_cases
    return set(comparison_cases())


def case_key(detail):
    return tuple(detail[field] if field != 'target' else detail[field].split('/')[-1]
                 for field in ['reference', 'dataset', 'target', 'aspect', 'scope'])


def completeness(rows, run_id, expected):
    selected = [row for row in rows if row['run_id'] == run_id]
    cases = [row for row in selected if row['test_type'] == 'reference-comparison']
    keys = [case_key(json.loads(row['detail'])) for row in cases]
    invocations = [row for row in selected if row['test_type'] == 'run']
    invocation = invocations[0]['status'] if len(invocations) == 1 else 'missing-or-duplicate'
    baselines = [row for row in selected if row['test_type'] == 'reference-execution'
                 and (lambda detail: detail.get('reference') == 'classic' and detail.get('dataset') == 'original-seeds')(json.loads(row['detail']))]
    baseline = baselines[0]['status'] if len(baselines) == 1 else 'missing-or-duplicate'
    lifecycle_errors = sum(row['test_type'] == 'lifecycle-error' for row in selected)
    complete = (len(keys) == len(expected) and set(keys) == expected and invocation == 'passed'
                and baseline == 'passed' and not lifecycle_errors
                and all(row['status'] == 'passed' for row in cases))
    return {'run_completeness': 'complete-successful' if complete else 'partial-or-failed',
            'expected_cases': len(expected), 'actual_cases': len(keys),
            'missing_cases': len(expected - set(keys)), 'invocation_status': invocation,
            'baseline_status': baseline, 'lifecycle_errors': lifecycle_errors}


def evidence_path(value):
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def validate_evidence(rows, run_id, expected):
    relevant = [row for row in rows if row['run_id'] == run_id
                and row['test_type'] in ['reference-comparison', 'reference-execution', 'lifecycle-error']]
    selected = [row for row in relevant if row['test_type'] == 'reference-comparison']
    seen = set()
    for row in relevant:
        detail = json.loads(row['detail'])
        actual = json.loads(evidence_path(row['evidence']).read_text())
        # Evidence binds the measured result to its exact persisted history row.
        for field in ['run_id', 'revision', 'environment', 'case_id', 'input_id', 'status']:
            if actual.get(field) != row[field]:
                raise ValueError(f'Evidence/history {field} mismatch: {row["evidence"]}')
        if {key: value for key, value in actual.items() if key not in ['reference_output', 'generated_output']} != detail:
            raise ValueError(f'Contradictory comparison evidence: {row["evidence"]}')
        if row['test_type'] != 'reference-comparison':
            continue
        key = case_key(detail)
        if key not in expected or key in seen:
            raise ValueError(f'Unknown or duplicate reference case in {run_id}: {key}')
        seen.add(key)
        status = detail['comparison_status']
        if status not in ['matched', 'different', 'error', 'unsupported', 'non_comparable']:
            raise ValueError(f'Unknown comparison status: {status}')
        if status in ['matched', 'different']:
            left, right = actual['reference_output'], actual['generated_output']
            nleft, nright = len(left['rows']), len(right['rows'])
            maximum, overlap = detail['max_rows'], detail['overlap_rows']
            if (detail['reference_rows'] != nleft or detail['generated_rows'] != nright
                    or maximum != max(nleft, nright) or not isinstance(overlap, int)
                    or not 0 <= overlap <= min(nleft, nright)):
                raise ValueError(f'Contradictory row counts: {row["evidence"]}')
            if status == 'matched' and (not detail['schema_compatible'] or nleft != nright or overlap != maximum):
                raise ValueError(f'Invalid matching disposition: {row["evidence"]}')
            rate = 100 * overlap / maximum if maximum else (100.0 if detail['schema_compatible'] else None)
            observed = detail['row_agreement_pct']
            if (rate is None) != (observed is None) or (rate is not None and not math.isclose(rate, observed)):
                raise ValueError(f'Contradictory row rate: {row["evidence"]}')
            manifest = json.loads(evidence_path(detail['input_manifest']).read_text())
            identity = manifest.pop('input_id')
            import hashlib
            digest = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            if (identity != row['input_id'] or not identity.endswith(digest)
                    or manifest['reference'] != detail['reference'] or manifest['dataset'] != detail['dataset']):
                raise ValueError(f'Input manifest/history mismatch: {row["evidence"]}')
        elif detail.get('row_agreement_pct') is not None or detail.get('max_rows') is not None or detail.get('overlap_rows') is not None:
            raise ValueError(f'Non-executed comparison has row agreement: {row["evidence"]}')
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT / 'reports/test-runs.csv')
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/accuracy-by-aspect.csv')
    parser.add_argument('--run-id', help='Explicit run, including a visibly labelled partial/failed run')
    args = parser.parse_args()
    try:
        with args.input.open() as stream:
            rows = list(csv.DictReader(stream))
        reference_rows = [row for row in rows if row['test_type'] == 'reference-comparison']
        if not reference_rows:
            raise ValueError('No executed reference comparisons exist; refusing an empty accuracy report')
        expected = matrix_keys()
        if args.run_id:
            run_id = args.run_id
        else:
            run_id = next((run for run in reversed(dict.fromkeys(row['run_id'] for row in reference_rows))
                           if completeness(rows, run, expected)['run_completeness'] == 'complete-successful'), None)
            if run_id is None:
                raise ValueError('No successful complete reference matrix; use --run-id to explicitly inspect a partial run')
        selected = validate_evidence(rows, run_id, expected)
        if not selected:
            raise ValueError(f'No reference comparisons in run {run_id}')
        info = completeness(rows, run_id, expected)
        summaries = [row | info for row in aggregate(rows, run_id)]
        # Validate first, then atomically replace: rejected input cannot truncate
        # or overwrite the previous measured report.
        with tempfile.NamedTemporaryFile(mode='w', newline='', dir=args.output.parent, delete=False) as stream:
            temporary = Path(stream.name)
            writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator='\n')
            writer.writeheader()
            writer.writerows(summaries)
        os.replace(temporary, args.output)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(f'{run_id}: {info["run_completeness"]}; reference cases={info["actual_cases"]}/{info["expected_cases"]}; '
          f'{len(summaries)} end-to-end aspect/dataset/scope groups -> {args.output}')


if __name__ == '__main__':
    main()
