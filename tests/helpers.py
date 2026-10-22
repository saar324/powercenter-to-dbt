from pathlib import Path
import json

from pwc_to_dbt.dependencies import plan
from pwc_to_dbt.project import compile_models, write_project
from pwc_to_dbt.xml_reader import read_xml

ROOT = Path(__file__).resolve().parents[1]
XML = ROOT / 'fixtures/powercenter/FLOWLINE_DEMO_JAFFLESHOP.xml'
PREFIX = 'REPO_Jaffleshop/FLOWLINE_DEMO_JAFFLESHOP/'
STAGING = PREFIX + 'm_FL_JS_STAGING_FULL/'
CORE = PREFIX + 'm_FL_JS_MARTS_CORE/'
REQUIRED = [STAGING + name for name in ['STG_CUSTOMERS', 'STG_ORDERS', 'STG_PRODUCTS', 'STG_SUPPLIES']] + [CORE + 'CUSTOMERS']


def config():
    return json.loads((ROOT / 'examples/sample-bindings.json').read_text())


def convert_to(path, *, xml=XML, selected=REQUIRED, configuration=None):
    export = read_xml(xml)
    planning = plan(export, selected, config() if configuration is None else configuration)
    artifacts, outcomes = compile_models(planning)
    manifest = write_project(path, export, planning, artifacts, outcomes)
    return export, planning, artifacts, outcomes, manifest


def mutated(tmp_path, request, change):
    import hashlib
    import xml.etree.ElementTree as ET
    root = ET.parse(XML).getroot()
    change(root)
    destination = tmp_path / (request.node.name + '.xml')
    ET.ElementTree(root).write(destination, encoding='utf-8', xml_declaration=True)
    request.node.actual_input_id = destination.name + ':sha256:' + hashlib.sha256(destination.read_bytes()).hexdigest()
    return destination


def run_dbt(project, database, evidence_name):
    import os
    import subprocess
    import sys
    from .conftest import RUN
    env = os.environ | {'PWC_DUCKDB_PATH': str(database), 'DO_NOT_TRACK': '1', 'DBT_SEND_ANONYMOUS_USAGE_STATS': 'false'}
    result = subprocess.run([str(Path(sys.executable).parent / 'dbt'), 'run', '--project-dir', str(project), '--profiles-dir', str(project), '--no-use-colors'],
                            capture_output=True, text=True, env=env, timeout=120)
    path = ROOT / 'reports/evidence' / f'{RUN}-{evidence_name}.txt'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stdout + result.stderr
    return result
