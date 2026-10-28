"""Core report facts, uncertain evidence and the actual CLI publication flow."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest

from pwc_to_dbt.cli import main
from pwc_to_dbt.dependencies import plan
from pwc_to_dbt.mapping import ConversionError
from pwc_to_dbt.project import compile_models
from pwc_to_dbt.source_report import source_report
from pwc_to_dbt.xml_reader import read_xml
from .helpers import CORE, ROOT, STAGING, XML, config, mutated


def definitions(report):
    return {row['metadata']['NAME']: row for row in report['source_definitions']}


def uses(report):
    return {use['identity']: use for row in report['source_definitions'] for use in row['uses']}


def snapshot(directory):
    return {str(path.relative_to(directory)): path.read_bytes() for path in directory.rglob('*') if path.is_file()}


def test_whole_export_inventory_exact_uses_bindings_and_contexts():
    report = source_report(read_xml(XML), config())
    assert report['format_version'] == 1 and report['scope'] == 'whole_export'
    assert report['input_sha256'] == hashlib.sha256(XML.read_bytes()).hexdigest()
    assert report['catalogue']['review_date'] == '2026-10-28'
    assert report['counts'] == {
        'source_definitions': 12, 'source_uses': 28, 'unresolved_source_uses': 0,
        'definitions_by_classification': {'external': 7, 'mixed': 5},
        'uses_by_classification': {'bound': 12, 'external': 16},
        'definitions_by_connector_status': {'available': 12}}
    rows = definitions(report)
    assert len(rows['RAW_PRODUCTS']['uses']) == 2
    assert rows['STG_CUSTOMERS']['classification'] == 'mixed'
    assert rows['STG_LOCATIONS']['classification'] == 'external'
    assert all(row['connector']['client_compatibility'] == 'not_verified' for row in rows.values())
    assert all(use['producer_availability'] == 'not_evaluated' for use in uses(report).values() if use['producer'])
    references = [row for row in report['reader_connections'] if row['reader_instance'] == 'SQ_RAW_CUSTOMERS']
    assert len(references) == 2
    assert {row['connection_name'] for row in references} == {'MART_Jaffleshop', 'RAW_Jaffleshop'}
    assert all(row['source_uses'] == [STAGING + 'RAW_CUSTOMERS'] for row in references)
    override = next(row for row in references if row['task_instance'])
    assert override['workflow'] == 'wf_FL_JAFFLESHOP_DEMO'
    assert override['session'] == override['task_instance'] == 's_FL_JS_STAGING_FULL'
    assert set(override['association_provenance']) == {'INSTANCE/ASSOCIATED_SOURCE_INSTANCE', 'SESSIONEXTENSION/DSQINSTNAME (inherited session declaration)'}
    session = next(row for row in references if row['task_instance'] is None)
    assert set(session['association_provenance']) == {'INSTANCE/ASSOCIATED_SOURCE_INSTANCE', 'SESSIONEXTENSION/DSQINSTNAME'}
    assert all(row['task_instance'] is None for row in report['source_associations']
               if row['provenance'] == 'SESSIONEXTENSION/DSQINSTNAME')
    assert not report['unassigned_reader_connections']
    # WRITER declarations do not become source connections.
    assert len(report['reader_connections']) == 35
    assert not any('WRITER' in row['provenance'] for row in report['reader_connections'])


def test_unused_exact_definitions_missing_and_unknown_metadata(tmp_path, request):
    def change(root):
        folder = root.find('.//FOLDER')
        source = deepcopy(folder.find("SOURCE[@NAME='RAW_CUSTOMERS']"))
        source.set('NAME', 'UNUSED')
        source.set('DATABASETYPE', 'Oracle-Compatible')
        source.attrib.pop('OWNERNAME', None)
        source.attrib.pop('DBDNAME', None)
        folder.append(source)
        other = ET.SubElement(root.find('REPOSITORY'), 'FOLDER', NAME='OTHER')
        duplicate = deepcopy(source)
        duplicate.attrib.pop('DATABASETYPE')
        other.append(duplicate)
    report = source_report(read_xml(mutated(tmp_path, request, change)))
    rows = [row for row in report['source_definitions'] if row['metadata']['NAME'] == 'UNUSED']
    assert len(rows) == 2 and {row['identity']['folder'] for row in rows} == {'OTHER', 'FLOWLINE_DEMO_JAFFLESHOP'}
    assert all(row['classification'] == 'unused' and not row['uses'] for row in rows)
    assert {row['connector']['status'] for row in rows} == {'unknown', 'no_known_match'}
    assert all(row['metadata']['OWNERNAME'] is None and row['metadata']['DBDNAME'] is None for row in rows)
    assert all('missing OWNERNAME' in row['diagnostics'] for row in rows)


@pytest.mark.parametrize('technology,expected', [(' oracle ', 'Oracle'), ('Postgres', 'PostgreSQL'),
                                               ('MYSQL', 'MySQL'), (' Microsoft SQL Server ', 'SQL Server'),
                                               ('Oracle Compatible', None)])
def test_catalogue_uses_exact_trimmed_case_insensitive_aliases(tmp_path, request, technology, expected):
    def change(root):
        folder = root.find('.//FOLDER')
        ET.SubElement(folder, 'SOURCE', NAME='UNUSED', DATABASETYPE=technology)
    row = definitions(source_report(read_xml(mutated(tmp_path, request, change))))['UNUSED']
    assert row['metadata']['DATABASETYPE'] == technology
    assert [candidate['technology'] for candidate in row['connector']['candidates']] == ([expected] if expected else [])
    assert row['connector']['status'] == ('available' if expected else 'no_known_match')


@pytest.mark.parametrize('mode', ['conflicting_subtype', 'absent_type', 'absent_connection_name'])
def test_connection_metadata_uncertainty_is_explicit(tmp_path, request, mode):
    def change(root):
        if mode == 'absent_type':
            root.find(".//SOURCE[@NAME='RAW_CUSTOMERS']").attrib.pop('DATABASETYPE')
        else:
            reference = root.find(".//SESSION[@NAME='s_FL_JS_STAGING_FULL']/SESSIONEXTENSION[@SINSTANCENAME='SQ_RAW_CUSTOMERS']/CONNECTIONREFERENCE")
            if mode == 'conflicting_subtype':
                reference.set('CONNECTIONSUBTYPE', 'PostgreSQL')
            else:
                reference.attrib.pop('CONNECTIONNAME')
    row = definitions(source_report(read_xml(mutated(tmp_path, request, change))))['RAW_CUSTOMERS']
    connector = row['connector']
    assert connector['status'] == {'conflicting_subtype': 'requires_review', 'absent_type': 'unknown', 'absent_connection_name': 'available'}[mode]
    assert connector['client_compatibility'] == connector['existing_fivetran_configuration'] == 'not_verified'
    assert row['diagnostics']
    if mode == 'conflicting_subtype':
        assert {candidate['technology'] for candidate in connector['candidates']} == {'Oracle', 'PostgreSQL'}


@pytest.mark.parametrize('mode', ['disagree', 'wrong_type', 'missing_source', 'absent', 'ambiguous_dsq', 'unknown_task',
                                'missing_qualifier_declaration', 'missing_session_declaration'])
def test_invalid_reader_associations_are_preserved_unassigned(tmp_path, request, mode):
    def change(root):
        mapping = root.find(".//MAPPING[@NAME='m_FL_JS_STAGING_FULL']")
        qualifier = mapping.find("INSTANCE[@NAME='SQ_RAW_CUSTOMERS']")
        session = root.find(".//SESSION[@NAME='s_FL_JS_STAGING_FULL']")
        if mode == 'disagree':
            qualifier.find('ASSOCIATED_SOURCE_INSTANCE').set('NAME', 'RAW_PRODUCTS')
        elif mode == 'wrong_type':
            mapping.find("TRANSFORMATION[@NAME='SQ_RAW_CUSTOMERS']").set('TYPE', 'Expression')
        elif mode == 'missing_source':
            qualifier.find('ASSOCIATED_SOURCE_INSTANCE').set('NAME', 'ABSENT')
        elif mode == 'absent':
            qualifier.remove(qualifier.find('ASSOCIATED_SOURCE_INSTANCE'))
            session.remove(session.find("SESSIONEXTENSION[@SINSTANCENAME='RAW_CUSTOMERS']"))
        elif mode == 'ambiguous_dsq':
            duplicate = deepcopy(session.find("SESSIONEXTENSION[@SINSTANCENAME='RAW_CUSTOMERS']"))
            duplicate.set('DSQINSTNAME', 'SQ_RAW_PRODUCTS')
            session.append(duplicate)
        elif mode == 'missing_qualifier_declaration':
            qualifier.remove(qualifier.find('ASSOCIATED_SOURCE_INSTANCE'))
        elif mode == 'missing_session_declaration':
            session.remove(session.find("SESSIONEXTENSION[@SINSTANCENAME='RAW_CUSTOMERS']"))
        else:
            root.find(".//TASKINSTANCE[@NAME='s_FL_JS_STAGING_FULL']").set('TASKNAME', 'ABSENT')
    report = source_report(read_xml(mutated(tmp_path, request, change)))
    references = [row for row in report['reader_connections'] if row['reader_instance'] == 'SQ_RAW_CUSTOMERS'
                  and (mode != 'unknown_task' or row['task_instance'])]
    assert references and all(row['diagnostics'] and not row['source_uses'] for row in references)
    assert all(row['id'] in report['unassigned_reader_connections'] for row in references)
    assert len(uses(report)) == 28
    if mode in {'disagree', 'ambiguous_dsq', 'missing_qualifier_declaration', 'missing_session_declaration'}:
        evidence = [row for row in report['source_associations'] if row['qualifier_instance'] == 'SQ_RAW_CUSTOMERS']
        assert evidence and all(row['diagnostics'] for row in evidence)
        if mode == 'ambiguous_dsq':
            dsq_evidence = [row for row in evidence if row['provenance'] == 'SESSIONEXTENSION/DSQINSTNAME']
            assert all(any('ambiguous DSQ' in problem for problem in row['diagnostics']) for row in dsq_evidence)


def test_missing_definition_remains_an_unresolved_use(tmp_path, request):
    def change(root):
        root.find(".//MAPPING[@NAME='m_FL_JS_STAGING_FULL']/INSTANCE[@NAME='RAW_CUSTOMERS']").set('TRANSFORMATION_NAME', 'ABSENT')
    report = source_report(read_xml(mutated(tmp_path, request, change)), config())
    assert report['counts']['source_definitions'] == 12 and report['counts']['source_uses'] == 28
    assert report['counts']['unresolved_source_uses'] == 1
    assert report['unresolved_source_uses'][0]['identity'] == STAGING + 'RAW_CUSTOMERS'
    assert report['unresolved_source_uses'][0]['classification'] == 'unresolved'
    assert definitions(report)['RAW_CUSTOMERS']['classification'] == 'unused'


def test_binding_availability_and_ingestion_are_separate_for_unselected_use(tmp_path, request):
    # The selected customer path emits STG_ORDERS. Another bound, unselected
    # source use may still be incompatible; producer emission cannot certify it.
    def change(root):
        root.find(".//SOURCE[@NAME='STG_ORDERS']/SOURCEFIELD").set('NAME', 'UNAVAILABLE_COLUMN')
    export = read_xml(mutated(tmp_path, request, change))
    artifacts, outcomes = compile_models(plan(export, [STAGING + 'STG_ORDERS'], config()))
    assert len(artifacts) == 1
    report = source_report(export, config(), outcomes=outcomes)
    use = uses(report)[CORE + 'STG_ORDERS']
    assert use['classification'] == 'bound' and use['producer_availability'] == 'emitted'
    assert use['external_ingestion'] == 'not_established'
    assert uses(report)[CORE + 'STG_CUSTOMERS']['producer_availability'] == 'unselected'
    assert report['counts']['source_uses'] == 28


def test_failed_producer_never_becomes_external_ingestion(tmp_path, request):
    def change(root):
        root.find(".//MAPPING[@NAME='m_FL_JS_STAGING_FULL']/TRANSFORMATION[@NAME='EXP_ORDERS']/TRANSFORMFIELD[@NAME='SUBTOTAL']").set('EXPRESSION', 'UNKNOWN(SUBTOTAL_IN)')
    export = read_xml(mutated(tmp_path, request, change))
    _, outcomes = compile_models(plan(export, config=config()))
    report = source_report(export, config(), outcomes=outcomes)
    use = uses(report)[CORE + 'STG_ORDERS']
    assert use['classification'] == 'bound'
    assert use['producer_availability'] == 'failed_or_blocked'
    assert use['producer_outcome'] == 'unsupported'
    assert use['external_ingestion'] == 'not_established'
    reason = next(outcome.reason for key, outcome in outcomes.items() if str(key) == use['producer'])
    assert any(reason in diagnostic for diagnostic in use['diagnostics'])


def test_report_only_skips_planning_compilation_and_database(monkeypatch, capsys):
    import duckdb
    def forbidden(*args, **kwargs):
        raise AssertionError('report attempted conversion/database access')
    monkeypatch.setattr('pwc_to_dbt.cli.plan', forbidden)
    monkeypatch.setattr('pwc_to_dbt.cli.compile_models', forbidden)
    monkeypatch.setattr(duckdb, 'connect', forbidden)
    assert main([str(XML), '--source-report']) == 0
    report = json.loads(capsys.readouterr().out)
    assert report['counts']['source_uses'] == 28
    assert report['counts']['uses_by_classification'] == {'external': 28}


@pytest.mark.negative
@pytest.mark.parametrize('configuration', [{'typo': {}}, {'bindings': []}, {'bindings': {CORE + 'STG_ORDERS': 'STG_ORDERS'}},
                                          {'bindings': {CORE + 'STG_ORDERS': 123}}, [], False,
                                          {'target_relations': {CORE + 'CUSTOMERS': []}},
                                          {'target_relations': {CORE + 'CUSTOMERS': {'schema': 'MART', 'table': 42}}}])
def test_report_binding_configuration_uses_exact_existing_contract(configuration):
    with pytest.raises(ConversionError):
        source_report(read_xml(XML), configuration)


@pytest.mark.negative
@pytest.mark.parametrize('options', [['--inventory'], ['--target', CORE + 'CUSTOMERS']])
def test_report_rejects_conflicting_cli_options(options, capsys):
    assert main([str(XML), '--source-report', *options]) == 2
    assert capsys.readouterr().err


def test_actual_cli_report_is_deterministic_and_conversion_artifact_is_opt_in(tmp_path):
    command = [str(Path(sys.executable).parent / 'pwc-to-dbt'), str(XML), '--bindings', str(ROOT / 'examples/sample-bindings.json')]
    first = subprocess.run([*command, '--source-report'], capture_output=True, text=True, timeout=30)
    second = subprocess.run([*command, '--source-report'], capture_output=True, text=True, timeout=30)
    assert first.returncode == second.returncode == 0, first.stderr + second.stderr
    assert first.stdout == second.stdout
    assert json.loads(first.stdout)['counts']['source_uses'] == 28
    for name, options, status in [('default', [], 0), ('report', ['--source-report'], 0), ('partial', ['--source-report'], 1)]:
        selection = ['--target', CORE + 'CUSTOMERS'] if name != 'partial' else []
        result = subprocess.run([*command, '--output', str(tmp_path / name), *selection, *options], capture_output=True, text=True, timeout=30)
        assert result.returncode == status, result.stdout + result.stderr
    default, included = snapshot(tmp_path / 'default'), snapshot(tmp_path / 'report')
    artifact = included.pop('fivetran-source-report.json')
    assert included == default
    assert json.loads(artifact)['counts']['source_uses'] == 28
    partial = json.loads((tmp_path / 'partial/fivetran-source-report.json').read_bytes())
    assert partial['counts']['source_definitions'] == 12 and partial['counts']['source_uses'] == 28
    manifest = json.loads((tmp_path / 'partial/conversion-manifest.json').read_bytes())
    assert any(row['status'] == 'unsupported' for row in manifest['outcomes'])
    assert uses(partial)[CORE + 'STG_ORDER_ITEMS']['producer_availability'] == 'emitted'


def test_report_output_protection_and_atomic_write_failure(tmp_path, monkeypatch, capsys):
    output = tmp_path / 'existing'
    output.mkdir()
    (output / 'keep').write_bytes(b'keep')
    assert main([str(XML), '--source-report', '--output', str(output)]) == 2
    assert snapshot(output) == {'keep': b'keep'}
    capsys.readouterr()
    def fail_publish(*args):
        raise OSError('controlled publication failure')
    monkeypatch.setattr('pwc_to_dbt.project.os.replace', fail_publish)
    assert main([str(XML), '--source-report', '--output', str(tmp_path / 'new')]) == 2
    assert not (tmp_path / 'new').exists()
    assert not list(tmp_path.glob('.pwc-project-*'))


@pytest.mark.negative
def test_report_only_keeps_fatal_xml_and_duplicate_config_guards(tmp_path, capsys):
    malformed = tmp_path / 'malformed.xml'
    malformed.write_text('<broken>')
    assert main([str(malformed), '--source-report']) == 2
    assert 'Malformed XML' in capsys.readouterr().err
    configuration = tmp_path / 'duplicate.json'
    configuration.write_text('{"bindings": {}, "bindings": {}}')
    assert main([str(XML), '--source-report', '--bindings', str(configuration)]) == 2
    assert 'Duplicate configuration key' in capsys.readouterr().err


def test_direct_source_reader_with_invalid_dsq_stays_unassigned(tmp_path, request):
    def change(root):
        extension = root.find(".//SESSION[@NAME='s_FL_JS_STAGING_FULL']/SESSIONEXTENSION[@SINSTANCENAME='RAW_CUSTOMERS']")
        extension.set('DSQINSTNAME', 'ABSENT')
        ET.SubElement(extension, 'CONNECTIONREFERENCE', CONNECTIONNAME='DECLARED',
                      CONNECTIONTYPE='Relational', CONNECTIONSUBTYPE='Oracle')
    report = source_report(read_xml(mutated(tmp_path, request, change)))
    reader = next(row for row in report['reader_connections'] if row['reader_instance'] == 'RAW_CUSTOMERS')
    assert not reader['source_uses'] and reader['connection_name'] == 'DECLARED'
    assert any('DSQ instance is absent' in problem for problem in reader['diagnostics'])
    evidence = next(row for row in report['source_associations'] if row['qualifier_instance'] == 'ABSENT')
    assert evidence['source_instance'] == 'RAW_CUSTOMERS'
    assert any('DSQ instance is absent' in problem for problem in evidence['diagnostics'])


@pytest.mark.parametrize('field,value', [('CONNECTIONTYPE', None), ('CONNECTIONTYPE', '  '),
                                        ('CONNECTIONNAME', '  '), ('CONNECTIONSUBTYPE', '  ')])
def test_definition_and_reader_share_connection_completeness_rule(tmp_path, request, field, value):
    def change(root):
        reference = root.find(".//SESSION[@NAME='s_FL_JS_STAGING_FULL']/SESSIONEXTENSION[@SINSTANCENAME='SQ_RAW_CUSTOMERS']/CONNECTIONREFERENCE")
        if value is None:
            reference.attrib.pop(field)
        else:
            reference.set(field, value)
    report = source_report(read_xml(mutated(tmp_path, request, change)))
    assert 'associated reader connection declaration is incomplete' in definitions(report)['RAW_CUSTOMERS']['diagnostics']
    reader = next(row for row in report['reader_connections'] if row['reader_instance'] == 'SQ_RAW_CUSTOMERS' and row['task_instance'] is None)
    assert f'missing {field}' in reader['diagnostics']


def test_reader_subtype_conflict_does_not_invent_absent_source_type(tmp_path, request):
    def change(root):
        root.find(".//SOURCE[@NAME='RAW_CUSTOMERS']").attrib.pop('DATABASETYPE')
        reference = root.find(".//SESSION[@NAME='s_FL_JS_STAGING_FULL']/SESSIONEXTENSION[@SINSTANCENAME='SQ_RAW_CUSTOMERS']/CONNECTIONREFERENCE")
        reference.set('CONNECTIONSUBTYPE', 'PostgreSQL')
    row = definitions(source_report(read_xml(mutated(tmp_path, request, change))))['RAW_CUSTOMERS']
    assert row['metadata']['DATABASETYPE'] is None
    assert row['connector']['status'] == 'requires_review'
    assert 'technology declarations conflict' in row['diagnostics']
    assert not any('source database type' in problem for problem in row['diagnostics'])


def test_report_catalogue_and_row_lists_are_independent():
    export = read_xml(XML)
    original = source_report(export)
    changed = source_report(export)
    changed['catalogue']['entries'][0]['aliases'].append('changed')
    changed['catalogue']['entries'][0]['limits'].append('changed catalogue')
    first, second = changed['source_definitions'][:2]
    first['connector']['further_checks'].append('changed checks')
    first['connector']['candidates'][0]['limits'].append('changed row')
    assert second['connector']['further_checks'] == original['source_definitions'][1]['connector']['further_checks']
    assert second['connector']['candidates'][0]['limits'] == original['source_definitions'][1]['connector']['candidates'][0]['limits']
    assert source_report(export) == original


def test_worklet_reader_context_is_explicitly_unsupported(tmp_path, request):
    def change(root):
        folder = root.find('.//FOLDER')
        session = folder.find("SESSION[@NAME='s_FL_JS_STAGING_FULL']")
        folder.remove(session)
        ET.SubElement(folder, 'WORKLET', NAME='UNRESOLVED_WORKLET').append(session)
    report = source_report(read_xml(mutated(tmp_path, request, change)))
    readers = [row for row in report['reader_connections'] if row['session'] == 's_FL_JS_STAGING_FULL']
    assert len(readers) == 14 and all(not row['source_uses'] for row in readers)
    assert all(any('worklet scope is unsupported' in problem for problem in row['diagnostics']) for row in readers)
    evidence = [row for row in report['source_associations'] if row['session'] == 's_FL_JS_STAGING_FULL']
    assert evidence and all(any('worklet scope is unsupported' in problem for problem in row['diagnostics']) for row in evidence)


def test_used_same_name_definitions_keep_exact_metadata_binding_and_reader_ownership(tmp_path, request):
    other_staging = STAGING.replace('/FLOWLINE_DEMO_JAFFLESHOP/', '/OTHER/')
    def change(root):
        folder = root.find('.//FOLDER')
        source = folder.find("SOURCE[@NAME='RAW_CUSTOMERS']")
        source.set('OWNERNAME', 'Owner Original')
        source.set('DBDNAME', 'Database Original')
        other = deepcopy(folder)
        other.set('NAME', 'OTHER')
        source = other.find("SOURCE[@NAME='RAW_CUSTOMERS']")
        source.set('OWNERNAME', 'Owner Other')
        source.set('DBDNAME', 'Database Other')
        for extension in other.iter('SESSIONEXTENSION'):
            if extension.get('TYPE') == 'READER':
                for reference in extension.findall('CONNECTIONREFERENCE'):
                    reference.set('CONNECTIONNAME', 'Other Reader')
        root.find('REPOSITORY').append(other)
    configuration = {'bindings': {STAGING + 'RAW_CUSTOMERS': STAGING + 'STG_CUSTOMERS'}}
    report = source_report(read_xml(mutated(tmp_path, request, change)), configuration)
    rows = {tuple(row['identity'][key] for key in ('repository', 'folder', 'name')): row
            for row in report['source_definitions'] if row['metadata']['NAME'] == 'RAW_CUSTOMERS'}
    assert len(rows) == 2
    for folder, prefix, owner, database, producer in [
        ('FLOWLINE_DEMO_JAFFLESHOP', STAGING, 'Owner Original', 'Database Original', STAGING + 'STG_CUSTOMERS'),
        ('OTHER', other_staging, 'Owner Other', 'Database Other', None),
    ]:
        row = rows[('REPO_Jaffleshop', folder, 'RAW_CUSTOMERS')]
        assert row['metadata'] == {'NAME': 'RAW_CUSTOMERS', 'DATABASETYPE': 'Oracle',
                                   'OWNERNAME': owner, 'DBDNAME': database}
        assert len(row['uses']) == 1
        use = row['uses'][0]
        assert use['identity'] == prefix + 'RAW_CUSTOMERS'
        assert use['producer'] == producer and use['classification'] == ('bound' if producer else 'external')
        readers = [reader for reader in report['reader_connections'] if reader['id'] in use['connection_references']]
        assert len(readers) == 2
        assert all(reader['folder'] == folder and reader['source_uses'] == [prefix + 'RAW_CUSTOMERS'] for reader in readers)
        assert {reader['connection_name'] for reader in readers} == ({'Other Reader'} if folder == 'OTHER' else {'MART_Jaffleshop', 'RAW_Jaffleshop'})
