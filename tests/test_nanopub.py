from unittest import mock
from unittest.mock import patch

import pytest
import rdflib
import requests
from rdflib.namespace import RDF

from nanopub import NanopubClient, namespaces
from nanopub.nanopub import Nanopub

DEFAULT_FORMAT = '.trig'
BAD_GATEWAY = 502
NANOPUB_SERVER = 'http://purl.org/np/'
SERVER_UNAVAILABLE = 'Nanopub server is unavailable'


def test_nanopub_construction_with_bnode_introduced_concept():
    """
    Test Nanopub construction from assertion where a BNode is introduced as a concept.
    """
    test_uri = 'http://www.example.com/my-nanopub'
    test_concept_uri = 'http://www.example.com/my-nanopub#DrBob'  # This nanopub introduced DrBob
    assertion_rdf = rdflib.Graph()
    assertion_rdf.add((rdflib.term.BNode('DrBob'),
                       namespaces.HYCL.claims,
                       rdflib.Literal('This is a test')))

    nanopub = Nanopub.from_assertion(
        assertion_rdf=assertion_rdf,
        uri=rdflib.term.URIRef(test_uri),
        introduces_concept=rdflib.term.BNode('DrBob'),
        derived_from=rdflib.term.URIRef('http://www.example.com/another-nanopub')
        )
    assert str(nanopub.introduces_concept) == test_concept_uri


def nanopub_server_unavailable():
    response = requests.get(NANOPUB_SERVER)

    return response.status_code == BAD_GATEWAY


@pytest.mark.flaky(max_runs=10)
@pytest.mark.skipif(nanopub_server_unavailable(), reason=SERVER_UNAVAILABLE)
def test_nanopub_search_text():
    """
        Check that Nanopub text search is returning results for a few common search terms
    """
    client = NanopubClient()
    searches = ['fair', 'heart']

    for search in searches:
        results = client.search_text(search)
        assert len(results) > 0

    assert len(client.search_text('')) == 0

@pytest.mark.flaky(max_runs=10)
@pytest.mark.skipif(nanopub_server_unavailable(), reason=SERVER_UNAVAILABLE)
def test_nanopub_search_pattern():
    """
        Check that Nanopub pattern search is returning results
    """
    client = NanopubClient()

    searches = [
        ('', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'https://www.omg.org/spec/BPMN/scriptTask'),
        ('http://purl.org/np/RANhYfdZCVDQr8ItxDYCZWhvBhzjJTs9Cq-vPnmSBDd5g', '', '')
    ]

    for subj, pred, obj in searches:
        results = client.search_pattern(subj=subj, pred=pred, obj=obj)
        assert len(results) > 0

@pytest.mark.flaky(max_runs=10)
@pytest.mark.skipif(nanopub_server_unavailable(), reason=SERVER_UNAVAILABLE)
def test_nanopub_search_things():
    """
        Check that Nanopub 'things' search is returning results
    """
    client = NanopubClient()
    searches = [
        'http://dkm.fbk.eu/index.php/BPMN2_Ontology#ManualTask',
        'http://purl.org/net/p-plan#Plan'
    ]

    for thing_type in searches:
        results = client.search_things(thing_type=thing_type)
        assert len(results) > 0

    with pytest.raises(Exception):
        client.search_things()


def test_nanopub_search():
    client = NanopubClient()
    with pytest.raises(Exception):
        client._search(searchparams=None,
                       max_num_results=100,
                       apiurl='http://www.api.url')
    with pytest.raises(Exception):
        client._search(searchparams={'search': 'text'},
                       max_num_results=None,
                    apiurl='http://www.api.url')
    with pytest.raises(Exception):
        client._search(searchparams={'search': 'text'},
                       max_num_results=100,
                       apiurl=None)


