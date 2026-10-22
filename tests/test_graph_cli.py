from dataclasses import replace
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from pwc_to_dbt.cli import main
from pwc_to_dbt.dependencies import plan
from pwc_to_dbt.mapping import ConversionError, InstanceKey
from pwc_to_dbt.project import compile_models
from pwc_to_dbt.xml_reader import read_xml
from .helpers import CORE, REQUIRED, STAGING, XML, config, convert_to, mutated


def staging(root):
    return root.find(".//MAPPING[@NAME='m_FL_JS_STAGING_FULL']")


def outcome_by_name(outcomes):
    return {key.instance: value for key, value in outcomes.items()}


def test_inventory_is_complete_and_exact():
    export = read_xml(XML)
    assert len(export.mappings) == 3
    assert len(export.targets) == 16
    core = next(m for m in export.mappings.values() if m.key.mapping == 'm_FL_JS_MARTS_CORE')
    assert core.nodes['STG_PRODUCTS1'].definition == 'STG_PRODUCTS'
    assert core.nodes['STG_PRODUCTS1'].key != core.nodes['STG_PRODUCTS'].key


def test_core_selection_includes_exact_bound_producer_closure(tmp_path):
    _, planning, artifacts, outcomes, manifest = convert_to(tmp_path / 'output', selected=[CORE + 'CUSTOMERS'])
    assert len(artifacts) == 3
    assert {key.instance for key in artifacts} == {'CUSTOMERS', 'STG_CUSTOMERS', 'STG_ORDERS'}
    customer = next(a for k, a in artifacts.items() if k.instance == 'CUSTOMERS')
    assert customer.sql.count('{{ ref(') == 2
    assert not any(s.producer is None for s in customer.plan.sources)
    assert len(manifest['inventory']) == 16
    assert sum(i['selection'] == 'unselected' for i in manifest['inventory']) == 13


def test_unbound_inputs_are_declared_external(tmp_path):
    configuration = config()
    configuration['bindings'] = {}
    _, _, artifacts, _, manifest = convert_to(tmp_path / 'output', selected=[CORE + 'CUSTOMERS'], configuration=configuration)
    assert len(artifacts) == 1
    artifact = next(iter(artifacts.values()))
    assert artifact.sql.count('{{ source(') == 2
    sources = json.loads((tmp_path / 'output/models/sources.yml').read_text())
    assert {s['schema'] for s in sources['sources']} == {'STG'}


@pytest.mark.negative
@pytest.mark.parametrize('identity', ['CUSTOMERS', CORE + 'ABSENT'])
def test_unknown_or_short_selection_rejected(identity):
    with pytest.raises(ConversionError, match='full inventory identity'):
        plan(read_xml(XML), [identity], config())


@pytest.mark.negative
@pytest.mark.parametrize('source,target', [('STG_ORDERS', STAGING + 'STG_ORDERS'), (CORE + 'STG_ORDERS2', STAGING + 'ABSENT')])
def test_unknown_bindings_rejected(source, target):
    configuration = config()
    configuration['bindings'] = {source: target}
    with pytest.raises(ConversionError, match='Unknown'):
        plan(read_xml(XML), REQUIRED, configuration)


@pytest.mark.negative
def test_unknown_config_and_duplicate_json_keys(tmp_path, capsys):
    path = tmp_path / 'bindings.json'
    path.write_text('{"bindings": {}, "bindings": {}}')
    assert main([str(XML), '--output', str(tmp_path / 'out'), '--bindings', str(path)]) == 2
    assert 'Duplicate configuration key' in capsys.readouterr().err
    with pytest.raises(ConversionError, match='accepts'):
        plan(read_xml(XML), REQUIRED, {'typo': {}})


@pytest.mark.negative
def test_missing_connector_blocks_only_affected_and_consumers(tmp_path, request):
    def change(root):
        mapping = staging(root)
        mapping.remove(mapping.find("CONNECTOR[@TOINSTANCE='EXP_ORDERS'][@TOFIELD='SUBTOTAL_IN']"))
    xml = mutated(tmp_path, request, change)
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'output', xml=xml)
    values = outcome_by_name(outcomes)
    assert values['STG_ORDERS'].status == 'error'
    assert 'SUBTOTAL_IN' in values['STG_ORDERS'].reason
    assert values['CUSTOMERS'].status == 'blocked'
    assert {key.instance for key in artifacts} == {'STG_CUSTOMERS', 'STG_PRODUCTS', 'STG_SUPPLIES'}


