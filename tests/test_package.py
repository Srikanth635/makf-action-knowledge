"""Package installation APIs, source integrity, and CLI smoke tests."""
import json
from pathlib import Path
from makf_knowledge import describe_class, build_context, list_ontologies
from makf_knowledge.cli import run
from makf_knowledge.paths import resource_path, profile_path
from makf_knowledge.schema import compile_schema
import yaml

def test_packaged_ontologies_present():
    names={x['filename'] for x in list_ontologies()}
    assert {'aicor-ontology.ttl','cram-aicor-ontology.ttl','makf-core.ttl','pouring-frame.ttl','grasping-smoke.ttl','dul-alignment.ttl'} <= names

def test_direct_pouring_frame_restrictions():
    d=describe_class('paf:PouringKnowledgeFrame')
    assert any(x['predicate'].endswith('#hasActionCategory') and x['some_values_from'].endswith('#Pouring') for x in d['some_values_from'])

def test_guidance_reusable():
    assert build_context(profile_path('pouring'))['action_class']=='aicor:Pouring'
    assert build_context(profile_path('grasping'))['action_class']=='aicor:Grasping'

def test_generated_json_schema_matches_bundled():
    src=yaml.safe_load(resource_path('schema','makf_extraction.linkml.yaml').read_text())
    assert compile_schema(src)==json.loads(resource_path('schema','makf_extraction.schema.json').read_text())

def test_cli_doctor(capsys):
    assert run(['doctor'])==0
    assert json.loads(capsys.readouterr().out)['status']=='PASS'

def test_cli_validate(capsys):
    assert run(['validate','pouring','--profile','pouring'])==0
    assert json.loads(capsys.readouterr().out)['status']=='PASS'

def test_cli_reject_bad_profile(capsys):
    assert run(['validate','pouring','--profile','grasping'])==1
    assert 'ERROR:' in capsys.readouterr().err

def test_offline_catalog_points_to_active_modules():
    from xml.etree import ElementTree
    cat=resource_path('config','catalog-v001.xml')
    ns='{urn:oasis:names:tc:entity:xmlns:xml:catalog}'
    nodes=ElementTree.parse(cat).getroot().findall(ns+'uri')
    assert len(nodes)==5
    assert all((cat.parent/n.attrib['uri']).is_file() for n in nodes)
    assert not any('DUL.owl' in n.attrib['name'] for n in nodes)

def test_inventory_preserved():
    assert resource_path('inventory','all_classes.csv').stat().st_size>150000
    assert resource_path('inventory','POURING_ONTOLOGY_INVENTORY.md').exists()