@pytest.mark.flaky(max_runs=10)
@pytest.mark.skipif(nanopub_server_unavailable(), reason=SERVER_UNAVAILABLE)
def test_nanopub_fetch():
    """
        Check that Nanopub fetch is returning results for a few known nanopub URIs.
        Check that the returned object is of type NNanopubObj, that it has the expected
        source_uri, and that it has non-zero data.
    """
    client = NanopubClient()

    known_nps = [
        'http://purl.org/np/RAFNR1VMQC0AUhjcX2yf94aXmG1uIhteGXpq12Of88l78',
        'http://purl.org/np/RAePO1Fi2Wp1ARk2XfOnTTwtTkAX1FBU3XuCwq7ng0jIo',
        'http://purl.org/np/RA48Iprh_kQvb602TR0ammkR6LQsYHZ8pyZqZTPQIl17s'
    ]

    for np_uri in known_nps:
        np = client.fetch(np_uri, format='trig')
        assert isinstance(np, Nanopub)
        assert np.source_uri == np_uri
        assert len(np.rdf) > 0
        assert np.assertion is not None
        assert np.pubinfo is not None
        assert np.provenance is not None
        assert len(np.__str__()) > 0


def test_nanopub_from_assertion():
    """
    Test that Nanopub.from_assertion is creating an rdf graph with the right features (contexts)
    for a nanopub.
    """
    assertion_rdf = rdflib.Graph()
    assertion_rdf.add((namespaces.AUTHOR.DrBob, namespaces.HYCL.claims,
                       rdflib.Literal('This is a test')))

    nanopub = Nanopub.from_assertion(assertion_rdf)

    assert nanopub.rdf is not None
    assert (None, RDF.type, namespaces.NP.Nanopublication) in nanopub.rdf
    assert (None, namespaces.NP.hasAssertion, None) in nanopub.rdf
    assert (None, namespaces.NP.hasProvenance, None) in nanopub.rdf
    assert (None, namespaces.NP.hasPublicationInfo, None) in nanopub.rdf

    new_concept = rdflib.term.URIRef('www.purl.org/new/concept/test')
    nanopub = Nanopub.from_assertion(assertion_rdf, introduces_concept=new_concept)

    assert nanopub.rdf is not None
    assert (None, RDF.type, namespaces.NP.Nanopublication) in nanopub.rdf
    assert (None, namespaces.NP.hasAssertion, None) in nanopub.rdf
    assert (None, namespaces.NP.hasProvenance, None) in nanopub.rdf
    assert (None, namespaces.NP.hasPublicationInfo, None) in nanopub.rdf

    assert (None, namespaces.NPX.introduces, new_concept) in nanopub.rdf


def test_nanopub_claim():
    client = NanopubClient()
    client.java_wrapper.publish = mock.MagicMock()
    optional_triple = (rdflib.term.URIRef('http://www.uri1.com'),
                       rdflib.term.URIRef('http://www.uri2.com'),
                       rdflib.Literal('Something'))
    client.claim('Some controversial statement', rdftriple=optional_triple)


def test_nanopub_publish():
    test_uri = 'http://www.example.com/my-nanopub'
    test_concept_uri = 'http://purl.org/person#DrBob'  # This nanopub introduced DrBob
    client = NanopubClient()
    client.java_wrapper.publish = mock.MagicMock(return_value=test_uri)
    assertion_rdf = rdflib.Graph()
    assertion_rdf.add((namespaces.AUTHOR.DrBob, namespaces.HYCL.claims, rdflib.Literal('This is a test')))

    nanopub = Nanopub.from_assertion(
        assertion_rdf=assertion_rdf,
        uri=rdflib.term.URIRef(test_uri),
        introduces_concept=namespaces.AUTHOR.DrBob,
        derived_from=rdflib.term.URIRef('http://www.example.com/another-nanopub')
        )
    pubinfo = client.publish(nanopub)
    assert pubinfo['nanopub_uri'] == test_uri
    assert pubinfo['concept_uri'] == test_concept_uri