@pytest.mark.negative
def test_missing_port_diagnostic(tmp_path, request):
    def change(root):
        staging(root).find("CONNECTOR[@TOINSTANCE='STG_CUSTOMERS']").set('FROMFIELD', 'ABSENT')
    xml = mutated(tmp_path, request, change)
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'out', xml=xml, selected=[STAGING + 'STG_CUSTOMERS'])
    assert not artifacts
    assert 'missing port' in next(iter(outcomes.values())).reason


@pytest.mark.negative
def test_cycle_is_detected(tmp_path, request):
    def change(root):
        mapping = staging(root)
        for c in mapping.findall("CONNECTOR[@TOINSTANCE='SQ_RAW_CUSTOMERS']"):
            c.set('FROMINSTANCE', 'SQ_RAW_CUSTOMERS')
            c.set('FROMFIELD', c.get('TOFIELD'))
    xml = mutated(tmp_path, request, change)
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'out', xml=xml, selected=[STAGING + 'STG_CUSTOMERS'])
    assert not artifacts
    assert 'cycle' in next(iter(outcomes.values())).reason


@pytest.mark.negative
def test_incompatible_binding_and_missing_consumed_column(tmp_path, request):
    def change(root):
        root.find(".//TARGET[@NAME='STG_CUSTOMERS']/TARGETFIELD[@NAME='CUSTOMER_NAME']").set('PRECISION', '250')
    xml = mutated(tmp_path, request, change)
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'out', xml=xml, selected=[CORE + 'CUSTOMERS'])
    values = outcome_by_name(outcomes)
    assert values['CUSTOMERS'].status == 'error'
    assert 'incompatible binding' in values['CUSTOMERS'].reason
    assert 'STG_CUSTOMERS' in {key.instance for key in artifacts}


@pytest.mark.negative
@pytest.mark.parametrize('operation', ['unknown_expression', 'unknown_transformation', 'required_preparation'])
def test_unsupported_blocks_producer_and_retains_independent_outputs(tmp_path, request, operation):
    def change(root):
        mapping = staging(root)
        if operation == 'unknown_expression':
            mapping.find("TRANSFORMATION[@NAME='EXP_ORDERS']/TRANSFORMFIELD[@NAME='SUBTOTAL']").set('EXPRESSION', 'MYSTERY(SUBTOTAL_IN)')
        elif operation == 'unknown_transformation':
            mapping.find("TRANSFORMATION[@NAME='EXP_ORDERS']").set('TYPE', 'Custom Transformation')
        else:
            mapping.find("INSTANCE[@NAME='STG_ORDERS']/TABLEATTRIBUTE[@NAME='Pre SQL']").set('VALUE', 'DELETE FROM STG.STG_ORDERS WHERE ORDER_ID IS NULL')
    xml = mutated(tmp_path, request, change)
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'out', xml=xml)
    values = outcome_by_name(outcomes)
    assert values['STG_ORDERS'].status == 'unsupported'
    assert values['CUSTOMERS'].status == 'blocked'
    assert {key.instance for key in artifacts} == {'STG_CUSTOMERS', 'STG_PRODUCTS', 'STG_SUPPLIES'}
    assert not (tmp_path / 'out/models' / values['STG_ORDERS'].artifact).exists() if values['STG_ORDERS'].artifact else True


@pytest.mark.negative
def test_required_qualifier_override_is_not_ignored(tmp_path, request):
    def change(root):
        staging(root).find("TRANSFORMATION[@NAME='SQ_RAW_CUSTOMERS']/TABLEATTRIBUTE[@NAME='Source Filter']").set('VALUE', 'ID IS NOT NULL')
    xml = mutated(tmp_path, request, change)
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'out', xml=xml, selected=[STAGING + 'STG_CUSTOMERS'])
    assert not artifacts
    assert 'Source Filter' in next(iter(outcomes.values())).reason


@pytest.mark.negative
def test_collision_is_rejected(tmp_path, request):
    def change(root):
        mapping = staging(root)
        original = mapping.find("INSTANCE[@NAME='STG_CUSTOMERS']")
        duplicate = ET.fromstring(ET.tostring(original))
        duplicate.set('NAME', 'stg_customers')
        mapping.append(duplicate)
    xml = mutated(tmp_path, request, change)
    with pytest.raises(ConversionError, match='collision'):
        plan(read_xml(xml), REQUIRED, config())


@pytest.mark.negative
@pytest.mark.parametrize('payload', [b'<!DOCTYPE POWERMART [<!ENTITY e "expand">]><POWERMART>&e;</POWERMART>',
                                   b'<!DOCTYPE POWERMART [<!ENTITY e SYSTEM "file:///nonexistent">]><POWERMART>&e;</POWERMART>'])
