from unittest.mock import patch

import pytest
import rdflib
import requests
from rdflib.namespace import RDF

from nanopub import Nanopub

DEFAULT_FORMAT = '.trig'
BAD_GATEWAY = 502
NANOPUB_SERVER = 'http://purl.org/np/'
SERVER_UNAVAILABLE = 'Nanopub server is unavailable'


def nanopub_server_unavailable():
    response = requests.get(NANOPUB_SERVER)

    return response.status_code == BAD_GATEWAY


@pytest.mark.flaky(max_runs=10)
@pytest.mark.skipif(nanopub_server_unavailable(), reason=SERVER_UNAVAILABLE)
def test_nanopub_search_text():
    """
        Check that Nanopub text search is returning results for a few common search terms
    """

    searches = ['fair', 'heart']

    for search in searches:
        results = Nanopub.search_text(search)
        assert len(results) > 0

    assert len(Nanopub.search_text('')) == 0

@pytest.mark.flaky(max_runs=10)
@pytest.mark.skipif(nanopub_server_unavailable(), reason=SERVER_UNAVAILABLE)
def test_nanopub_search_pattern():
    """
        Check that Nanopub pattern search is returning results
    """

    searches = [
        ('', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'https://www.omg.org/spec/BPMN/scriptTask'),
        ('http://purl.org/np/RANhYfdZCVDQr8ItxDYCZWhvBhzjJTs9Cq-vPnmSBDd5g', '', '')
    ]

    for subj, pred, obj in searches:
        results = Nanopub.search_pattern(subj=subj, pred=pred, obj=obj)
        assert len(results) > 0

@pytest.mark.flaky(max_runs=10)
@pytest.mark.skipif(nanopub_server_unavailable(), reason=SERVER_UNAVAILABLE)
def test_nanopub_search_things():
    """
        Check that Nanopub 'things' search is returning results
    """

    searches = [
        'http://dkm.fbk.eu/index.php/BPMN2_Ontology#ManualTask',
        'http://purl.org/net/p-plan#Plan'
    ]

    for thing_type in searches:
        results = Nanopub.search_things(thing_type=thing_type)
        assert len(results) > 0

    with pytest.raises(Exception):
        Nanopub.search_things()


def test_nanopub_search():

    with pytest.raises(Exception):
        Nanopub._search(searchparams=None, max_num_results=100, apiurl='http://www.api.url')
    with pytest.raises(Exception):
        Nanopub._search(searchparams={'search': 'text'}, max_num_results=None, apiurl='http://www.api.url')
    with pytest.raises(Exception):
        Nanopub._search(searchparams={'search': 'text'}, max_num_results=100, apiurl=None)


@pytest.mark.flaky(max_runs=10)
@pytest.mark.skipif(nanopub_server_unavailable(), reason=SERVER_UNAVAILABLE)
def test_nanopub_fetch():
    """
        Check that Nanopub fetch is returning results for a few known nanopub URIs.
        Check that the returned object is of type NNanopubObj, that it has the expected
        source_uri, and that it has non-zero data.
    """

    known_nps = [
        'http://purl.org/np/RAFNR1VMQC0AUhjcX2yf94aXmG1uIhteGXpq12Of88l78',
        'http://purl.org/np/RAePO1Fi2Wp1ARk2XfOnTTwtTkAX1FBU3XuCwq7ng0jIo',
        'http://purl.org/np/RA48Iprh_kQvb602TR0ammkR6LQsYHZ8pyZqZTPQIl17s'
    ]

    for np_uri in known_nps:
        np = Nanopub.fetch(np_uri)
        assert isinstance(np, Nanopub.NanopubObj)
        assert np.source_uri == np_uri
        assert len(np.rdf) > 0
        assert np.assertion is not None
        assert np.pubinfo is not None
        assert np.provenance is not None
        assert len(np.__str__()) > 0

def test_nanopub_rdf():
    """
    Test that Nanopub.to_rdf() is creating an rdf graph with the right features (contexts)
    for a nanopub.
    """

    assertionrdf = rdflib.Graph()
    assertionrdf.add((Nanopub.AUTHOR.DrBob, Nanopub.HYCL.claims, rdflib.Literal('This is a test')))

    generated_rdf = Nanopub.to_rdf(assertionrdf)

    assert generated_rdf is not None
    assert (None, RDF.type, Nanopub.NP.Nanopublication) in generated_rdf
    assert (None, Nanopub.NP.hasAssertion, None) in generated_rdf
    assert (None, Nanopub.NP.hasProvenance, None) in generated_rdf
    assert (None, Nanopub.NP.hasPublicationInfo, None) in generated_rdf

    new_concept = rdflib.term.URIRef('www.purl.org/new/concept/test')
    generated_rdf = Nanopub.to_rdf(assertionrdf, introduces_concept=new_concept)

    assert generated_rdf is not None
    assert (None, RDF.type, Nanopub.NP.Nanopublication) in generated_rdf
    assert (None, Nanopub.NP.hasAssertion, None) in generated_rdf
    assert (None, Nanopub.NP.hasProvenance, None) in generated_rdf
    assert (None, Nanopub.NP.hasPublicationInfo, None) in generated_rdf

    assert (None, Nanopub.NPX.introduces, new_concept) in generated_rdf


@patch('nanopub.java_wrapper.publish')
def test_nanopub_claim(java_wrapper_publish_mock):
    optional_triple = (rdflib.term.URIRef('http://www.uri1.com'), rdflib.term.URIRef('http://www.uri2.com'), rdflib.Literal('Something'))
    Nanopub.claim('Some controversial statement', rdftriple=optional_triple)

@patch('nanopub.java_wrapper.publish')
def test_nanopub_publish(java_wrapper_publish_mock):

    assertionrdf = rdflib.Graph()
    assertionrdf.add((Nanopub.AUTHOR.DrBob, Nanopub.HYCL.claims, rdflib.Literal('This is a test')))

    Nanopub.publish(assertionrdf, uri=rdflib.term.URIRef('http://www.example.com/auri'), introduces_concept=Nanopub.AUTHOR.DrBob, derived_from=rdflib.term.URIRef('http://www.example.com/someuri'))
