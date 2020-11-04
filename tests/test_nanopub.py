from unittest import mock

import pytest
import rdflib
from rdflib.namespace import RDF

from conftest import skip_if_nanopub_server_unavailable
from nanopub import NanopubClient, namespaces, Nanopub

client = NanopubClient(use_test_server=True)

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


@pytest.mark.flaky(max_runs=10)
@skip_if_nanopub_server_unavailable
def test_find_nanopubs_with_text():
    """
    Check that Nanopub text search is returning results for a few common search terms
    """
    searches = ['test', 'US']

    for search in searches:
        results = client.find_nanopubs_with_text(search)
        assert len(results) > 0

    assert len(client.find_nanopubs_with_text('')) == 0


@pytest.mark.flaky(max_runs=10)
def test_find_nanopubs_with_text_prod():
    """
    Check that Nanopub text search is returning results for a few common search terms on the
    production nanopub server
    """
    prod_client = NanopubClient()
    searches = ['test', 'US']
    for search in searches:
        results = prod_client.find_nanopubs_with_text(search)
        assert len(results) > 0


@pytest.mark.flaky(max_runs=10)
@skip_if_nanopub_server_unavailable
def test_find_nanopubs_with_pattern():
    """
        Check that Nanopub pattern search is returning results
    """
    searches = [
        ('', 'http://example.org/transmits', 'http://example.org/malaria'),
        ('http://purl.org/np/RA8ui7ddvV25m1qdyxR4lC8q8-G0yb3SN8AC0Bu5q8Yeg', '', '')
    ]

    for subj, pred, obj in searches:
        results = client.find_nanopubs_with_pattern(subj=subj, pred=pred, obj=obj)
        assert len(results) > 0
        assert 'Error' not in results[0]


@pytest.mark.flaky(max_runs=10)
@skip_if_nanopub_server_unavailable
def test_nanopub_find_things():
    """
    Check that Nanopub 'find_things' search is returning results
    """
    results = client.find_things(type='http://purl.org/net/p-plan#Plan')
    assert len(results) > 0

    with pytest.raises(Exception):
        client.find_things()


def test_nanopub_search():
    with pytest.raises(Exception):
        client._search(params=None,
                       max_num_results=100,
                       endpoint='http://www.api.url')
    with pytest.raises(Exception):
        client._search(params={'search': 'text'},
                       max_num_results=None,
                       endpoint='http://www.api.url')
    with pytest.raises(Exception):
        client._search(params={'search': 'text'},
                       max_num_results=100,
                       endpoint=None)


@pytest.mark.flaky(max_runs=10)
@skip_if_nanopub_server_unavailable
def test_nanopub_fetch():
    """
    Check that Nanopub fetch is returning results for a few known nanopub URIs.
    """
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


def test_nanopub_publish_blanknode():
    test_concept = rdflib.term.BNode('test')
    test_published_uri = 'http://www.example.com/my-nanopub'
    expected_concept_uri = 'http://www.example.com/my-nanopub#test'
    client = NanopubClient()
    client.java_wrapper.publish = mock.MagicMock(return_value=test_published_uri)
    assertion_rdf = rdflib.Graph()
    assertion_rdf.add(
        (test_concept, namespaces.HYCL.claims, rdflib.Literal('This is a test')))

    nanopub = Nanopub.from_assertion(
        assertion_rdf=assertion_rdf,
        introduces_concept=test_concept,
    )
    pubinfo = client.publish(nanopub)
    assert pubinfo['nanopub_uri'] == test_published_uri
    assert pubinfo['concept_uri'] == expected_concept_uri