def test_entity_declarations_refused(tmp_path, payload):
    xml = tmp_path / 'unsafe.xml'
    xml.write_bytes(payload)
    with pytest.raises(ConversionError, match='entity declarations'):
        read_xml(xml)


def test_external_dtd_is_never_fetched(tmp_path, request):
    import hashlib
    xml = tmp_path / 'external.xml'
    data = XML.read_bytes().replace(b'powrmart.dtd', b'http://127.0.0.1:9/never-fetch.dtd')
    xml.write_bytes(data)
    request.node.actual_input_id = 'external-DTD-XML:sha256:' + hashlib.sha256(data).hexdigest()
    assert len(read_xml(xml).targets) == 16


@pytest.mark.negative
@pytest.mark.parametrize('payload', [b'<broken>', b'<OTHER/>'])
def test_malformed_and_unknown_roots_rejected(tmp_path, payload):
    path = tmp_path / 'bad.xml'
    path.write_bytes(payload)
    with pytest.raises(ConversionError):
        read_xml(path)


@pytest.mark.negative
def test_destination_refusal_preserves_existing_files(tmp_path):
    output = tmp_path / 'output'
    output.mkdir()
    sentinel = output / 'keep.txt'
    sentinel.write_bytes(b'keep')
    assert main([str(XML), '--output', str(output)]) == 2
    assert list(output.iterdir()) == [sentinel]
    assert sentinel.read_bytes() == b'keep'


def test_deterministic_files_include_manifest_and_empty_directory(tmp_path):
    first = tmp_path / 'one'
    second = tmp_path / 'two'
    second.mkdir()
    convert_to(first)
    convert_to(second)
    snapshot = lambda path: {str(p.relative_to(path)): p.read_bytes() for p in path.rglob('*') if p.is_file()}
    assert snapshot(first) == snapshot(second)
    assert len(snapshot(first)) == 13


def test_cli_success_partial_failure_and_inventory(tmp_path, capsys):
    bindings = tmp_path / 'bindings.json'
    bindings.write_text(json.dumps(config()))
    assert main([str(XML), '--inventory']) == 0
    assert len(json.loads(capsys.readouterr().out)['targets']) == 16
    assert main([str(XML), '--output', str(tmp_path / 'one'), '--target', CORE + 'CUSTOMERS', '--bindings', str(bindings)]) == 0
    capsys.readouterr()
    assert main([str(XML), '--output', str(tmp_path / 'all'), '--bindings', str(bindings)]) == 1
    manifest = json.loads((tmp_path / 'all/conversion-manifest.json').read_text())
    assert len(manifest['outcomes']) == 16
    assert any(o['status'] == 'unsupported' for o in manifest['outcomes'])
    assert any(o['status'] == 'emitted' for o in manifest['outcomes'])


@pytest.mark.negative
def test_cleanup_requires_correct_explicit_original_relation(tmp_path):
    configuration = config()
    configuration['target_relations'] = {}
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'missing', selected=[STAGING + 'STG_CUSTOMERS'], configuration=configuration)
    assert not artifacts
    assert 'original target schema absent' in next(iter(outcomes.values())).reason
    configuration['target_relations'][STAGING + 'STG_CUSTOMERS'] = {'schema': 'WRONG', 'table': 'STG_CUSTOMERS'}
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'wrong', selected=[STAGING + 'STG_CUSTOMERS'], configuration=configuration)
    assert not artifacts
    assert 'does not match' in next(iter(outcomes.values())).reason


def test_supplied_hashes_are_unchanged():
    import hashlib
    from .helpers import ROOT
    provenance = json.loads((ROOT / 'fixtures/powercenter/provenance.json').read_text())
    for item in provenance['files']:
        assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']


def test_conversion_never_opens_database_or_executes_imported_sql(tmp_path, monkeypatch):
    import duckdb
    def forbidden(*args, **kwargs):
        raise AssertionError('Conversion opened a database')
    monkeypatch.setattr(duckdb, 'connect', forbidden)
    _, _, artifacts, outcomes, manifest = convert_to(tmp_path / 'output')
    assert len(artifacts) == 5
    assert manifest['unconverted_workflow_commands']
    assert all(intent.operation == 'clear' for a in artifacts.values() for intent in a.plan.preparations)
    for path in (tmp_path / 'output').rglob('*.sql'):
        assert 'TRUNCATE TABLE' not in path.read_text()


