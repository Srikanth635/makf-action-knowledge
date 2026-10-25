"""Lossless quantitative snapshots and rejection of RDF/eligibility corruption."""
from copy import deepcopy
from importlib.util import find_spec
import json

import pytest
from rdflib import Dataset,Graph,Literal,RDF,URIRef
from makf_knowledge.paths import resource_path
from makf_knowledge.publication import read_json
from makf_knowledge.quantitative_rdf import Q,export_quantitative,validate_quantitative_rdf
from makf_knowledge.validation import ValidationError

pytestmark=pytest.mark.skipif(find_spec('pyshacl') is None,reason='Optional rdf extra')

@pytest.fixture
def data():return read_json(resource_path('quantitative','fluidlab.json'))

def unpack(result):
    return Dataset().parse(data=dict(result.artifacts)['dataset.trig'],format='trig'),json.loads(result.manifest_json)


def test_export_is_lossless_repeatable_and_retains_issues(data):
    before=deepcopy(data);result=export_quantitative(data,base_iri='https://example.org/test/')
    ds,m=unpack(result);again,_=unpack(export_quantitative(data,base_iri='https://example.org/test/'))
    assert data==before and set(ds.quads())==set(again.quads())
    g=ds.graph(URIRef(m['graph_iri']));snapshot=URIRef(m['snapshot_iri'])
    assert json.loads(str(g.value(snapshot,Q.inputJSON)))==data
    assert len(list(g.subjects(RDF.type,Q.Quantity)))==10
    assert Literal('timing_conflict') in set(g.objects(None,Q.code))
    unknown=[s for s,p,o in g.triples((None,Q.status,Literal('unreported')))]
    assert len(unknown)==6 and all(g.value(s,Q.symbol) is None for s in unknown)
    assert set(g.objects(None,Q.execution_eligible))=={Literal(False)}
    assert Literal('2e-3') in set(g.objects(None,Q.reported_value_text))
    assert not list(g.triples((None,RDF.type,URIRef('http://aicor.knowledge/l2-ontology.owl#Pouring'))))
    assert validate_quantitative_rdf(ds,m)


@pytest.mark.parametrize('fault',['value','unit','execution','quote','issue','extra','default','json','manifest'])
def test_corrupted_rdf_cannot_bypass_source_validation(data,fault):
    ds,m=unpack(export_quantitative(data,base_iri='https://example.org/test/'))
    g=ds.graph(URIRef(m['graph_iri']));snapshot=URIRef(m['snapshot_iri'])
    q=g.value(predicate=Q.quantity_id,object=Literal('light-density_rho'))
    if fault=='value':g.set((q,Q.reported_value_text,Literal('800')))
    elif fault=='unit':g.add((g.value(q,Q.unit),Q.symbol,Literal('kg/m3')))
    elif fault=='execution':g.set((q,Q.execution_eligible,Literal(True)))
    elif fault=='quote':g.set((g.value(q,Q.evidence),Q.exact_quote,Literal('Invented quotation.')))
    elif fault=='issue':g.remove((snapshot,Q.issue,None))
    elif fault=='extra':ds.graph(URIRef('urn:extra')).add((q,RDF.type,Q.Quantity))
    elif fault=='default':ds.default_graph.add((q,RDF.type,Q.Quantity))
    elif fault=='json':g.set((snapshot,Q.inputJSON,Literal('{invalid')))
    elif fault=='manifest':m['input_sha256']='0'*64
    with pytest.raises(ValidationError):validate_quantitative_rdf(ds,m)


def test_derived_conversion_is_separate_from_reported_value(data):
    data['conversions']=[dict(conversion_id='step-ms',input_id='step',target_unit='ms',derived_value_text='2',method='unit_conversion_v1')]
    ds,m=unpack(export_quantitative(data,base_iri='https://example.org/test/'))
    g=ds.graph(URIRef(m['graph_iri']));conversion=g.value(predicate=RDF.type,object=Q.Conversion)
    assert g.value(conversion,Q.computed_value)==Literal('2')
    assert g.value(g.value(conversion,Q.input),Q.reported_value_text)==Literal('2e-3')


def test_invalid_input_creates_no_bundle_and_existing_bundle_is_preserved(data,tmp_path):
    result=export_quantitative(data,base_iri='https://example.org/test/');out=tmp_path/'bundle';result.save(out)
    before=(out/'dataset.trig').read_bytes()
    with pytest.raises(FileExistsError):result.save(out)
    assert (out/'dataset.trig').read_bytes()==before
    data['quantities'][0]['reported_value_text']='999'
    with pytest.raises(ValidationError):export_quantitative(data,base_iri='https://example.org/test/').save(tmp_path/'bad')
    assert not (tmp_path/'bad').exists()


def test_shapes_are_valid_and_enforce_no_execution(data):
    from pyshacl import validate
    shapes=Graph().parse(resource_path('quantitative','shapes.ttl'))
    assert validate(Graph(),shacl_graph=shapes,meta_shacl=True,do_owl_imports=False)[0]
    ds,m=unpack(export_quantitative(data,base_iri='https://example.org/test/'))
    g=ds.graph(URIRef(m['graph_iri']))
    g.set((URIRef(m['snapshot_iri']),Q.execution_eligible,Literal(True)))
    assert not validate(g,shacl_graph=shapes,do_owl_imports=False)[0]