def test_installed_cli_help():
    import subprocess
    import sys
    result = subprocess.run([str(Path(sys.executable).parent / 'pwc-to-dbt'), '--help'], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0
    assert '--bindings' in result.stdout and '--target' in result.stdout and '--inventory' in result.stdout


@pytest.mark.negative
def test_session_required_preparation_override_is_not_ignored(tmp_path, request):
    def change(root):
        extension = root.find(".//SESSION[@MAPPINGNAME='m_FL_JS_STAGING_FULL']/SESSIONEXTENSION[@SINSTANCENAME='STG_CUSTOMERS']")
        ET.SubElement(extension, 'ATTRIBUTE', NAME='Pre SQL', VALUE='DELETE FROM other_table')
    xml = mutated(tmp_path, request, change)
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'out', xml=xml, selected=[STAGING + 'STG_CUSTOMERS'])
    assert not artifacts
    outcome = next(iter(outcomes.values()))
    assert outcome.status == 'unsupported'
    assert 'session override' in outcome.reason


@pytest.mark.negative
def test_unknown_storage_semantics_are_rejected(tmp_path, request):
    def change(root):
        root.find(".//SOURCE[@NAME='RAW_CUSTOMERS']").set('DATABASETYPE', 'DifferentVendor')
    xml = mutated(tmp_path, request, change)
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'out', xml=xml, selected=[STAGING + 'STG_CUSTOMERS'])
    assert not artifacts
    assert 'Storage semantics' in next(iter(outcomes.values())).reason


@pytest.mark.negative
def test_cross_mapping_binding_cycle_is_rejected(tmp_path):
    configuration = config()
    configuration['bindings'][STAGING + 'RAW_CUSTOMERS'] = STAGING + 'STG_CUSTOMERS'
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'out', selected=[STAGING + 'STG_CUSTOMERS'], configuration=configuration)
    assert not artifacts
    assert 'cycle' in next(iter(outcomes.values())).reason


@pytest.mark.negative
@pytest.mark.parametrize('mode,value', [('Insert', 'NO'), ('Treat source rows as', 'Delete'), ('Incremental Aggregation', 'YES')])
def test_incompatible_session_modes_preserve_independent_outputs(tmp_path, request, mode, value):
    def change(root):
        if mode == 'Insert':
            setting = root.find(".//SESSION[@MAPPINGNAME='m_FL_JS_STAGING_FULL']/SESSIONEXTENSION[@SINSTANCENAME='STG_CUSTOMERS']/ATTRIBUTE[@NAME='Insert']")
        else:
            setting = root.find(f".//SESSION[@MAPPINGNAME='m_FL_JS_MARTS_CORE']/ATTRIBUTE[@NAME='{mode}']")
        setting.set('VALUE', value)
    xml = mutated(tmp_path, request, change)
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'out', xml=xml)
    values = outcome_by_name(outcomes)
    failed = 'STG_CUSTOMERS' if mode == 'Insert' else 'CUSTOMERS'
    assert values[failed].status == 'unsupported'
    assert mode in values[failed].reason
    assert 'STG_PRODUCTS' in {key.instance for key in artifacts}
    if mode == 'Insert':
        assert values['CUSTOMERS'].status == 'blocked'


@pytest.mark.negative
@pytest.mark.parametrize('definition', ['source', 'transformation', 'target'])
def test_malformed_metadata_keeps_independent_selected_paths(tmp_path, request, definition):
    def change(root):
        paths = {'source': ".//SOURCE[@NAME='RAW_ORDERS']/SOURCEFIELD[@NAME='SUBTOTAL']",
                 'target': ".//TARGET[@NAME='STG_ORDERS']/TARGETFIELD[@NAME='SUBTOTAL']",
                 'transformation': ".//MAPPING[@NAME='m_FL_JS_STAGING_FULL']/TRANSFORMATION[@NAME='EXP_ORDERS']/TRANSFORMFIELD[@NAME='SUBTOTAL']"}
        root.find(paths[definition]).set('PRECISION', 'invalid')
    xml = mutated(tmp_path, request, change)
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'out', xml=xml)
    values = outcome_by_name(outcomes)
    assert values['STG_ORDERS'].status == 'error'
    assert 'PRECISION' in values['STG_ORDERS'].reason
    assert 'malformed metadata' in values['STG_ORDERS'].reason
    assert values['CUSTOMERS'].status == 'blocked'
    assert {key.instance for key in artifacts} == {'STG_CUSTOMERS', 'STG_PRODUCTS', 'STG_SUPPLIES'}
    # The same malformed definition must not abort a separately selected path.
    _, _, independent, _, _ = convert_to(tmp_path / 'independent', xml=xml, selected=[STAGING + 'STG_CUSTOMERS'])
    assert len(independent) == 1


@pytest.mark.negative
@pytest.mark.parametrize('kind', ['SOURCE', 'TARGET'])
@pytest.mark.parametrize('bad_ordinal', [None, '0', '-1', 'bad', '2'])
def test_source_target_ordinals_are_positive_and_unique(tmp_path, request, kind, bad_ordinal):
    def change(root):
        name = 'RAW_CUSTOMERS' if kind == 'SOURCE' else 'STG_CUSTOMERS'
        field = root.find(f".//{kind}[@NAME='{name}']/{kind}FIELD")
        if bad_ordinal is None:
            field.attrib.pop('FIELDNUMBER')
        else:
            field.set('FIELDNUMBER', bad_ordinal)
    xml = mutated(tmp_path, request, change)
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'out', xml=xml, selected=[STAGING + 'STG_CUSTOMERS', STAGING + 'STG_PRODUCTS'])
    values = outcome_by_name(outcomes)
    assert values['STG_CUSTOMERS'].status == 'error'
    assert 'FIELDNUMBER' in values['STG_CUSTOMERS'].reason
    assert {key.instance for key in artifacts} == {'STG_PRODUCTS'}


@pytest.mark.negative
def test_output_only_qualifier_port_is_contextually_unsupported(tmp_path, request):
    def change(root):
        qualifier = staging(root).find("TRANSFORMATION[@NAME='SQ_RAW_CUSTOMERS']")
        ET.SubElement(qualifier, 'TRANSFORMFIELD', NAME='UNCONNECTED', PORTTYPE='OUTPUT', DATATYPE='string', PRECISION='10', SCALE='0')
    xml = mutated(tmp_path, request, change)
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'out', xml=xml, selected=[STAGING + 'STG_CUSTOMERS', STAGING + 'STG_PRODUCTS'])
    outcome = outcome_by_name(outcomes)['STG_CUSTOMERS']
    assert outcome.status == 'unsupported'
    assert 'SQ_RAW_CUSTOMERS' in outcome.reason and 'UNCONNECTED' in outcome.reason
    assert 'passthrough' in outcome.reason
    assert {key.instance for key in artifacts} == {'STG_PRODUCTS'}


@pytest.mark.negative
@pytest.mark.parametrize('configuration', [[], False, 0, ''])
def test_falsey_nonobject_configuration_is_rejected(configuration):
    with pytest.raises(ConversionError, match='Configuration accepts'):
        plan(read_xml(XML), [STAGING + 'STG_CUSTOMERS'], configuration)


@pytest.mark.negative
@pytest.mark.parametrize('expression', ['ORDER_TOTAL', 'SUM(ORDER_TOTAL) + TAX_PAID', 'SUM(SUM(ORDER_TOTAL))'])
def test_aggregator_rejects_ungrouped_and_nested_aggregate_shapes(tmp_path, request, expression):
    def change(root):
        root.find(".//MAPPING[@NAME='m_FL_JS_MARTS_CORE']/TRANSFORMATION[@NAME='AGG_ORDERS_BY_CUSTOMER']/TRANSFORMFIELD[@NAME='LIFETIME_SPEND']").set('EXPRESSION', expression)
    xml = mutated(tmp_path, request, change)
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'out', xml=xml, selected=[CORE + 'CUSTOMERS'])
    outcome = outcome_by_name(outcomes)['CUSTOMERS']
    assert outcome.status == 'unsupported'
    assert 'AGG_ORDERS_BY_CUSTOMER' in outcome.reason
    assert 'Ungrouped' in outcome.reason or 'Nested aggregate' in outcome.reason
    assert {key.instance for key in artifacts} == {'STG_CUSTOMERS', 'STG_ORDERS'}


@pytest.mark.negative
def test_deep_expression_keeps_independent_outputs(tmp_path, request):
    def change(root):
        staging(root).find("TRANSFORMATION[@NAME='EXP_PRODUCTS']/TRANSFORMFIELD[@NAME='PRODUCT_NAME']").set('EXPRESSION', 'UPPER(' * 2000 + 'NAME' + ')' * 2000)
    xml = mutated(tmp_path, request, change)
    _, _, artifacts, outcomes, _ = convert_to(tmp_path / 'out', xml=xml, selected=[STAGING + 'STG_CUSTOMERS', STAGING + 'STG_PRODUCTS'])
    outcome = outcome_by_name(outcomes)['STG_PRODUCTS']
    assert outcome.status == 'unsupported'
    assert 'EXP_PRODUCTS' in outcome.reason and 'complexity' in outcome.reason
    assert {key.instance for key in artifacts} == {'STG_CUSTOMERS'}
